import re
from urllib.parse import urlparse, parse_qs

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.views import redirect_to_login
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import DetailView
from django.views.generic.edit import FormMixin
from django.views.generic.list import MultipleObjectMixin
from django_filters.views import FilterView
from googleapiclient import discovery
from slugify import slugify

from music.filters import MusiqueFilter, StyleFilter, LabelFilter, ArtisteFilter, PlaylistFilter
from music.models import Playlist, Musique, Lien, Artiste, Style, Label, Plateforme
from music.forms import LienForm, LienPlaylistForm, MusiqueForm


class MusiqueListView(FilterView):
    filterset_class = MusiqueFilter
    paginate_by = 50
    queryset = Musique.objects.select_related('artiste', 'remixed_by')\
        .prefetch_related('featuring', 'liens__plateforme', 'styles')


class StyleListView(FilterView):
    filterset_class = StyleFilter
    paginate_by = 20
    queryset = Style.objects.prefetch_related('musiques')


class StyleDetailView(DetailView, MultipleObjectMixin):
    model = Style
    paginate_by = 20
    slug_field = 'slug'

    def get_context_data(self, **kwargs):
        object_list = self.get_object().musiques.all()
        context = super().get_context_data(object_list=object_list, **kwargs)
        return context

    def get_queryset(self):
        return Style.objects.prefetch_related(
            'musiques__artiste', 'musiques__liens', 'musiques__styles', 'musiques__remixed_by', 'musiques__featuring'
        )


class LabelListView(FilterView):
    filterset_class = LabelFilter
    paginate_by = 20
    queryset = Label.objects.prefetch_related('musiques')


class LabelDetailView(DetailView):
    model = Label
    slug_field = 'slug'

    def get_queryset(self):
        return Label.objects.prefetch_related(
            'artistes', 'styles', 'musiques__artiste', 'musiques__liens',
            'musiques__styles', 'musiques__remixed_by', 'musiques__featuring'
        )


class PlaylistListView(FilterView):
    filterset_class = PlaylistFilter
    queryset = Playlist.objects\
        .select_related('createur__user')\
        .prefetch_related('musiqueplaylist_set')\
        .annotate(total_vue=Sum('musiqueplaylist__musique__liens__click_count'))


class PlaylistDetailView(FormMixin, DetailView):
    model = Playlist
    slug_field = 'slug'
    form_class = LienPlaylistForm

    def get_queryset(self):
        return Playlist.objects.select_related('createur__user')

    def get_context_data(self, **kwargs):
        # Prépare les musiques de la playslists afin de les avoir dans le bon ordre
        musiques = self.get_object().musiques\
            .select_related('artiste', 'remixed_by')\
            .prefetch_related('styles', 'featuring', 'liens__plateforme')\
            .order_by('musiqueplaylist__position')
        context = super().get_context_data(
            musiques=musiques,
            plateformes=Plateforme.objects.all(),
            **kwargs
        )
        return context

    def post(self, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if self.request.user.profil == self.object.createur and form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        lien = form.save(commit=False)
        lien.playlist = self.object
        lien.save()
        messages.success(self.request, 'Le lien a bien été ajouté.')
        return redirect(self.object.get_absolute_url())


def create_music_from_url(request):
    form = MusiqueForm(request.POST or None)
    link_form = LienForm(request.POST or None)
    if form.is_valid() and link_form.is_valid():
        musique = form.save(commit=False)
        musique.createur = request.user.profil
        musique.slug = slugify(musique.titre)
        musique.save()
        form.save_m2m()
        link = link_form.save(commit=False)
        link.musique = musique
        link.createur = request.user.profil
        link.date_validation = timezone.now()
        link.save()
        messages.success(request, 'La musique a bien été créée et ajoutée à la playlist.')
        return redirect(musique)

    return render(request, 'music/create_musique_from_url.html', {
        'form': form,
        'link_form': link_form,
        'plateformes': Plateforme.objects.all()
    })


@user_passes_test(lambda u: u.is_superuser)
def get_music_info_from_link(request):
    plateforme_id = request.POST.get('plateforme')
    if not plateforme_id:
        return JsonResponse({'success': False, 'error': 'plateforme_id manquant'})
    plateforme = get_object_or_404(Plateforme, id=plateforme_id)

    url = request.POST.get('url')
    if not url:
        return JsonResponse({'success': False, 'error': 'url manquante'})

    full_title = title = artist = remixed_by = ''
    featuring = []
    if plateforme.nom == 'Youtube':
        o = urlparse(url)
        query = parse_qs(o.query)
        if 'v' in query:
            video_id = query['v']

            youtube = discovery.build(
                'youtube', 'v3', developerKey=settings.GOOGLE_API_KEY
            )

            request = youtube.videos().list(
                part="snippet",
                id=video_id
            )
            response = request.execute()
            if response['items']:
                full_title = response['items'][0]['snippet'].get('title')
                if '-' in full_title:
                    artist, title = map(str.strip, full_title.split('-', 2))
                else:
                    title = full_title
                    artist = full_title = response['items'][0]['snippet'].get('channelTitle')
    elif plateforme.nom == 'Soundcloud':
        try:
            result = settings.SOUNDCLOUD_CLIENT.get(f'/resolve/', url=url)
        except Exception as e:
            return JsonResponse({'success': False, 'error': f"Erreur lors de l'appel API vers Soundcloud : {e}"})
        full_title = result.fields().get('title')
        if '-' in full_title:
            artist, title = map(str.strip, full_title.split('-', 1))
        else:
            title = full_title
            artist = result.fields().get('user').get('username')
    elif plateforme.nom == 'Spotify':
        try:
            track = settings.SPOTIFY.track(url)
        except Exception as e:
            return JsonResponse({'success': False, 'error': f"Erreur lors de l'appel API vers Spotify : {e}"})
        title = track.get('name')
        artists = track.get('artists')
        if artists:
            artist = artists[0].get('name')
            # Add to featuring other artists
            if len(artists) > 1:
                for a in artists[1:]:
                    try:
                        artist_obj = Artiste.objects.get(nom_artiste__iexact=a.get('name'))
                        featuring.append({'name': artist_obj.nom_artiste, 'id': artist_obj.id})
                    except Artiste.DoesNotExist:
                        pass
    else:
        return JsonResponse({
            'success': False,
            'error': f"Le traitement de la plateforme {plateforme} n'a pas été fait..."
        })

    if not title and not artist:
        return JsonResponse({'success': False, 'error': "Impossible de retrouver des infos via l'url."})

    # Extract a possible artist who remixed the track with a regex
    remixed = re.findall(r'\((.*) Re?mi?x\)', title, flags=re.IGNORECASE)
    if remixed:
        try:
            artist_obj = Artiste.objects.get(nom_artiste__iexact=remixed[0])
            remixed_by = {'name': artist_obj.nom_artiste, 'id': artist_obj.id}
        except Artiste.DoesNotExist:
            remixed_by = remixed[0]

    try:
        artist_obj = Artiste.objects.get(nom_artiste__iexact=artist)
        artist = {'name': artist_obj.nom_artiste, 'id': artist_obj.id}
    except Artiste.DoesNotExist:
        pass

    return JsonResponse({
        'success': True,
        'full_title': full_title,
        'title': title,
        'artist': artist,
        'remixed_by': remixed_by,
        'featuring': featuring
    })


class MusiqueDetailView(FormMixin, DetailView):
    model = Musique
    slug_field = 'slug'
    query_pk_and_slug = True
    form_class = LienForm

    def get_context_data(self, **kwargs):
        context = super(MusiqueDetailView, self).get_context_data(**kwargs)
        context['form'] = self.get_form()
        context['plateformes'] = Plateforme.objects.all()
        return context

    def post(self, *args, **kwargs):
        self.object = self.get_object()
        if not self.request.user.is_authenticated:
            messages.error(self.request, 'Vous devez être connecté pour proposer un lien.')
            return redirect_to_login(self.object.get_absolute_url())
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        lien = form.save(commit=False)
        lien.musique = self.object
        if self.request.user.profil:
            lien.createur = self.request.user.profil
            # Son lien est automatiquement validé si c'est la musique qu'il a créé
            if self.request.user == self.object.createur.user:
                lien.date_validation = timezone.now()
            elif self.object.createur.user.email:
                # Avertissement par mail qu'un lien a été proposé
                current_site = Site.objects.get_current()
                send_mail(
                    'Nouveau lien proposé sur la musique %s' % self.object,
                    'Le lien "%s" a été proposé pour la musique %s que tu as ajouté. Tu peux valider le lien ici : %s%s'
                    % (lien.url, self.object, current_site.domain, self.object.get_absolute_url()),
                    'noreply@benbb96.com',
                    [self.object.createur.user.email]
                )
        lien.save()
        messages.success(self.request, 'Le lien a bien été ajouté.')
        return redirect(self.object.get_absolute_url())


class ArtisteListView(FilterView):
    filterset_class = ArtisteFilter
    paginate_by = 50
    queryset = Artiste.objects.prefetch_related('musiques', 'musiques_featuring', 'remixes')


class ArtisteDetailView(DetailView):
    model = Artiste
    slug_field = 'slug'


@require_POST
def incremente_link_click_count(request, lien_id):
    lien = get_object_or_404(Lien, id=lien_id)
    lien.click_count += 1
    lien.save(update_fields=['click_count'])
    return JsonResponse({
        'success': True,
        'click_count': lien.click_count,
        'music_id': lien.musique.id,
        'music_count': lien.musique.nombre_vue()
    })


def valider_lien(request, lien_id):
    lien = get_object_or_404(Lien, id=lien_id)
    if request.user != lien.musique.createur.user or not request.user.is_superuser:
        messages.error(request, "Cette musique ne t'appartient pas.")
    else:
        lien.date_validation = timezone.now()
        lien.save(update_fields=['date_validation'])
    return redirect(lien.musique.get_absolute_url())
