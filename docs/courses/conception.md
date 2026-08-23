# Liste de courses partagée & intelligente — conception

> Document de cadrage. Statut : **discussion en cours**, rien n'est implémenté.
> Date : 2026-08-22.

## 1. Le besoin

Une liste de courses partagée entre les membres d'un foyer, utilisable **dans le magasin**
(donc potentiellement sans réseau), qui sait d'elle-même ce qui va manquer.

Origine : POC React de la conjointe (artifact Claude), analysé en §2.

## 2. Ce que le POC a déjà résolu (à conserver)

Le POC (~50 articles par défaut, 10 catégories, stockage KV mono-blob) tient sur trois champs :

```js
{ name, category, want, have, checked }
const need = (it) => Math.max(it.want - it.have, 0);
```

**À reprendre tel quel :**

- **Pas de champ « à acheter ».** Il est *dérivé* de `want − have`. C'est le bon design : une
  seule source de vérité, pas de désynchronisation possible entre « il m'en faut 2 » et « j'en ai 1 ».
- **Deux vues, pas une** : « À acheter » (filtre `need > 0`, mode magasin) et « Mon inventaire »
  (tout, avec les steppers voulu/stock). Les deux usages sont vraiment distincts.
- **Catégories ordonnées** = ordre de parcours du magasin (Fruits & légumes → … → Boissons).
  Ce n'est pas de la taxonomie, c'est de l'ergonomie de terrain. L'ordre doit rester éditable.
- **« Valider mes achats »** en fin de session : les articles cochés repassent à `have = want`.
- Les 10 catégories et les 49 articles du POC → **données de seed** de la nouvelle app,
  extraites dans **[`seed-poc.json`](seed-poc.json)** (le code du POC n'est plus la source).
- L'esprit visuel « liste sur papier » (lignes pointillées, leader dots, badges) est reprenable,
  mais **avec les tokens `.ds-*` du design system et le dark mode** (cf. `assets/css/main.css`).
  Pas de reprise du CSS inline du POC.

## 3. Ce qui manque au POC

| Manque | Conséquence |
|---|---|
| **`have` ne baisse jamais tout seul** | Après « Valider mes achats », tout est plein. Il faudrait décrémenter chaque couche à la main. Au bout de 2 semaines l'inventaire ment et « À acheter » est vide en permanence. **C'est le point de rupture de l'app.** |
| **Pas de besoin ponctuel** | « De la pâte feuilletée pour dimanche » oblige à monter `want`… qui reste monté pour toujours. → traité par `DemandePonctuelle` (§5). |
| Pas d'historique | Aucune donnée pour apprendre quoi que ce soit. |
| Pas de multi-utilisateur, pas de sync | Un seul appareil, un seul blob JSON. |
| Pas d'étiquettes | Le cas « Festival » n'est pas couvert (la catégorie est mono-valuée et sert déjà à l'ordre magasin). |
| Pas de conditionnement | « Paquet de 40 couches » ≠ « 40 couches ». |

## 4. L'idée centrale : le stock fond tout seul

> **L'intelligence, ce n'est pas d'ajouter un article à la liste à une date donnée.
> C'est de faire décroître le stock automatiquement.**

```
conso_retenue   = conso_par_jour_estimee, sinon conso_amorce, sinon rien
stock_estimé(t) = stock_référence − conso_retenue × (t − stock_maj_le).jours
besoin(t)       = max(stock_cible − stock_estimé(t), 0) + Σ demandes ponctuelles non satisfaites
```

Conséquences, toutes bonnes :

1. **Zéro saisie supplémentaire.** On ne déclare jamais une consommation. On coche ses courses,
   c'est tout — ce qu'on fait déjà.
2. **L'article remonte tout seul dans « À acheter »** au bon moment. Le cas des couches, c'est
   `conso_amorce = 1` et `stock_référence = 40` au dernier achat — puis l'estimation prend le relais
   et la graine devient inerte.
3. **Calculable côté client** → la vue reste juste **hors ligne**, et aucun cron n'est nécessaire
   pour l'affichage.
4. **La consommation s'apprend.** À partir de 2–3 achats, la médiane de
   `quantité_achetée / intervalle` donne `conso_par_jour_estimee`, qui devient la seule source.
   Avant, `conso_amorce` tient lieu de valeur de départ (§11) — et elle n'est plus jamais relue ensuite.
5. **Recalage manuel possible** : bouton « j'ai recompté, il en reste 12 » → un mouvement de type
   *recalage*, qui remet `stock_référence` et `stock_maj_le` à jour. Facultatif, jamais obligatoire.

**Garde-fous à ne pas oublier :**

- `suivi_auto` désactivable par article. Le lait se consomme régulièrement, pas les piles.
- Ne jamais faire descendre le stock estimé sous 0.
- Les suggestions issues de l'estimation doivent être **visuellement distinctes** d'un ajout humain,
  et **refusables** (« pas maintenant » → snooze + ajustement du rythme). Une suggestion fausse
  qu'on ne peut pas écarter tue la confiance dans l'app entière.

## 5. Modèles proposés

Calqués sur `super_moite_moite` (`Logement` → `Foyer`), avec `base.Profil` comme utilisateur.

```python
class Foyer:                 # ~ Logement de super_moite_moite
    nom, slug, membres = M2M(Profil), archive (bool), date_creation

class Magasin:
    foyer FK, nom, enseigne, actif (bool)
    # auto-complétion à la création d'une Sortie, et clé d'ArticleMagasin

class Rayon:                 # la « catégorie » du POC — ordre = parcours du magasin
    foyer FK, nom, ordre (PositiveInteger, db_index), couleur (ColorField), icone (IconField)

class Etiquette:             # les tags — transverses aux rayons
    foyer FK, nom, couleur   # ex. « Festival », « Bébé », « Bio »

class Article:
    foyer FK, nom, rayon FK (null), etiquettes = M2M(Etiquette)
    unite                    # unité / kg / L / paquet…
    conditionnement          # 40 → « paquet de 40 couches » (unité d'achat ≠ unité de conso)
                             # décimal comme les autres quantités : « bouteille de 1,5 L »
    stock_cible              # le `want` du POC : niveau normal à la maison
    stock_reference          # le `have`, figé au dernier achat/recalage
    stock_maj_le             # date de ce figeage
    conso_par_jour_estimee   # calculé depuis l'historique — la source normale, nullable
    conso_amorce             # GRAINE : ne sert que si conso_par_jour_estimee est nulle, nullable
    suivi_auto (bool)        # active la fonte automatique du stock
    actif (bool), note
    # champs de synchro (cf. §7) : uuid, modifie_le, supprime_le

class Sortie:                # une virée ; PLUSIEURS peuvent être ouvertes en parallèle (§5.1)
    foyer FK, nom (blank), magasin FK (null), cree_par, cree_le, cloture_le
    source                   # manuel | ticket | drive  (cf. §9)

class DemandePonctuelle:     # « il me faut X, en plus du niveau normal » — remplace besoin_ponctuel
    article FK, profil FK    # profil = QUI l'a demandé, affiché dans la liste
    quantite, date
    sortie FK (null)         # rattache la demande à une virée précise (« pour l'apéro »)
    satisfaite_par FK (null) # -> Ligne. On marque, on ne supprime pas : la trace reste
    # uuid, modifie_le, supprime_le

class Ligne:
    sortie FK, article FK, quantite, cochee_le, cochee_par
    indisponible_le (null)     # « pas trouvé en rayon » — ne génère AUCUN mouvement de stock
    article_magasin FK (null)  # le produit précis pris ce jour-là
    prix_unitaire (null)       # ← l'historique des prix vit ICI, pas sur ArticleMagasin
    origine                    # manuel | seuil | suggestion | import
    # uuid, modifie_le, supprime_le

class MouvementStock:        # journal — source de vérité de l'apprentissage
    article FK, type         # achat | recalage | perte
    ligne FK (null)          # la Ligne qui l'a produit — sans elle, « Corriger » ne sait rien défaire
    quantite                 # ⚠ toujours POSITIVE, mais son sens dépend du type (voir note)
    date, profil, commentaire

class ArticleMagasin:        # le produit concret acheté dans CE magasin
    article FK, magasin FK
    libelle                  # « CHOCO AUCH 500G » — tel que le ticket ou le drive l'écrit
    marque                   # « Auchan »
    code_barre               # facultatif
    vu_le, occurrences
    # unique_together (magasin, libelle) — PAS (article, magasin) : voir la note ci-dessous
```

**Notes de conception**

- **Multi-foyer : oui** (`membres` en M2M). Cas d'usage validé : un déménagement doit pouvoir créer
  un nouveau foyer sans détruire l'ancien, d'où aussi `Foyer.archive`.
  → Mais le foyer est un **contexte de navigation**, pas un champ de formulaire : il vit dans l'URL
  (`/courses/<slug-foyer>/`, comme `Logement` dans SMM) et se change par un lien dans la nav.
  **Pas de widget de sélection** — Tom Select serait de l'artillerie pour deux foyers.
- `Sortie` + `Ligne` remplacent le `checked` du POC. « Valider mes achats » = clôturer la sortie :
  chaque ligne cochée génère un `MouvementStock(type=achat)` et remet `stock_reference` /
  `stock_maj_le`. **L'historique se construit sans aucune saisie dédiée.**
- Pas de modèle « Liste ». Une liste spéciale (« courses du festival ») est un **filtre par
  étiquette** sur les articles, qui pousse leur `besoin_ponctuel` d'un coup. Un modèle de plus
  n'apporterait rien.
- **`Magasin` est créé dès la phase 0** — coût nul, et il débloque deux choses : l'auto-complétion
  à la création d'une Sortie, et surtout la clé d'`ArticleMagasin` pour l'import (§9).
  → **L'ordre des rayons par magasin** (le frais n'est pas au même endroit au Leclerc et au Lidl)
  est le vrai gain à terme, et c'est ce qui rend la vue « À acheter » efficace en rayon. Il
  nécessitera une table `OrdreRayonMagasin(magasin, rayon, ordre)`. **Pas maintenant** — mais
  avoir `Magasin` en table dès le début évite une migration douloureuse le jour venu.
- **Le stock estimé n'est pas éditable directement** (conséquence du choix de la direction B, §6.5) :
  il se corrige par « Recompter », qui écrit un `MouvementStock(type=recalage)`. On ne confond donc
  jamais « j'ai recompté, il en reste 12 » avec un tâtonnement, et l'apprentissage (§8) garde des
  données traçables.
- **`MouvementStock.ligne` est indispensable, pas décoratif.** L'écran d'historique permet de corriger
  une sortie clôturée (§6.5) ; sans la FK vers la `Ligne` d'origine, on sait créer l'historique mais
  pas le défaire — et une sortie validée par erreur fausse le rythme de consommation sans recours.
- **`ArticleMagasin` sert deux rôles d'un coup** : il décrit le produit qu'on prend réellement là-bas
  (« les Chocos marque Auchan » pour l'article générique « Chocos ») **et** il tient la mémoire de
  rapprochement de l'import (§9) — c'est la même information vue sous deux angles, donc une seule table.
  → **L'unicité porte sur `(magasin, libelle)`, pas sur `(article, magasin)`** : le ticket de caisse et
  le drive n'écrivent pas pareil (`CHOCO AUCH 500G` vs `Biscuits Choco Auchan 500g`). Plusieurs libellés
  doivent pouvoir pointer vers le même article dans le même magasin.
- **Le prix vit sur `Ligne`, pas sur `ArticleMagasin`.** Un champ `prix` sur le référentiel est écrasé à
  chaque import : on n'a jamais qu'une valeur, donc aucune évolution observable. La `Ligne` est un fait
  daté et rattaché à un magasin (via `Sortie`) : y poser `prix_unitaire` donne l'historique des prix
  gratuitement, et « le prix actuel chez Auchan » comme « la courbe sur 2 ans » deviennent des requêtes.
  Tout est facultatif : l'import remplit ce qu'il trouve, une saisie manuelle ne remplit rien.
- **Toutes les quantités sont décimales** (`DecimalField`, 3 décimales) : `stock_cible`,
  `stock_reference`, `besoin_ponctuel`, `conso_par_jour_estimee`, `Ligne.quantite`,
  `MouvementStock.quantite`, `conditionnement`. Un ticket de caisse indique « 0,834 kg de tomates » — arrondir à
  l'import fausserait le stock, donc l'apprentissage. À l'affichage, une valeur entière se rend sans
  décimale : invisible dans la quasi-totalité des cas.
- **`conso_amorce` est une graine, pas un réglage.** Elle n'est lue que tant que
  `conso_par_jour_estimee` est nulle, et devient définitivement inerte dès que l'historique suffit.
  C'est ce qui donne des suggestions sur les couches dès le premier paquet, sans qu'une valeur saisie
  une fois puisse mentir pour toujours (cf. §11).
- **`indisponible_le` n'est pas un doublon de `cochee_le`.** Les deux sont monotones et exclusifs :
  cocher = acheté (génère un `MouvementStock`), indisponible = pas trouvé en rayon (n'en génère
  aucun, le stock reste juste, et l'article repart dans la liste suivante). Si les deux sont posés,
  « acheté » gagne. Sans cette distinction, une rupture en rayon fausse le stock en silence.
- **`DemandePonctuelle` remplace le compteur `besoin_ponctuel`, et c'est un gain net.** Elle porte le
  demandeur (affiché dans la liste, cf. §6.4) *et* elle **supprime le seul cas qui exigeait une file
  de deltas** (§7.2) : chaque demande est une création d'objet avec son uuid, donc deux personnes qui
  demandent chacune une pâte feuilletée produisent deux lignes — total 2, sans arbitrage possible.
  Le besoin ponctuel d'un article est désormais un **dérivé** : la somme des demandes non satisfaites.
- **`Article.rayon` est nullable.** L'import (§9) doit pouvoir créer un article sans exiger son rayon
  ni ses étiquettes, sinon il devient un formulaire de 30 champs à remplir en rentrant des courses.
  Les articles sans rayon se regroupent en fin de liste (« Sans rayon »), et l'inventaire affiche un
  compteur « n articles à compléter » pour que ça ne pourrisse pas. Préféré à un faux rayon
  « Non classé » à créer pour chaque foyer.
- **`MouvementStock.quantite` porte trois sens selon le `type`** — c'est une source de bugs de signe
  garantie si ce n'est pas écrit noir sur blanc dans le modèle :
  | type | sens de `quantite` |
  |---|---|
  | `achat` | quantité **ajoutée** au stock |
  | `perte` | quantité **retirée** du stock (positive, on soustrait) |
  | `recalage` | **nouvelle valeur absolue** du stock — ni un ajout ni un retrait |
  La valeur reste toujours positive ; c'est le `type` qui porte le signe et la sémantique. Le calcul
  de la §8 doit traiter `recalage` à part : il *remplace* `stock_reference` au lieu de s'y ajouter.
- **Soft delete + unicité = collision à la recréation.** `Etiquette` a `supprime_le` *et*
  `unique_together ("foyer", "nom")` : supprimer « Apéro » puis en recréer une du même nom échoue,
  car la ligne effacée occupe toujours le couple. Il faut une contrainte **conditionnelle** —
  `UniqueConstraint(fields=["foyer", "nom"], condition=Q(supprime_le__isnull=True))`. Ici c'est
  légitime et faisable : la condition ne porte que sur des colonnes de la table (contrairement au
  cas impossible du §5.1).
- **La cohérence inter-foyer doit être validée explicitement** — aucune contrainte de base ne la
  donne. Les quatre couples à vérifier : `Article.rayon` (même foyer que l'article),
  `Ligne` (`sortie.foyer` == `article.foyer`), `DemandePonctuelle` (`article.foyer` ==
  `sortie.foyer`), `ArticleMagasin` (`article.foyer` == `magasin.foyer`). Le scoping de l'admin
  filtre les *listes* mais n'empêche pas l'écriture croisée, et les widgets M2M
  (`filter_horizontal`) ne sont pas scopés du tout. **À faire au plus tard avec l'API (phase 2)** :
  un client buggé mélangerait les données de deux foyers sans qu'aucune contrainte ne bronche.
  C'est de la validation (`clean()` / serializer), pas de la logique métier — les modèles restent
  sans comportement.
- `PhotoAbstract` n'est pas utilisé : une photo par article n'apporte rien et coûte du stockage GCS.

### 5.1 Plusieurs sorties ouvertes — et le piège du double achat

Deux cas d'usage réels, très différents :

| Cas | Déroulé |
|---|---|
| **Le drive** | On prépare la commande sur le site de l'enseigne, on la récupère, puis on l'exporte vers l'app : une `Sortie` **déjà clôturée** est créée sur le bon magasin, les articles inconnus sont créés au passage (§9). |
| **L'apéro imprévu** | On ouvre une `Sortie` nommée (« Apéro samedi »), on y jette 5 articles, on coche en rayon. En parallèle, la liste de la semaine continue de vivre. |

D'où : **oui, plusieurs sorties ouvertes en parallèle.** Mais il y a un piège à désamorcer.

> Le besoin calculé (`stock_cible − stock_estimé`) est un état **du foyer**, pas d'une sortie. Si
> deux sorties sont ouvertes et que « il manque 4 laits » s'affiche dans les deux, on rentre avec 8.

La règle qui l'évite :

- **« Tout ce qui manque »** = le besoin global, vue par défaut, rattachée à aucune sortie.
- **Une sortie** = ce qu'on a décidé d'emporter dans cette virée-là.
- **Un article ne devrait appartenir qu'à UNE sortie ouverte à la fois** — c'est ce qui empêche le
  double achat. Mais **cette règle ne peut pas être une contrainte de base de données**, et il ne
  faut surtout pas essayer :
  - Techniquement, une contrainte unique partielle ne peut pas référencer `Sortie.cloture_le` : la
    clause `WHERE` d'un index partiel ne voit que les colonnes de sa propre table. Dénormaliser un
    booléen `Ligne.sortie_ouverte` pour contourner ça crée un champ dérivé que `bulk_create`,
    `bulk_update` et l'admin contournent **en silence** — et l'import du §9 crée des lignes en masse.
  - Surtout, **une contrainte dure est incompatible avec le local-first.** Deux personnes hors ligne
    ajoutent le lait, l'une à « Courses semaine », l'autre à « Apéro samedi ». Les deux gestes sont
    valides : aucun appareil ne pouvait savoir. Rejeter le second push perdrait le travail de
    quelqu'un — exactement ce que tout le §7 s'attache à éviter.

  **Donc :**
  - **en base** : `UniqueConstraint(fields=["sortie", "article"])` — vrai, sans dénormalisation, et
    attrape le doublon réellement fréquent (deux fois le lait dans la même liste) ;
  - **en applicatif** : à l'ajout, si l'article est déjà dans une autre sortie ouverte, le signaler
    (« déjà dans Apéro samedi ») et proposer de le déplacer. Au push, le serveur **fusionne et
    informe**, il ne rejette pas.
- `DemandePonctuelle.sortie` permet de dire « ces chips, c'est pour l'apéro » sans inventer de
  nouvelle notion de liste.

Une étiquette ne remplace pas ça : elle qualifie l'**article** de façon permanente (« Chips » est
« Apéro » pour toujours), alors qu'une sortie qualifie **un moment**.

## 6. Front : décision

**Décidé : PWA local-first servie par Django, Vue 3 + Dexie.js vendorisés, synchro maison via DRF.
Pas de WebSocket, pas d'app native, pas de sync engine tiers.**

### 6.1 Pourquoi pas les autres pistes

| Piste | Verdict | Motif |
|---|---|---|
| **WebSocket / Django Channels** | ❌ **Bloqué** | PythonAnywhere ne sert que du WSGI : pas d'ASGI, pas de WebSocket. Les *always-on tasks* font bien tourner un processus en continu, mais PA n'y route **aucun trafic HTTP entrant** (pas de port public) : elles servent des workers sortants, pas des connexions entrantes. Le Web tab reste WSGI → Channels reste bloqué. |
| **htmx** | ❌ **Incompatible avec le besoin** | htmx = HTML rendu serveur à chaque interaction. Dans le rayon frais avec deux barres de 4G, il n'y a plus d'app. → **Reporté** : htmx sera testé sur d'autres pages du site, sans contrainte offline. |
| **Flutter / React Native** | ❌ **Coût sans gain** | Sur Android, une PWA installée donne l'icône, le plein écran, IndexedDB, Web Push et Background Sync. Aucun besoin de caméra, GPS ou store. Une app native = un 2ᵉ déploiement, un 2ᵉ build, une 2ᵉ auth, pour zéro fonctionnalité en plus. |
| **Firestore** | ❌ **Sort l'app du projet** | Résoudrait offline + temps réel « gratuitement », mais fait perdre l'admin Django, les modèles, l'auth existante, et le calcul serveur sur l'historique. |

### 6.2 Pourquoi pas ElectricSQL (ni PowerSync, Zero, Triplit, Convex…)

Question posée explicitement, réponse détaillée car l'idée est séduisante.

**ElectricSQL** — trois blocages, du plus dur au plus instructif :

1. **Exige PostgreSQL** avec logical replication. Le projet est en SQLite en dev *et* en prod.
2. **C'est un service séparé à héberger** (Elixir). PythonAnywhere ne fait tourner que le WSGI ;
   impossible d'y lancer un second daemon écoutant sur un port.
3. **Il ne couvre que le chemin de lecture.** Depuis la v1, Electric a abandonné le
   SQLite-embarqué-avec-CRDT de ses débuts pour devenir un moteur de *Shapes* : il streame des
   sous-ensembles de Postgres vers le client en HTTP, et les écritures repartent vers ton API
   comme avant. Même avec Postgres et le service hébergé, **il ne résoudrait que la moitié du
   problème — et c'est la moitié facile.**

Le même raisonnement élimine toute la famille des sync engines « backend-couplés »
(PowerSync, Zero, Triplit, Instant, Convex) : ils imposent leur backend ou Postgres, plus un
service à héberger.

> **À retenir :** le moteur de stockage local n'est pas le sujet. Le sujet, c'est le **protocole
> de synchro** — et celui-ci dépend du domaine, pas de la lib. Pour une liste de courses il est
> trivial (cf. §7). Une synchro maison de ~300 lignes qu'on comprend vaut mieux qu'un moteur
> générique mal maîtrisé qui déraille en rayon.

**SQLite dans le navigateur** (wa-sqlite / sql.js sur OPFS) : techniquement possible, mais ~1 Mo
de WASM pour stocker quelques centaines d'articles. IndexedDB fait le travail sans effort.

**RxDB** : alternative sérieuse — son protocole de réplication est justement fait pour brancher
n'importe quel backend HTTP via des handlers `pull`/`push`. Écarté pour deux raisons : le poids,
et le fait qu'une partie des plugins relève d'une licence Premium payante — risque à long terme
sur un projet perso. **À reconsidérer si la synchro maison s'avère plus retorse que prévu.**

**CRDT (Yjs, Automerge)** : surdimensionné. Les CRDT servent l'édition concurrente de texte ;
ici deux personnes qui cochent le même article ont la même intention.

### 6.3 La stack retenue

| Brique | Choix | Poids | Rôle |
|---|---|---|---|
| Vue | **Vue 3, build global `prod`** | ~35 ko gz | Rendu réactif de la liste, filtres, compteurs |
| Stockage local | **Dexie.js** (wrapper IndexedDB) | ~25 ko gz | Base locale, requêtes, file d'écritures en attente |
| Widgets | **Tom Select** *(déjà vendorisé)* | — | Étiquettes (multi + création), rayon, magasin |
| Synchro | **maison**, contre DRF | — | cf. §7 |

Soit ~60 ko — sobre, et sans étape de build, cohérent avec le reste du site.

**Points d'attention**

- **Vendoriser, pas de CDN.** SMM charge Vue 2.6 depuis jsdelivr ; ici c'est impossible : le
  service worker doit pouvoir mettre tout le nécessaire en cache. Vue 3 et Dexie vont dans
  `assets/js/`, comme Tom Select et Chart.js.
- **Vue 3 sans build** : utiliser le build *global* (avec compilateur de templates) et écrire les
  templates dans le HTML. Pas de fichiers `.vue`, pas de bundler.
- **Conflit de délimiteurs avec Django** : `{{ }}` est revendiqué par les deux moteurs. Fixer
  `delimiters: ['[[', ']]']` à la création de l'app Vue (plus lisible qu'un `{% verbatim %}` global).
- **Auth** : cookie de session Django longue durée, **pas JWT**. Un JWT qui expire pendant qu'on
  est hors ligne au supermarché est un bug garanti. (Les endpoints JWT existants restent en place
  pour le tracker et l'app mobile — on n'y touche pas.)
- **Service worker** : scope `/courses/`, servi depuis ce chemin — attention à
  `collectstatic`/whitenoise et à l'en-tête `Service-Worker-Allowed`.

### 6.4 Maquettes

Canvas des écrans, aux tokens réels de `assets/css/main.css` (thème clair/sombre commutable sur
chaque planche, steppers et coches fonctionnels) :
**https://claude.ai/code/artifact/8b6b0d41-1b9b-4432-a9de-7dedbd5d1dc6**

Sources versionnées dans [`maquettes/`](maquettes/) — éditer les `.dc.html` puis re-générer.

| Écran | Rôle |
|---|---|
| **À acheter** | Mode magasin : groupé par rayon dans l'ordre de parcours, suggestions isolées et refusables |
| **Inventaire** | Jauge de niveau par article, édition au tap (direction B, cf. §6.5) |
| **Historique des sorties** | Sorties clôturées, leur source (saisie / drive / ticket), et « Corriger » |
| **Fiche article** | Création / édition : tous les champs du §5, suivi automatique, conso estimée ou imposée |
| **Journal d'un article** | Les `MouvementStock` du même article + le graphe de fonte du stock |

Navigation : trois onglets de premier niveau (**À acheter · Inventaire · Historique**). La sortie
*en cours* est l'écran « À acheter » — elle n'a pas d'entrée séparée. Le journal d'un article et
l'historique des sorties sont **le même modèle vu par deux bouts**.

### 6.5 Inventaire : direction B retenue

Deux directions ont été maquettées pour la ligne d'inventaire, le point le plus délicat (trois
compteurs + le fait que le stock soit une estimation) :

- **A — tout éditable en liste** : les trois steppers visibles d'un coup. Rejetée.
- **B — jauge + édition au tap** : ~7 articles par écran au lieu de ~4, hiérarchie plus lisible,
  et surtout le stock passe obligatoirement par « Recompter ». **Retenue.**

Le gain n'est pas qu'ergonomique : en A, le stepper de stock écrivait dans `stock_reference` sans
laisser de trace. B force le mouvement de recalage, donc préserve la qualité des données dont
dépend toute la §8.

### 6.6 Le « temps réel » est un faux besoin

Pour deux personnes : polling léger (5–10 s) quand l'app est au premier plan, plus Web Push pour
les notifications utiles. Ça couvre l'intégralité de l'usage réel pour ~1 % de la complexité
d'une stack WebSocket.

## 7. Synchronisation — le protocole

Modèle **pull/push delta avec last-write-wins**, écrit à la main. Pas de CRDT : le domaine ne le
justifie pas. C'est la pièce qu'il faut concevoir avec soin, parce que c'est elle — et non le
stockage local — qui décide si l'app est agréable ou frustrante.

### 7.1 Base

- Chaque objet synchronisable porte un `uuid` **généré par le client**, `modifie_le`, et
  `supprime_le` (soft delete, pour propager les suppressions ; sans tombstone, un objet supprimé sur
  un appareil ressuscite au pull suivant).
- **Pull** : `GET /api/courses/sync/?depuis=<curseur>` → tout ce qui a changé depuis.
- **Push** : `POST` d'un lot d'objets modifiés localement.
- Le client tient une **file d'écritures en attente** dans Dexie, rejouée au retour du réseau
  (Background Sync, ou simplement au `online` / au focus).
- La purge des tombstones se fait côté serveur après un délai large (ex. 90 jours), sinon un
  appareil resté longtemps hors ligne rate la suppression.

**L'`uuid` est un champ unique indexé, PAS la clé primaire.** On garde l'`AutoField` de Django en PK :

- sur SQLite — la base en dev **comme en prod** — un `INTEGER PRIMARY KEY` *est* le rowid, donc accès
  direct et index minimal ; une PK UUID perd cette propriété ;
- les FK internes restent compactes, l'admin et le debug gardent des ids lisibles ;
- l'API de synchro expose l'`uuid`, l'interne travaille en `id`. Le coût est une résolution
  `uuid → id` au push, confinée à l'endpoint de sync et batchable en une requête.

`UUIDField(unique=True, db_index=True, default=uuid4, editable=False)` : le `default` sert aux objets
nés côté serveur (admin, seed, import), et l'endpoint de sync accepte l'uuid fourni par le client.

**Pourquoi un uuid client, et pas juste l'id serveur** — deux raisons, la seconde étant la plus
sournoise :

1. **Identité avant le serveur.** Hors ligne, on crée un `Article` *et* une `DemandePonctuelle` qui
   le référence. Sans identité côté client, la demande pointe vers un id temporaire qu'il faudrait
   remapper partout à la synchro, dans tous les objets liés de la même session.
2. **Idempotence du push.** Si le réseau coupe après l'enregistrement mais avant l'accusé de
   réception, le client rejoue son lot. Avec un uuid, le serveur fait un upsert et rien ne double.
   Avec un id auto-incrémenté, le rejeu crée un doublon — et un `MouvementStock` en double fausse
   l'apprentissage de consommation **en silence**.

**Quels modèles portent un uuid** : ceux qui peuvent naître hors ligne — `Article`, `Sortie`,
`Ligne`, `DemandePonctuelle`, `MouvementStock`, `Etiquette` (création à la volée dans Tom Select).
Le référentiel administré en ligne (`Foyer`, `Rayon`, `Magasin`, `ArticleMagasin`) n'en a pas besoin.

#### En quoi consiste la résolution `uuid → id`

Le client ne connaît que des uuid. Un push de `DemandePonctuelle` ressemble à
`{"uuid": "a3f2…", "article": "7bc9…", "quantite": 1}` : le serveur doit faire de `"7bc9…"` un
`article_id`. Batché, c'est une requête pour tout le lot :

```python
uuids = {d["article"] for d in lot}
correspondance = dict(
    Article.objects.filter(foyer=foyer, uuid__in=uuids).values_list("uuid", "id")
)
```

**Le vrai piège est l'ordre, pas la performance.** Un article créé hors ligne et la demande qui le
référence arrivent dans le même push : au moment de résoudre la demande, l'article n'existe pas
encore côté serveur. Le lot doit donc être traité **dans l'ordre des dépendances** —
`Article` → `Sortie` → `Ligne` → `DemandePonctuelle` / `MouvementStock`. Un uuid encore non résolu
après cette passe signifie que l'objet a été supprimé ailleurs : rejeter **cette ligne** en le
signalant au client, jamais faire échouer le lot entier.

**Et dans l'autre sens** : au pull, les FK sortent en **uuid**, jamais en id — un `article: 42` est
un nombre que le client ne peut relier à rien dans son IndexedDB. Donc `select_related` puis
exposition de `article.uuid`, sous peine de N+1 au pull.

`SlugRelatedField(slug_field="uuid", …)` de DRF fait cette résolution, mais une requête par objet :
sur un lot, préférer la correspondance ci-dessus.

**Corollaire pour les modèles à nom unique** (`Rayon`, `Etiquette`, avec `unique_together
("foyer", "nom")`) : deux personnes peuvent créer l'étiquette « Apéro » hors ligne le même soir, avec
deux uuid différents. Le push ne doit pas rejeter la seconde : le serveur fait un `get_or_create` sur
`(foyer, nom)` et **renvoie au client la correspondance d'uuid** pour qu'il réaligne ses références
locales. Même principe que ci-dessus — fusionner et informer, jamais refuser.

### 7.2 Piège nº 1 — les compteurs ne supportent pas le LWW

C'est **l'erreur classique**, et elle frappe exactement le champ le plus utilisé :

> Toi et elle êtes chacun hors ligne. Elle met « +1 pâte feuilletée », tu mets « +1 pâte feuilletée ».
> En LWW sur l'état, la valeur finale est **1**. Un des deux incréments est perdu silencieusement.

**Règle** : ce qui est un *compteur* se synchronise comme une **opération**, pas comme un état.

| Champ | Synchro | Pourquoi |
|---|---|---|
| `stock_cible` | LWW sur l'état | C'est un réglage : « il nous en faut 2 à la maison ». La dernière volonté exprimée gagne, c'est le comportement attendu. |
| `DemandePonctuelle` | **création d'objet** (uuid client) — aucun conflit possible | Ce qui était un compteur est devenu une table (§5) : deux demandes concurrentes = deux lignes, les deux survivent sans arbitrage. **C'est ce qui a supprimé le besoin de deltas.** |
| `Ligne.cochee_le` | **first-write-wins** (première valeur non nulle) | Monotone : une fois dans le caddie, ça y reste. Décocher est une opération explicite distincte. |
| `Ligne.indisponible_le` | **first-write-wins**, perd face à `cochee_le` | Même logique monotone. Si les deux arrivent, « acheté » gagne : quelqu'un l'a bien trouvé. |
| `stock_reference` / `stock_maj_le` | LWW, mis à jour ensemble | Toujours écrits en couple par un achat ou un recalage — jamais indépendamment. |
| Tout le reste (`nom`, `rayon`, `etiquettes`…) | LWW sur l'état | Conflits rares et bénins. |

**Il ne reste aucun compteur à synchroniser.** Le seul candidat était le besoin ponctuel, et le
passage à `DemandePonctuelle` (motivé par « qui l'a demandé ? ») l'a transformé en créations d'objets
— immunes au conflit par construction. La règle reste à connaître pour tout champ cumulatif qu'on
ajouterait plus tard : un compteur se synchronise comme une opération, jamais comme un état.

### 7.3 Piège nº 2 — ne jamais faire confiance à l'horloge du client

Un téléphone déréglé de deux heures, et le LWW attribue la victoire au mauvais appareil, de façon
permanente et invisible.

**Règle** : le `modifie_le` qui fait autorité est **estampillé par le serveur à la réception**.
Le client garde son propre horodatage local uniquement pour ordonner sa file d'attente. Pour deux
personnes, l'ordre d'arrivée au serveur est un arbitre parfaitement acceptable — pas besoin
d'horloge de Lamport ni de vecteur de versions.

### 7.4 Ce qui reste calculable hors ligne

Le stock qui fond (§4) est une **fonction pure du temps** :
`stock_estimé(t) = stock_reference − conso_retenue × (t − stock_maj_le)` (§4).

Le client la calcule lui-même. Donc **la liste reste juste en rayon, sans réseau**, et aucun cron
n'est nécessaire pour l'affichage — le serveur ne sert qu'à *apprendre* `conso_par_jour_estimee` (§8).

## 8. L'intelligence — au-delà du stock qui fond

Par ordre de rapport valeur / effort :

1. **Apprentissage de `conso_par_jour_estimee`** (§4) — médiane des intervalles entre achats, à partir de
   3 achats. Management command quotidien (tâche planifiée PythonAnywhere).
2. **Notification push** « il te manque 6 articles » quand le besoin dépasse un seuil, ou la veille
   du jour de courses habituel.
3. **Détection du rythme de courses** — « vous faites les courses le samedi » → push le vendredi soir.
4. *(plus tard)* Suggestion d'articles fréquemment achetés ensemble et absents de la liste.

Réutilisable : `django-pandas` est déjà une dépendance du projet (utilisé par `tracker` pour ses
séries temporelles).

## 9. Import d'une Sortie : commande drive & ticket de caisse

Objectif : au lieu de cocher 30 lignes à la main, **reconstituer une `Sortie` clôturée** depuis une
commande drive réceptionnée ou une photo de ticket. L'intérêt dépasse le confort : chaque import
alimente `MouvementStock`, donc **nourrit directement l'apprentissage de consommation** (§8).

### 9.1 Le drive d'abord, le ticket ensuite

La difficulté est inversée par rapport à l'intuition :

| Source | Difficulté | Pourquoi |
|---|---|---|
| **Export / mail de commande drive** | 🟢 Facile | Contenu structuré, noms de produits propres, quantités et prix explicites. |
| **Photo de ticket de caisse** | 🟠 Dur | `PLT BANANE CAT1 EQ`, `YAOURT NAT X16` : abréviations propres à l'enseigne, quantités implicites, tickets froissés. |

**Le problème n'est pas l'OCR, c'est le matching** libellé → `Article` du catalogue. C'est là qu'est
tout le travail, et il existe dans les deux cas — le drive l'a juste beaucoup plus simple.

→ **Livrer le drive en premier.** Le ticket vient après, en réutilisant tout le pipeline.

### 9.2 Pipeline

```
  source (texte drive | photo ticket)
      ↓
  1. ArticleMagasin : rapprochement instantané des libellés déjà connus  (gratuit)
      ↓
  2. LLM vision/texte sur le reliquat, catalogue du foyer fourni en contexte
      ↓
  3. ÉCRAN DE VALIDATION HUMAINE                      ← non négociable
      ↓
  4. Sortie clôturée + Lignes (avec prix) + MouvementStock + ArticleMagasin mis à jour
```

**Étape 2 — pourquoi un LLM et pas un OCR + fuzzy matching maison.** Un modèle avec vision fait
l'extraction *et* le rapprochement en une passe : on lui passe l'image (ou le texte) plus le
catalogue du foyer — quelques centaines de lignes, négligeable en contexte — et il rend du JSON où
chaque ligne pointe vers l'`uuid` d'un article existant ou `null` (= proposition de création).
Un fuzzy matching maison sur `PLT BANANE CAT1 EQ` n'a aucune chance. Coût : quelques centimes par
ticket. Nécessite une `ANTHROPIC_API_KEY` dans `secrets.json`.

**Étape 1 — `ArticleMagasin` est ce qui rend le système durable.** Chaque rapprochement validé est
mémorisé `(magasin, libelle) → article`, avec la marque du produit réellement pris là-bas. Le deuxième
achat des mêmes yaourts au même magasin est reconnu instantanément et gratuitement. **Le système
s'améliore à l'usage et les appels au LLM se raréfient** jusqu'à ne plus concerner que les nouveautés.
Chaque ligne importée pose aussi son `prix_unitaire` : l'historique des prix se constitue sans effort.

**Étape 3 — créer un article doit être quasi gratuit.** Les articles inconnus se créent depuis
l'écran de validation avec **le seul nom** : `rayon` et `etiquettes` restent vides (§5), on complète
plus tard depuis l'inventaire, qui affiche un compteur « n articles à compléter ». Exiger le rayon
ici transformerait un retour de courses en session de saisie de 30 champs — et l'import serait
abandonné au bout de deux fois.

**Étape 3 (suite) — la validation humaine n'est pas optionnelle.** Un ticket mal lu qui fausse
`stock_reference` corrompt l'apprentissage de consommation en aval, et le bug restera **invisible
pendant des semaines** (les suggestions deviennent juste « bizarres »). L'écran doit montrer, ligne
par ligne : libellé brut → article proposé → quantité, tout éditable, avec les rapprochements
incertains signalés.

### 9.2 bis Ce que contient réellement un mail Auchan Drive

Analyse d'un cas réel ([`example-mail.html`](example-mail.html), commande du 22/08/2026, 75 Ko) :

| Donnée | Présente ? |
|---|---|
| N° de commande, montant payé | ✅ `n°373169277`, `80.16 €` |
| Magasin + adresse + créneau de retrait | ✅ `Drive, Zac Du Champ Du Pont 69800 SAINT-PRIEST`, `samedi 22 août 17:30-18:00` |
| Lignes produits | ✅ **35 lignes / 45 unités**, avec libellé, quantité, prix unitaire, total |
| Remise par ligne | ✅ mais en **second montant** : `4 x 1.68 € = 6.72 € 5.04 €` |
| Code-barres / EAN | ❌ absent |
| Image par produit | ❌ absente |

**Le parsing est déterministe — pas besoin de LLM pour l'extraction.** Les libellés portent la classe
`prodTitre`, les prix unitaires `prodDetail`, et les lignes suivent le motif `N x P € = T €`. Un
parser dédié Auchan (~50 lignes) suffit ; le LLM ne sert plus qu'au **matching** des libellés
inconnus (§9.2 étape 2), que `ArticleMagasin` fait disparaître au bout de deux commandes.

**Trois pièges relevés sur le cas réel :**

1. **Ne pas parser le HTML vu dans les devtools du navigateur.** Gmail réécrit les classes CSS à
   l'affichage (`prodTitre` → `m_-4624525442045307526prodTitre`), avec un préfixe qui change à chaque
   message. Le mail *source* a des classes propres — encore une raison de le lire à la source (§9.3).
2. **48 % des libellés sont tronqués à 50 caractères par Auchan**, dans le HTML lui-même. Ce n'est pas
   bloquant : la troncature est déterministe, donc `ArticleMagasin.libelle` reste une clé stable. Mais
   la marge est faible — « GARDEN GOURMET Végétal Pavé Gourmand Courgettes… » et « …Epinards e… »
   partagent 37 des 47 caractères utiles. **Prévoir la détection de collision** plutôt que de
   présumer l'unicité du libellé tronqué.
3. **Deux montants sur une ligne remisée** : prendre le second (prix réellement payé), sinon
   `prix_unitaire` est faux d'environ 25 % sur ces lignes. Et **ne pas répartir le « décagnotté »**
   (−35,19 € ici) sur les articles : c'est un paiement par cagnotte, pas une remise produit.

### 9.3 Conséquences techniques

- **Acheminement du mail : webhook entrant Mailgun sur un sous-domaine dédié.** On transfère le mail
  de confirmation à `courses@in.benbb96.com` ; une *route* Mailgun le POSTe vers une vue Django, qui
  crée une `TacheImport`. Transférer est un geste natif à deux tapes sur Android, sans copier-coller.

  **Contraintes constatées sur les comptes réels** (captures du 23/08/2026) :

  | | État |
  |---|---|
  | Mailgun | plan **Flex à 0 $/mois**, 1000 messages inclus — largement au-dessus de ~4 courses/mois |
  | OVH, offre e-mail | **`redirect`** : quota de comptes **0/0** → aucune boîte créable, donc **pas d'IMAP** |
  | OVH, redirections | **0/1000 utilisées** → une redirection de confort reste possible |
  | MX de `benbb96.com` | `mx{1,2,3}.mail.ovh.net` → **à ne pas toucher**, la messagerie existante en dépend |

  D'où le montage : un **sous-domaine** `in.benbb96.com` porte ses propres MX vers Mailgun, sans
  rien changer à `benbb96.com`. `django-anymail` est **déjà une dépendance du projet** et fournit
  une vue de réception avec vérification de signature — l'intégration est de l'ordre de la trentaine
  de lignes. En option, une redirection OVH `courses@benbb96.com` → `courses@in.benbb96.com` rend
  l'adresse présentable.

  → **L'IMAP a été envisagé puis écarté** : l'offre OVH `redirect` interdit toute boîte, il aurait
  fallu créer un compte Gmail dédié, y stocker un mot de passe d'application sur le serveur et
  écrire une relève périodique — plus de pièces mobiles que le webhook, pour 15 min de latence en
  prime.

  → **Routes confirmées disponibles sur Flex** (capture du 23/08/2026) : la section *Receiving →
  Routes* propose bien « Create route », et Mailgun *parse* le mail avant de le POSTer (corps HTML,
  texte et pièces jointes en champs séparés) — le parser du §9.2 bis reçoit donc du HTML propre,
  sans les réécritures de classes que fait Gmail à l'affichage.

  ⚠️ **Région du compte.** L'interface Mailgun bascule entre **US** et **EU**, et ce n'est pas
  cosmétique : domaines, routes et endpoints d'API sont cloisonnés par région
  (`api.mailgun.net` vs `api.eu.mailgun.net`). Créer `in.benbb96.com` **dans la même région** que
  le domaine d'envoi déjà en service, et si c'est l'EU, poser `MAILGUN_API_URL` dans le réglage
  `ANYMAIL` de `config/settings/prod.py` — absent aujourd'hui, donc l'envoi passe par l'API US par
  défaut. Une route créée dans la mauvaise région reste simplement invisible.

  → Reste à vérifier : si les messages entrants s'imputent sur le quota de 1000/mois.

  → **Sécurité** : vérifier la signature Mailgun (Anymail le fait), **et** l'expéditeur du mail
  (membre du foyer) avant de créer la `TacheImport` — l'adresse est publique par nature.
- **C'est asynchrone.** Un appel LLM sur une photo dure plusieurs secondes : hors de question de le
  faire dans une requête WSGI. → **C'est ici que servent les tâches planifiées et les always-on tasks
  de PythonAnywhere** : une file simple (table `TacheImport` + worker qui la dépile), sans Celery ni Redis.
- **Récupérer une photo de ticket depuis Android** : déclarer `share_target` dans le manifest de la
  PWA, qui devient alors une cible du menu « Partager ». Complémentaire de la voie mail, qui reste
  la meilleure pour le drive.
- Conserver l'image/le texte source rattaché à la `Sortie` : indispensable pour déboguer un import
  douteux a posteriori.

### 9.4 Périmètre

**Phase 5**, après l'intelligence. Cette fonctionnalité n'a de valeur que sur un catalogue déjà
constitué et un usage installé — l'importer trop tôt reviendrait à créer des articles en masse
sans savoir lesquels méritent un suivi.

## 10. Roadmap proposée

Livrer utile vite ; le local-first n'est **pas** la première brique.

- **Phase 0 — Squelette.** `startapp courses`, modèles (dont `Magasin` dès maintenant), migrations,
  admin, et une commande `seed_foyer` qui charge [`seed-poc.json`](seed-poc.json).
  Tests dans `smoke_tests.py`.
  → **Management command, pas data migration** : `Rayon` et `Article` portent une FK vers
  `Foyer`, donc rien ne peut être créé sans qu'un foyer existe. Et comme `db.sqlite3` est
  gitignoré (bases dev et prod indépendantes), le seed devra être rejoué à la main en prod.
- **Phase 1 — Utilisable.** Vues Django rendues serveur (les 2 vues du POC : « À acheter » /
  « Inventaire »), en `.ds-*` + dark mode. Multi-utilisateur, partagé, Tom Select sur les
  étiquettes et le magasin. **Déjà mieux que le POC**, mais en ligne uniquement.
  → *C'est le vrai jalon : à partir de là, vous l'utilisez pour de vrai.*
- **Phase 2 — Offline.** API de synchro DRF (§7), Vue 3 + Dexie, service worker, installation PWA.
- **Phase 3 — Intelligence.** Fonte du stock, apprentissage du rythme, suggestions refusables.
- **Phase 4 — Push.** VAPID + `pywebpush`, notifications.
- **Phase 5 — Import de Sortie** (§9). Drive d'abord, ticket de caisse ensuite.
- **Phase 6 — Scan de code-barres.** `BarcodeDetector` (Chrome Android) pour retrouver un article
  ou créer un `ArticleMagasin` sans le saisir. À tester sur les téléphones du foyer avant de s'engager.

**Backlog, hors roadmap** (retenu mais non prioritaire) : **comparaison des prix entre magasins.**
Les données arrivent gratuitement — `Ligne.prix_unitaire` daté + `Sortie.magasin` (§5) — donc
« le lait est à 1,15 € au Leclerc et 1,32 € à l'Auchan » devient une simple requête, sans champ ni
table de plus. À faire quand l'historique sera assez épais pour que ce soit honnête.

Attendre la phase 1 en usage réel avant de figer la phase 3 : c'est l'usage qui dira quels
articles méritent vraiment un suivi automatique.

## 11. Décisions actées

- **Nom** : module Python `courses`. Nom d'affichage à trancher plus tard (pistes : *Y'a Plus !*,
  *Le Caddie*, *Ça Manque*) — sans impact sur le code.
- **Front** : PWA local-first, Vue 3 + Dexie.js **vendorisés** dans `assets/js/`, synchro maison
  contre DRF. Pas de build, pas de CDN.
- **htmx** : écarté de ce projet, sera testé ailleurs sur le site.
- **Sync engines tiers** (ElectricSQL & co.) : écartés (§6.2).
- **Multi-foyer** : oui, M2M + `Foyer.archive`. Le foyer vit dans l'URL, pas dans un widget (§5).
- **`Magasin`** : créé dès la phase 0. L'ordre des rayons par magasin viendra plus tard.
- **Import de ticket / drive** : retenu, en phase 5, avec validation humaine obligatoire (§9).
- **Inventaire : direction B** (jauge + édition au tap) — donc stock estimé non éditable au stepper,
  corrigé par « Recompter » = `MouvementStock(type=recalage)` (§6.5).
- **Navigation** : trois onglets — À acheter · Inventaire · Historique. La sortie en cours EST
  l'écran « À acheter », pas une entrée séparée (§6.4).
- **`MouvementStock.ligne`** ajouté au modèle : sans cette FK, « Corriger » une sortie clôturée ne
  peut rien défaire.
- **Pas de consommation imposée à la main.** Le rythme vient *uniquement* du calcul sur les
  `MouvementStock` — une valeur saisie est jugée trop fragile. `conso_par_jour` est donc supprimée du
  modèle, il ne reste que `conso_par_jour_estimee`. Finalité assumée : produire une recommandation
  d'ajout à la liste, rien de plus. *(Coût connu : voir §12.1.)*
- **Le motif d'absence d'estimation est recalculé à l'affichage**, jamais stocké — un motif figé
  deviendrait faux en silence dès que l'historique change.
- **`ArticleMagasin`** : le produit concret d'un magasin ; absorbe l'ancien `AliasArticle`. Le prix
  se pose sur `Ligne`, pas sur le référentiel (§5).
- **`conso_amorce`** : une graine, lue seulement tant que l'estimation n'existe pas, puis définitivement
  inerte. Répond au démarrage à froid (3 mois sur les couches) sans la fragilité d'une valeur imposée.
- **Quantités décimales** partout (`DecimalField`) — imposé par l'import de ticket (« 0,834 kg »).
- **`Ligne.indisponible_le`** : « pas trouvé en rayon », distinct de « acheté », sans mouvement de stock.
- **Code-barres** : `code_barre` conservé au modèle, exploité en phase 6.
- **`DemandePonctuelle`** remplace le compteur `besoin_ponctuel` : porte le demandeur (affiché dans
  la liste) et supprime le dernier besoin de deltas à la synchro (§7.2).
- **Plusieurs sorties ouvertes en parallèle** (drive vs apéro imprévu), avec la contrainte « un
  article dans une seule sortie ouverte » pour empêcher le double achat (§5.1).
- **`Article.rayon` nullable** : créer un article à l'import ne doit coûter qu'un nom (§9).
- **Comparaison des prix entre magasins** : retenue au backlog, hors roadmap (§10).

## 12. Points ouverts

1. **Combien d'achats avant de faire confiance à l'estimation ?** 2 donne une réponse vite mais
   bruitée, 3 est plus sûr et retarde d'un cycle. À régler sur des données réelles, pas maintenant.
2. **SQLite en écriture concurrente** — OK pour 2–3 personnes, mais la synchro écrit par lots.
   Vérifier le mode WAL et le `timeout` sur PythonAnywhere.
3. **Réutiliser `Rayon` entre foyers ?** Actuellement par foyer (duplication assumée, simple).
4. Confirmer que PythonAnywhere autorise les requêtes sortantes vers le service de push **et** vers
   l'API du LLM (plan payant — a priori oui, mais à vérifier avant de s'engager sur les phases 4-5).
5. **Faire valider les maquettes (§6.4) par la conjointe** avant de coder la phase 1 — son POC portait
   l'ergonomie d'origine.
