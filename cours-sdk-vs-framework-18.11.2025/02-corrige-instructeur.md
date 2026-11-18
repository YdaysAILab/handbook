# Corrigé — SDK natif ou framework ?

> ⚠️ Document **instructeur** — ne pas distribuer. Sert à **calibrer** l'animation, pas à donner la réponse. Plusieurs choix sont défendables : on évalue **le raisonnement et les axes nommés**, pas le « bon mot ».

## Le message central de la séance (à faire émerger, pas à asséner)

> Un framework ne se choisit **jamais** par défaut ni par popularité. Il gagne sa place quand il **supprime un problème que vous auriez de toute façon** : orchestration stateful, portabilité, écosystème d'intégrations, collaboration de rôles. Sinon, le SDK natif — transparent, léger, auditable — est souvent le meilleur choix. **Le discriminant n°1 est rarement l'IA elle-même : c'est le FLUX (état/branches/reprise) et les INTÉGRATIONS.**

Les SDK natifs modernes font déjà beaucoup (tool calling, **sortie structurée**, streaming, retries). L'écart « SDK vs framework » s'est **réduit** : d'où l'importance de ne prendre un framework que pour ce qu'il apporte **en plus**.

---

## Cas A — 50 000 avis à classer

- **Choix défendable : SDK natif seul.**
- **Axes qui tranchent :** flux = appel unique (1), aucune agentivité (2), aucune intégration (4), script batch jetable/récurrent simple (7).
- **Pourquoi SDK natif (point par point) :**
  1. **Flux = 1 appel LLM par avis, appels indépendants** → une simple boucle `for` suffit, il n'y a rien à orchestrer.
  2. **Sortie structurée native** (`response_format` / tool calling du SDK) → pas besoin des *output parsers* d'un framework.
  3. **Zéro outil, zéro mémoire, zéro état** → il n'y a littéralement rien que LangChain **supprimerait**.
  4. **Volume (50 000 appels)** : tu veux garder la main sur le batching, la concurrence et les retries → une couche framework **masque** ce contrôle.
  5. **Script jetable/récurrent** → moins de dépendances = moins de surface de breaking changes à maintenir.
- **Pourquoi pas framework :** LangChain ici = dépendance lourde + magie pour… une boucle. **Sur-outillage.**
- **Piège :** l'étudiant qui sort LangChain « parce que c'est de l'IA ». Lui demander : *qu'est-ce que LangChain supprime ici que tu aurais dû écrire ?* Réponse honnête : rien.

## Cas A′ — même batch, mais comparer les providers (coût/qualité)

- **Choix défendable : LangChain OU un AI gateway** (les deux). Le **SDK natif seul** reste possible mais devient « j'écris mon propre wrapper de switch ».
- **Axe qui tranche : portabilité provider (3)** — mais cette fois elle est **dans l'énoncé**, donc réelle, pas hypothétique.
- **LE point pédagogique (tout l'intérêt du cas) :** on n'a **pas** changé le flux (toujours un batch, une passe, JSON). On a ajouté **un seul besoin** — et la réponse défendable **bascule**. Message : *l'outil suit le besoin, jamais l'inverse.* C'est le pont A → A′ à faire vivre en direct.
- **La nuance technique à ne pas rater — switcher ≠ LangChain obligatoire.** Trois façons d'obtenir la portabilité :
  1. **SDK natif + wrapper maison (~10 lignes)** ou un `base_url` OpenAI-compatible (Mistral/Groq/Together l'exposent).
  2. **LangChain** (`init_chat_model` / interface `ChatModel` unifiée) — l'abstraction est déjà écrite, gain de temps.
  3. **AI gateway** (voir [fiche 05](../05-ai-gateway-routing.md)) — le routing coût/qualité vit dans **l'infra**, le job reste en **SDK natif non couplé**. Souvent le plus propre pour un *batch*.
     → La vraie question n'est pas « SDK vs LangChain » mais **« où vit la logique de switch : wrapper, framework, ou gateway ? »**
- **Réserve honnête :** « switcher pour la qualité » n'est pas gratuit — prompts, mécanisme de structured output et parsing **diffèrent** par provider. LangChain en lisse une partie, pas tout : **l'abstraction fuit**.
- **Piège symétrique (à relier au Cas A) :** si un·e apprenant·e invoque ce switch **dans le Cas A** (où il n'est **pas** demandé) → c'est du **YAGNI / framework pour le framework**. La discipline : *ce besoin est-il dans le cahier des charges, ou inventé pour justifier l'outil ?*

## Cas B — Démo chatbot d'asso, jetable, 4 jours

- **Choix défendable : SDK natif OU LangChain** — les deux se tiennent.
- **Axes qui tranchent :** flux simple (1), faible agentivité / assistant (2), **time-to-market** (8), jetable (7).
- **Pourquoi les deux se tiennent (point par point) :**
  1. **LangChain fait gagner des heures** : loader PDF + splitter + retriever + chaîne RAG déjà écrits → précieux sous contrainte de 4 jours.
  2. **Mais le RAG minimal est trivial en SDK natif** : charger 30 PDF, embeddings + recherche, 1 appel → quelques dizaines de lignes.
  3. **Jetable** → la dette d'une dépendance framework n'a pas le temps de coûter : le **time-to-market** prime.
  4. **Ni LangGraph ni CrewAI** : aucun état à persister, aucune équipe de rôles → ils n'ajoutent **rien** ici.
- **Piège :** sortir LangGraph « pour bien faire ». Sur-outillage d'un jetable.

## Cas C — Dossier de location stateful + reprise

- **Choix défendable : LangChain + LangGraph.**
- **Axes qui tranchent :** **flux stateful, branches, validation humaine, reprise après crash (1)** — c'est le cœur. Agent qui agit (2).
- **Pourquoi LangChain + LangGraph (point par point) :**
  1. **Reprise après crash** = persistance d'état (checkpointing) : LangGraph la fournit **nativement** ; en SDK natif tu l'écris à la main.
  2. **Branches** (risque élevé → humain / faible → auto) = routage conditionnel d'un graphe → exactement le cœur de LangGraph.
  3. **Validation humaine** = interruption puis reprise (*human-in-the-loop*) : pattern natif LangGraph, pénible à câbler soi-même.
  4. **Nœuds IA** (extraction des pièces, scoring) = briques **LangChain** prêtes à poser dans chaque nœud.
  5. **En SDK natif seul** : tu réécris machine à états + persistance + reprise → fragile, coûteux = réinventer LangGraph **en moins bon**.
- **Pourquoi pas CrewAI :** le besoin n'est pas la collaboration de rôles, c'est le **contrôle du flux**.
- **Piège (erreur inverse à débusquer) :** le puriste « tout SDK natif ». Bonne occasion d'enseigner que le refus dogmatique du framework est **aussi** une erreur.

## Cas D — Même assistant vendu à plusieurs clients

- **Choix défendable : framework (LangChain) pour l'abstraction provider, OU un AI gateway.**
- **Axes qui tranchent :** **portabilité provider (3)**, équipe/maintenance (7).
- **Nuance clé à amener :** deux façons d'obtenir la portabilité — (a) l'**abstraction du framework** (une interface, on change le modèle en 1 ligne), ou (b) un **AI gateway** (routing côté infra, voir [fiche 05](../05-ai-gateway-routing.md)). Faire comparer : le gateway découple **sans** imposer le framework à tout le code. Les deux réponses sont bonnes si l'axe est bien nommé.

### Pourquoi un AI gateway répond au besoin (à faire émerger)

Le besoin du Cas D n'est pas « faire de l'IA », c'est **« router vers le bon provider selon le client, sans toucher à la logique »**. Un gateway est un **proxy** : l'app parle **une seule API** (OpenAI-compatible) au gateway, qui route vers le vrai backend selon sa **config**. C'est la stack réelle de la plateforme : **LiteLLM + Presidio (anonymisation PII) au egress**.

```
app (SDK natif, 1 intégration) ──base_url──► AI GATEWAY ──► OpenAI        (client 1)
                                              (routing)  ──► Mistral/local (client 2 : cloud US interdit)
                                                         ──► …            (client 3)
```

1. **Le switch sort du code.** « Client A → OpenAI, Client B → Mistral/local » vit dans la **config du gateway** (clé virtuelle / header de tenant / nom de modèle). Le code applicatif est **identique** pour tous → littéralement « basculer sans réécrire ».
2. **« Cloud US interdit » devient une règle d'infra.** Le gateway **force la résidence** (route vers un modèle EU/self-hosted). Gouvernance centralisée (enjeu DORA).
3. **Un seul point pour tout le transverse** : clés/secrets, retries, fallback, budget/coût, logs — **et la PII au egress (Presidio)**. Rien à recâbler par client ni par service.
4. **Zéro couplage framework** : l'app reste en **SDK natif**, on change juste `base_url`.

|                                      | **LangChain** (abstraction code)                       | **AI gateway** (routing infra)            |
| ------------------------------------ | ------------------------------------------------------------ | ----------------------------------------------- |
| Où vit le switch                    | dans le **code** (chaque service importe le framework) | dans la **config** (un seul chokepoint)   |
| Changer le routing                   | modif code + redeploy                                        | **changement de config**, pas de redeploy |
| Portée                              | par app Python                                               | **tous les services**, même polyglotte   |
| Qui pilote                           | les devs                                                     | **plateforme / SRE** (gouvernance)        |
| Transverse (PII, budget, résidence) | à recâbler                                                 | **centralisé**                           |

→ Le **gateway gagne** quand le besoin est **multi-client + gouvernance + résidence des données** (exactement le Cas D). **LangChain** reste défendable pour une petite app isolée qui utilise aussi d'autres briques du framework.

- **Réserve honnête :** le gateway est **un composant de plus** à exploiter/sécuriser/rendre HA (point de passage unique → SPOF s'il n'est pas redondé). Il normalise **l'API**, pas le **comportement** : prompts et structured output diffèrent par provider — **l'abstraction fuit encore** un peu.
- **La phrase à retenir :** *LangChain déplace le switch dans le code ; le gateway le déplace dans l'infra.* Pour un SaaS multi-client avec résidence + PII, **l'infra est le bon endroit**.
- **Piège :** croire que le SDK natif rend la portabilité impossible — faux, mais **vous** codez alors la couche d'abstraction. La question est *qui écrit cette couche, vous (wrapper), le framework, ou le gateway ?*

## Cas E — Chercheur → Analyste → Rédacteur

- **Choix défendable : CrewAI (naturel) OU LangGraph** — les deux se défendent.
- **Axes qui tranchent :** **collaboration de rôles (5)** vs contrôle de flux (1).
- **Pourquoi ce choix (point par point) :**
  1. **CrewAI** gagne si tu raisonnes **équipe de rôles** : chaque rôle a un objectif + des outils, et le **handoff** (sortie de l'un = entrée du suivant) est **natif** (task context).
  2. **LangGraph** gagne si le besoin est le **contrôle fin** de l'enchaînement (ordre explicite, nœuds nommés) — même sans état complexe, c'est un graphe linéaire valide.
  3. **SDK natif seul** : 3 appels chaînés à la main → possible, mais **tu** orchestres le passage de contexte et le format d'échange.
  4. **Le discriminant** : « 3 agents » ne décide **rien** ; c'est la **nature** (rôles qui collaborent **vs** contrôle de flux) qui tranche.
- **Piège :** « 3 agents donc CrewAI » asséné sans examiner la nature du besoin.

### Cas E′ — « gérer l'état » et « A2A » : deux objections à trancher

Objection fréquente (et piégeuse) : *« pourquoi pas CrewAI **+** LangGraph, il faut gérer l'état entre les 3 agents, et il y a l'aspect A2A ? »*. Les deux morceaux ne sont **pas** de même nature.

**Distinguer handoff vs orchestration stateful (le cœur).**

| « Handoff » (= le Cas E)                                                                          | « Orchestration stateful » (= ce qui justifie LangGraph)                                                                                                                    |
| --------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| sortie de A = entrée de B, en **séquence linéaire**                                        | **branches** (analyse faible → re-chercher), **boucles** (itérer jusqu'au seuil), **reprise après crash**, validation humaine, état **persisté** |
| géré **nativement par CrewAI seul** (task context) — ou un script séquentiel en SDK natif | là **LangGraph gagne sa place**                                                                                                                                        |

→ Dans le Cas E, « passer la sortie » **n'est pas** de l'état LangGraph. Ajouter LangGraph **ne supprime rien** = même discipline que A′ : *le besoin de flux est-il dans l'énoncé, ou inventé ?*

**Variante (a) — le besoin de flux devient réel** (reboucler si insuffisant + reprise après crash). → La combinaison devient défendable : **LangGraph orchestre (état/branches/reprise), chaque rôle est un nœud** (crew CrewAI ou agent LangChain). C'est le **flux** qui justifie LangGraph, **pas** « il y a 3 agents ». Coût réel à nommer : deux modèles d'orchestration = deux modèles mentaux ; ne l'acheter que si on a *vraiment* besoin des deux.

**Variante (b) — A2A : interop INTER-système, pas INTRA-système.** A2A répond à la collaboration **entre systèmes / équipes / éditeurs** (découverte d'agents, Agent Cards, transport standardisé) — voir [fiche 25](../25-a2a-interop-agents.md) et [fiche 01](../01-langchain-langgraph-crewai.md) (*CrewAI = intra-système ; A2A = inter-système*). Dans le Cas E, les 3 rôles sont **chez nous, un seul système** → A2A **n'apporte rien**, il ajoute un protocole pour un problème qu'on n'a pas (**over-engineering**). A2A **gagne** seulement si une **frontière de propriété / de confiance** traverse le pipeline (l'Analyste = agent d'une autre équipe ou d'un éditeur tiers).

**Le méta-enseignement (à faire dire aux apprenant·e·s).** E′ illustre **les deux versants** de la discipline :

- **A′** : ajouter un besoin **réel** (switch provider) → la réponse bascule **légitimement**. ✅
- **E + état/A2A** : ajouter des besoins **absents** (flux complexe, interop inter-système) → **gold-plating**. ❌
  La compétence = **distinguer le besoin réel du besoin fantasmé**. Question-réflexe : *« ce besoin est-il écrit dans l'énoncé, ou tu l'ajoutes pour justifier l'outil ? »*

## Cas F — Email prospect → tâche → Slack → relance

- **Choix défendable : n8n seul (la classification IA se fait en no-code via les nodes natifs).**
- **Axes qui tranchent :** **intégrations & déclencheurs massifs (4)**, time-to-market (8).
- **Pourquoi n8n (point par point) :**
  1. **~80 % = plomberie d'intégration** (email, tâche Trello/Notion, Slack) → n8n fournit ces connecteurs **prêts**, zéro code d'API.
  2. **Déclencheur + planification** (relance à 48h) = natifs (trigger, *wait/schedule*) → rien à héberger ni à cronner soi-même.
  3. **La classification IA est un node natif** (Text Classifier / AI Agent) → **no-code**, pas besoin d'un agent code.
  4. **Tout coder en SDK natif** = réécrire des dizaines d'intégrations **+** un scheduler → énorme sous-estimation du low-code.
- **La nuance à ne pas rater — n8n fait l'IA sans code.** La classification n'exige **pas** un agent code : n8n a des nodes IA natifs et configurables.
  - **Text Classifier node** : on donne les catégories (`sinistre`, `facture`, `accès IT`, `à vérifier`) + un prompt → il range le texte. Suffit pour le dispatch classique de ce cas.
  - **AI Agent node** : si le système doit **choisir sa prochaine action** selon des résultats intermédiaires (ex. « retrouver un dossier par expéditeur » puis « consulter son gestionnaire »), on branche un modèle + des outils autorisés, toujours **sans code**.
  - → Règle : *étapes connues à l'avance + l'IA sert à comprendre du texte → workflow + node IA. Le système choisit sa prochaine action → agent.* Les deux sont no-code dans n8n.
- **Quand un agent code (webhook/MCP) devient défendable — et seulement alors :** classification trop spécifique/multi-étapes que le node natif ne couvre pas, besoin de **tester/versionner/réutiliser** la brique hors n8n, prompt engineering lourd ou parsing maison. C'est un **choix d'ingénierie optionnel**, pas le défaut.
- **Piège :** coder toute la chaîne d'intégration « parce qu'on sait coder » (sous-estimation du low-code) **— et son symétrique :** croire qu'« il faut du code pour la partie IA » alors que n8n la fait nativement.

## Cas G — Agent en secteur contrôlé, 5 ans, audit

- **Choix défendable : SDK natif seul.**
- **Axes qui tranchent :** **contrôle / transparence / audit (6)**, durée de vie longue + équipe senior (7), flux simple (1).
- **Pourquoi SDK natif seul (point par point) :**
  1. **Besoin simple** (3 outils, flux linéaire) → rien à orchestrer que le framework **supprimerait**.
  2. **Audit = tout expliquer** : le SDK ne cache **aucun** prompt ni indirection → chaque appel est lisible et traçable ligne à ligne.
  3. **Durée de vie 5 ans** : dépendances minimales = moins de breaking changes, moins de CVE, moins de surface à ré-auditer dans le temps.
  4. **Équipe senior** : n'a pas besoin des béquilles (abstractions) du framework ; les écrire soi-même = **contrôle total**.
- **Piège :** réflexe « framework = sérieux / standard entreprise ». Ici le framework **ajoute** de la magie cachée exactement là où la régulation exige de la transparence.

## Les exigences qui décident vraiment — coût, confidentialité, fiabilité (I, J, K)

> Fil rouge de ces trois cas : **le discriminant n'est pas la feature IA, c'est une exigence non-fonctionnelle transversale** (obs, souveraineté, SLA). La bonne question : *« quel outil **du menu** porte cette exigence — un **framework standardisé** (LangChain, n8n) ou le **SDK natif** ? »* À l'échelle d'**une** app, la réponse **reste dans le menu** ; elle ne remonte en infra que sur un **parc polyglotte** (cas limite, pas le défaut).

### Cas I — Suivre le coût et tracer plusieurs outils IA

- **Choix défendable : LangChain (callbacks natifs), standardisé sur les apps et branché sur vos logs — en complément des logs natifs de n8n.** C'est la combinaison du menu qui capture chaque appel sans le coder à la main.
- **Pourquoi callbacks LangChain standardisés (point par point) :**
  1. **Besoin = capturer chaque appel** (tokens, coût, latence, entrées/sorties) → les callbacks LangChain le font **sans instrumenter à la main**.
  2. **Plusieurs apps** → on **standardise** la même brique → format d'événements **homogène**, pas un bricolage différent par service.
  3. **Coût par équipe + audit** = métadonnées attachées à chaque événement → routées vers **tes logs existants**.
  4. **n8n** couvre ses propres flux avec ses logs natifs → **complément**, pas un second outil à câbler.
  5. **LangGraph / CrewAI** n'ajoutent rien : **orchestrer n'est pas observer**.
- **Passage en revue du menu :**
  - **LangChain** : **callbacks/handlers natifs** → à chaque appel on récupère tokens, coût, latence, entrées/sorties. On **standardise** LangChain sur les apps et on **route** ces événements vers vos logs/metrics existants. ✅ **réponse centrale**.
  - **n8n** : logs d'exécution + monitoring **intégrés** → obs native pour ce qui passe **dans** n8n. ✅ **complément** si une partie des flux est en n8n.
  - **LangGraph / CrewAI** : **orchestrateurs**, pas des couches d'obs — n'apportent rien à « coût par équipe + audit ».
  - **SDK natif** : jouable mais **vous** écrivez les callbacks + l'export + l'agrégation à la main → plus de code, moins standardisé.
- **Combinaison défendable :** LangChain (callbacks dans les apps) **+** n8n (ses propres logs), le tout **agrégé dans votre stack de logs**. **C'est la réponse du menu.**
- **Axes qui tranchent :** exigence **transverse** (plusieurs apps) + gouvernance coût/audit → besoin d'un **point d'instrumentation commun**, donc d'une **brique standardisée** (callbacks LangChain), pas d'un bricolage différent par app. Lien [fiche 06](../06-observabilite.md) et [09 — coûts](../09-ai-finops.md).
- **Réserve honnête (le seul cas limite) :** si le parc est **polyglotte** (apps non-Python), LangChain ne peut pas être la couche commune → là seulement l'obs remonte d'un cran. Tant qu'on reste côté app Python, **les callbacks LangChain** sont la réponse.
- **Piège :** instrumenter à la main dans chaque service (dette, incohérence), ou croire que **LangGraph/CrewAI** « font de l'obs ».

### Cas J — Traiter des dossiers confidentiels en local

- **Choix défendable : SDK natif** pointant sur un **endpoint self-hosted OpenAI-compatible** (vLLM) — le plus sûr. **n8n self-hosted** est défendable si le besoin est aussi **intégrations**. LangChain/LangGraph/CrewAI **jouables après audit**. Aucun SaaS externe.
- **Pourquoi SDK natif (ou n8n self-hosted) (point par point) :**
  1. **Contrainte = rien ne sort du réseau** → toute dépendance qui envoie de la télémétrie dehors est **disqualifiante**.
  2. **SDK natif = surface minimale**, zéro indirection cachée, auditable → le plus facile à **prouver** en audit.
  3. **Endpoint OpenAI-compatible (vLLM)** → le code est quasi identique au cloud (souvent juste `base_url`) : la souveraineté ne coûte presque rien en code.
  4. **n8n self-hosted** tourne **derrière le pare-feu** → fort si le besoin est aussi **intégrations**.
  5. **Frameworks jouables mais à auditer** : télémétrie off, deps installables offline, tourne sans Internet → **surface à vérifier**, pas un acquis.
- **Passage en revue du menu (le discriminant n'est pas la marque, c'est « téléphone dehors ? tourne offline ? ») :**
  - **SDK natif** : surface minimale, zéro télémétrie cachée, auditable. Endpoint OpenAI-compatible → code quasi identique au cloud (souvent juste `base_url`). ✅ défaut le plus sûr.
  - **n8n** : **self-hostable** — c'est précisément son atout (tourne **derrière le pare-feu**, 0 cloud). ✅ fort si **intégrations + air-gap** ; vérifier que les nœuds utilisés ne sortent pas sur Internet.
  - **LangChain / LangGraph / CrewAI** : **pas interdits**, mais **à auditer** — (a) désactiver toute télémétrie (aucune trace ne doit **sortir du réseau**), (b) dépendances installables **offline**, (c) ça tourne **sans Internet**. Le framework devient une **surface à vérifier**, pas un acquis.
- **Axes qui tranchent :** **contrôle / souveraineté / résidence (6)**, sécurité. Tout en local = **aucune dépendance qui téléphone dehors**. Lien [fiche 08 — serving](../08-serving-inference.md).
- **Piège :** prendre un framework « parce que c'est pratique » sans vérifier qu'il fonctionne **sans Internet** ni n'exfiltre de traces. Erreur inverse : interdire **par principe** tout framework alors qu'un LangChain audité + offline est parfaitement souverain.

### Cas K — Ne jamais tomber : fallback multi-modèle

- **Choix défendable : LangChain (`.with_fallbacks()` + retries natifs)** pour une app embarquée, **ou n8n** (branche de secours) si c'est un workflow. C'est la brique du menu qui fait le fallback provider **sans le réécrire**.
- **Pourquoi LangChain `.with_fallbacks()` (ou n8n) (point par point) :**
  1. **Besoin = bascule auto primaire→secours + retries** → `.with_fallbacks()` le fournit **déjà**, et c'est **testable en CI**.
  2. **Au moins 2 modèles interchangeables** → axe portabilité : une interface commune suffit à router vers le secours.
  3. **Une app embarquée** → la résilience vit **dans le code de l'app**, versionnée et déployée **avec elle**.
  4. **n8n** : si c'est un workflow, la **branche de secours** + retries par nœud font le job en **no-code**.
  5. **SDK natif** = réécrire retries + fallback + circuit breaker à la main → inutile puisque **la brique existe**.
- **Passage en revue du menu :**
  - **LangChain** : `.with_fallbacks()`, retries, timeouts **intégrés** → bascule primaire→secours **en code**, testable en CI. ✅ **réponse centrale**.
  - **n8n** : gestion d'erreur par nœud, retries, **branche de secours** visuelle → fallback défendable **pour un workflow**.
  - **LangGraph** : peut **modéliser** retry / secours / circuit breaker comme logique de graphe — défendable **si** le flux est déjà stateful ; sinon c'est réécrire la fiabilité à la main.
  - **CrewAI** : hors-sujet (rôles, pas résilience réseau).
  - **SDK natif** : possible mais vous **réécrivez** retries + fallback + circuit breaker à la main.
- **Axes qui tranchent :** **fiabilité / SLA** + **portabilité provider (3)** (il faut au moins 2 providers interchangeables). Lien [fiche 20 — fiabilité](../20-deploiement-fiabilite.md).
- **Réserve honnête (le seul cas limite) :** si le SLA couvre **tout le parc** d'apps, répéter `with_fallbacks()` dans chacune devient incohérent → là seulement la résilience remonte d'un cran. Pour **une** app sous SLA, **LangChain** est la réponse du menu.
- **Piège :** éparpiller la logique de retry/fallback dans chaque app sans la tester ; erreur inverse : la **réécrire en SDK natif** alors que `with_fallbacks()` existe déjà.

> **Le motif récurrent à faire émerger :** une exigence **transversale et non-fonctionnelle** (obs, résidence, SLA, portabilité) se porte **d'abord avec un outil du menu** — un **framework standardisé** (LangChain, n8n) ou le **SDK natif**. Elle ne **remonte en infra** que lorsqu'elle doit couvrir **plusieurs apps / un parc polyglotte** (c'est le sens du Cas D à l'échelle multi-tenant). À l'échelle d'**une** app, la réponse **reste dans le menu**.

## Cas H — Le débat

- **Les deux ont tort.** C'est la synthèse de la séance.
  - Collègue n°1 (« LangChain partout ») : framework par défaut → complexité et dette là où le besoin était simple (cas A, G).
  - Collègue n°2 (« jamais de framework ») → réinvente mal l'orchestration stateful et les intégrations (cas C, F).
- **Réponse d'architecte attendue :** *« On ne choisit ni par principe ni par popularité. On part des capacités requises. SDK natif quand le flux est simple et qu'on veut contrôle/transparence ; LangGraph quand le flux est stateful ; n8n quand c'est de l'intégration ; CrewAI quand ce sont des rôles qui collaborent. Souvent on combine. Le nombre d'agents ou la mode ne décident de rien. »*

---

## Grille d'évaluation rapide (pour chaque réponse d'apprenant·e)

| Niveau          | Signe                                                                                                                                                 |
| --------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| ✅ Solide       | Nomme **l'axe qui tranche**, dit **ce qu'il refuse et pourquoi** (sur/sous-outillage), accepte qu'un cas ait 2 bonnes réponses.          |
| 🟡 Partiel      | Bon choix mais justifié par « c'est le standard » / « c'est de l'IA » au lieu d'un axe.                                                          |
| ❌ À reprendre | Choisit par popularité ou par nombre d'agents ; ne voit pas le flux/les intégrations comme discriminants ; dogmatique (tout-framework ou tout-SDK). |

## Fil rouge à tenir

- Revenir sans cesse à : **« qu'est-ce que cet outil SUPPRIME que tu aurais dû écrire ? »** Si la réponse est « rien », c'est du sur-outillage.
- Et son inverse : **« qu'est-ce que tu t'apprêtes à réécrire qui existe déjà et qui est dur à bien faire ? »** (machine à états, reprise, connecteurs) — c'est là que le framework gagne.
- Lien handbook : fiche [01 — LangChain vs LangGraph vs CrewAI](../01-langchain-langgraph-crewai.md) pour le prolongement.
