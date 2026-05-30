# 03 — Gestion des images : sortie de Firebase → stockage local Django

## Problème actuel

Les images sont uploadées **directement depuis le navigateur vers Firebase Storage** via un script
JS, puis le **chemin** est stocké dans un champ texte du modèle, et résolu en URL via **Pyrebase4**
côté serveur à l'affichage. Défauts :

- Config Firebase **en clair** dans `base/static/base/js/firebase-upload.js` (clé API exposée).
- SDK Firebase JS **v7.8.1** (2020), Pyrebase4 **non maintenu**.
- Dépendance à un service externe (Firebase) alors que le **stockage local est déjà disponible**.
- Résolution d'URL coûteuse : `PhotoAbstract.photo_url` ré-initialise Pyrebase à **chaque accès**.
- Upload non validé (taille, type) côté client.

### Comment ça marche aujourd'hui (détail technique)

- **Widget** : `base/widgets.py` → `FirebaseUploadWidget(forms.TextInput)`, `template_name =
  'base/widgets/firebase-upload-widget.html'`, charge le SDK Firebase + `firebase-upload.js`,
  paramètre `folder`.
- **Template widget** : `<input type="text">` (stocke le chemin), `<input type="file">`, bouton
  `.uploadFirebaseImage[data-folder]`, `<progress>`, `<img class="display" data-url=...>`.
- **JS** (`firebase-upload.js`) : upload vers `media/{folder}/{année}/{mois}/{jour}/{fichier}`,
  récupère le `downloadURL`, met le **chemin** dans l'input texte et l'URL dans la preview. Au chargement,
  résout les `img.display[data-url]` en URL via le SDK.
- **Modèle** : `base/models.py` → `PhotoAbstract.photo = TextField(default='placeholder.jpg')` ;
  propriété `photo_url` : si `photo` commence par `http` → renvoyé tel quel, sinon résolu via Pyrebase.
- **Réglage** : `FIREBASE_CONFIG = get_secret_setting('FIREBASE_CONFIG')` (`config/settings/base.py`).
- **Modèles utilisateurs** (champ `photo` via `PhotoAbstract`, widget dans le `forms.py` de l'app) :
  - `avis.Avis` → `FirebaseUploadWidget(folder='avis')`
  - `super_moite_moite.Tache` → `folder='taches'`
  - `kendama.Kendama` → `folder='kendamas'`
  - `my_spot.SpotPhoto` → `folder='spots'`
  - Cas à part : `base.Profil.avatar` = `ImageField(upload_to='avatars/')` (déjà un ImageField !),
    affiché via le mécanisme Firebase dans le template profil.

## Solution retenue : `ImageField` Django + `django-storages` sur Google Cloud Storage (= bucket Firebase)

> **Décision actée par le propriétaire.** On garde l'hébergement **gratuit** du bucket Firebase
> existant, mais accédé proprement via le backend GCS standard de Django.

**Insight clé** : un bucket Firebase Storage **EST** un bucket Google Cloud Storage. Le bucket actuel
`eminent-airport-148108.appspot.com` est donc pilotable par le backend `GoogleCloudStorage` de
`django-storages`. On bascule sur un `ImageField` Django classique dont le **storage par défaut** est
GCS. Avantages :

- Hébergement **gratuit** conservé (Firebase/GCS Spark, ~5 Go).
- **Images existantes en place** (les chemins sont déjà `media/...`) → migration **quasi triviale**,
  pas de téléchargement/réupload massif.
- Upload **côté serveur** → on **redimensionne avec Pillow avant l'envoi** (bucket léger).
- **Le disque PythonAnywhere n'est plus touché** par les images (c'était la cause de la saturation).
- On **supprime Pyrebase4** (non maintenu), le **SDK Firebase JS**, le script `firebase-upload.js` et
  la **config exposée en clair** côté client.

### Cible

1. Ajouter `django-storages[google]` (tire `google-cloud-storage`). Configurer le backend GCS :
   - `STORAGES['default']` → `storages.backends.gcloud.GoogleCloudStorage`
   - `GS_BUCKET_NAME = 'eminent-airport-148108.appspot.com'`
   - `GS_CREDENTIALS` = compte de service GCS (JSON), chargé depuis `secrets.json` (**côté serveur,
     jamais exposé**). À générer dans la console Google Cloud (IAM → comptes de service → clé JSON,
     rôle Storage Object Admin sur le bucket).
   - URLs publiques : soit rendre les objets `media/` **public-read** (`GS_DEFAULT_ACL='publicRead'`
     ou accès uniforme + lecture publique) et `GS_QUERYSTRING_AUTH=False`, soit garder des **URLs
     signées** (défaut). Choisir « public-read » pour des URLs stables et simples.
2. Remplacer le champ `photo` (TextField + Firebase) par un `ImageField` (`upload_to='<folder>/'`),
   uploadé via un `<input type="file">` standard + `request.FILES`. Aligner `upload_to` sur le
   préfixe **`media/`** existant pour retomber sur les chemins actuels (ou configurer `GS_LOCATION`).
3. Supprimer `FirebaseUploadWidget`, `firebase-upload.js`, le template widget, l'usage de Pyrebase,
   et `FIREBASE_CONFIG`.
4. **Optimiser côté serveur avec Pillow** (déjà dépendance) : à la sauvegarde, ouvrir l'image,
   redimensionner si > largeur max (ex. 1280px), ré-encoder en **WebP** (qualité ~80), avant envoi à
   GCS. Centraliser dans `PhotoAbstract` pour factoriser sur les 4 modèles. **C'est ce traitement qui
   évite de re-saturer le quota** (côté GCS comme PythonAnywhere).
5. Conserver une propriété `photo_url` **rétrocompatible** : si la valeur stockée est une URL `http`
   complète (vieilles entrées) → la renvoyer ; sinon `self.photo.url` (résolu par le backend GCS).

### Contraintes / vérifications

- **Compte de service GCS** : nécessite une clé JSON dans `secrets.json` (hors VCS). Vérifier les
  permissions IAM sur le bucket. Ne **jamais** committer la clé.
- **Egress GCS** : le free tier a des limites de bande passante en sortie ; pour un site perso à
  faible trafic, c'est négligeable. Le redimensionnement réduit aussi l'egress.
- **CORS bucket** : si des accès directs navigateur subsistent, configurer le CORS du bucket. Avec
  upload serveur + affichage via `<img src>`, ce n'est pas requis.
- **Sauvegarde** : `db.sqlite3` (hors repo) doit être sauvegardé. Les images sont dans GCS.

## Migration des images existantes (quasi triviale)

Comme les fichiers **restent dans le même bucket** aux mêmes chemins `media/...`, il n'y a **pas de
recopie de binaires**. La migration consiste surtout à **normaliser la donnée** stockée en base :

1. Management command idempotente (ex. `normalize_photo_paths`) itérant sur `Avis`, `Tache`,
   `Kendama`, `SpotPhoto` (+ `Profil` si besoin).
2. Pour chaque `photo` : convertir l'ancienne valeur (chemin Firebase type `media/avis/2024/...`) en
   la valeur attendue par l'`ImageField` GCS (alignée sur `GS_LOCATION`/`upload_to`). Les URLs `http`
   complètes restent gérées par `photo_url` rétrocompatible.
3. Vérifier sur quelques objets que `obj.photo.url` pointe sur le bon fichier dans le bucket.

> **Recommandé** (pas seulement optionnel) : repasser les **anciennes** images en WebP/redimensionné
> via un script one-shot (télécharger depuis GCS → optimiser Pillow → réécrire dans GCS).
> Mesure Phase 0 : le bucket contient **325 fichiers pour ~827 Mo, soit ~2,5 Mo/image** = plein format
> non optimisé. Le gain d'espace attendu est très important. Backup disponible :
> `~/backups/bucket-refonte-2026-05-29/media/` (utile comme source/filet pour ce script).

> Ordre : déployer le nouveau code (qui lit **les deux** formats grâce à `photo_url`) → exécuter la
> normalisation en prod → vérifier → retirer Pyrebase/SDK Firebase/config exposée.

## Étapes d'implémentation

1. Ajouter et configurer `django-storages[google]` + credentials GCS (settings + `secrets.json`).
2. Migration de schéma : `TextField photo` → `ImageField photo` (de préférence nouveau champ +
   migration de données puis suppression de l'ancien, pour la rétrocompatibilité).
3. Adapter `PhotoAbstract` (champ `ImageField` sur storage GCS + `photo_url` rétrocompatible +
   optimisation Pillow à la sauvegarde).
4. Retirer `FirebaseUploadWidget` des `forms.py` des 4 apps → `ClearableFileInput` standard.
5. Adapter les templates d'affichage (`img.display[data-url]` + JS Firebase → `<img src="{{ obj.photo_url }}">`).
6. Écrire/tester la management command de normalisation sur une copie de la DB de prod.
7. Déployer, normaliser en prod, vérifier.
8. Supprimer : `firebase-upload.js`, le template widget, la partie Firebase de `widgets.py`,
   `Pyrebase4` des requirements, `FIREBASE_CONFIG` des settings et de `secrets.json`, le SDK Firebase
   des `Media.js`.

## Critères de validation

- [ ] Upload d'une nouvelle image via formulaire (avis, tâche, kendama) → fichier dans le bucket GCS,
      optimisé (WebP, redimensionné), `obj.photo.url` correct.
- [ ] Affichage correct des anciennes images après normalisation.
- [ ] Plus aucune référence à Pyrebase/SDK Firebase JS/`FIREBASE_CONFIG` dans le code et `secrets.json`.
- [ ] Clé API Firebase retirée du code client ; credentials GCS uniquement côté serveur.
- [ ] `makemigrations --check` propre, migration de données rejouable.
</content>
