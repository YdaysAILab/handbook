# 29 — Multi-utilisateur, concurrence & isolation des sessions

> Module 05 — Déployer et fiabiliser. Couche **transversale**. Un système d'entreprise sert **N utilisateurs en parallèle** — chacun doit rester **privé, isolé, et bien servi** sous charge.

## P — Problème

En démo, **1 utilisateur**. En production, **des dizaines/centaines** d'utilisateurs **simultanés**. Deux risques majeurs, souvent découverts **trop tard** :
1. **Fuite inter-sessions** : l'état/mémoire/contexte d'un utilisateur se mélange avec celui d'un autre → l'agent répond à **Bob** avec les données d'**Alice**. Incident de confidentialité (RGPD), éliminatoire en entreprise.
2. **Effondrement sous charge** : 100 conversations simultanées saturent le serving (Ollama CPU), les pools de connexion, la fenêtre de contexte → latence, timeouts, coûts qui explosent.

## D — Définition

- **Session** : le fil d'interaction d'**un** utilisateur (conversation + état du workflow), identifiée par `session_id` **et** `user_id`.
- **Isolation de session / tenant** : garantir qu'**aucune** donnée (mémoire [10](10-memory.md), cache, état, RAG, trace) ne **traverse** d'un utilisateur à un autre — prolonge l'ACL ([04](04-securite-gouvernance.md)) et le cross-tenant (LLM08, [28](28-securite-llm-threats.md)).
- **Statelessness** : le LLM est **sans état**, et idéalement les **services applicatifs** aussi → l'état vit dans des **stores externes** (PostgreSQL, Redis) **scopés par clé** (`user_id`/`session_id`).
- **Concurrence** : nombre de requêtes/sessions traitées **en parallèle** ; bornée par le serving ([08](08-serving-inference.md)), les pools de connexion, la mémoire.
- **Multi-tenancy** : plusieurs groupes/entités partagent l'infra **avec cloisonnement**.

## S — Solution

**Isolation (confidentialité)**
- **Clé de scope partout** : chaque lecture/écriture — mémoire ([10](10-memory.md)), cache, **état LangGraph**, retrieval ACL ([04](04-securite-gouvernance.md)), trace ([06](06-observabilite.md)) — est **filtrée par `user_id`/tenant**. Jamais de store global partagé sans clé.
- **Aucun état en mémoire de process** partagé entre requêtes (variable globale, singleton, cache local) → **fuite silencieuse** sous concurrence. L'état va dans PG/Redis **scopé**.
- **Caches scopés** : ne pas partager un **prefix/KV cache** entre utilisateurs aux droits différents ([08](08-serving-inference.md)).

**Concurrence (tenue en charge)**
- **Services applicatifs stateless** → **scalables horizontalement** (plusieurs replicas derrière l'API).
- **File / backpressure** devant un serving limité (Ollama CPU) ; **timeouts** ; **pools de connexion** DB/vector dimensionnés.
- **Rate limit + budget par utilisateur** au gateway ([05](05-ai-gateway-routing.md)/[09](09-ai-finops.md)) : un utilisateur ne doit affamer ni les autres **ni la facture** (denial-of-wallet, [28](28-securite-llm-threats.md)).
- **Mémoire de session bornée** (résumé) pour ne pas exploser la fenêtre/coût ([10](10-memory.md)/[27](27-generation-parameters.md)).

**Preuve** : un **test de charge multi-utilisateurs** + un **test d'isolation** (2 utilisateurs aux données disjointes → **aucune fuite**).

## E — Exemple (DORA)

L'assistant sert **~10 juristes** en interne **et** un portail où **100+ clients** posent des questions **en parallèle** :
- chaque conversation a `session_id` + `user_id` ; **mémoire** et **état LangGraph** sont **scopés par utilisateur** (PG/Redis) → le client B ne voit **jamais** le dossier du client A ;
- l'**API/agent** sont **stateless** (3 replicas) ; une **file** absorbe les pics devant Ollama ; chaque utilisateur a un **budget + rate limit** ;
- **test d'acceptation** : 100 sessions simultanées dont 2 aux données disjointes → **aucune fuite**, latence **p95** tenue.

**Limite / piège :** l'isolation ne se vérifie **pas « à l'œil »** → test automatique à 2+ utilisateurs **obligatoire**. L'état partagé le plus sournois est **implicite** (variable globale, cache de process, singleton) : invisible à 1 utilisateur, il fuit dès 2 en parallèle.

## Erreurs fréquentes
- **État en variable globale / mémoire de process** → fuite entre utilisateurs concurrents.
- Mémoire/cache/retrieval **non scopés** par `user_id`/tenant → fuite de données.
- Tester **à 1 utilisateur** et supposer que ça tient à 100.
- Pas de **rate limit/budget par utilisateur** → un seul sature le serving **et** la facture.
- **Session non bornée** → fenêtre de contexte et coût qui explosent.
- Partager un **prefix/KV cache** entre utilisateurs aux droits différents → fuite ([08](08-serving-inference.md)).
