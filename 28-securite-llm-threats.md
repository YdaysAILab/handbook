# 28 — Sécurité des systèmes IA (OWASP LLM Top 10 & threat model)

> Module 04 — Sécuriser et gouverner. La **carte des menaces** d'un système IA. Complète [04](04-securite-gouvernance.md) (contrôles d'accès + injection) en couvrant les risques moins traités. Couche **transversale**.

## P — Problème

En entreprise régulée, la sécurité est un **go/no-go**. Un système IA a une **surface d'attaque élargie** : le modèle est **crédule**, l'agent **agit**, le RAG **ingère du contenu non fiable**, les outils **touchent des systèmes réels**, la mémoire **persiste**. Les contrôles classiques (pare-feu, IAM) ne suffisent pas — il faut un **modèle de menace propre à l'IA**, et une **checklist** pour ne rien oublier.

## D — Définition

- **Référentiels** : **OWASP LLM Top 10** (le plus actionnable — on s'appuie dessus), **MITRE ATLAS** (TTPs adverses), **NIST AI RMF** (gouvernance du risque).
- **OWASP LLM Top 10 (2025) → où c'est traité dans le kit** :

| # | Risque | Traité |
| --- | --- | --- |
| LLM01 | **Prompt injection** (directe/indirecte, jailbreak) | [04](04-securite-gouvernance.md) |
| LLM02 | **Divulgation d'info sensible** (PII, extraction) | [04](04-securite-gouvernance.md), [23](23-pii-anonymisation.md) |
| LLM03 | **Supply chain** (modèles/libs/datasets/MCP tiers) | **§S** + [13](13-dataset-engineering.md) |
| LLM04 | **Empoisonnement** données/modèle (poisoning, backdoor) | **§S** |
| LLM05 | **Mauvais traitement des sorties** (SQL/XSS/RCE en aval) | **§S** |
| LLM06 | **Agentivité excessive** (sur-permissions/autonomie) | **§S** + [02](02-mcp-tool-calling.md) |
| LLM07 | **Fuite du system prompt** | [04](04-securite-gouvernance.md) |
| LLM08 | **Faiblesses vecteurs/embeddings** (cross-tenant, inversion) | **§S** + [03](03-rag-data-pipelines.md) |
| LLM09 | **Désinformation** (hallucination) | [17](17-hallucinations.md) |
| LLM10 | **Consommation non bornée** (DoS, denial-of-wallet) | **§S** + [05](05-ai-gateway-routing.md), [09](09-ai-finops.md) |

## S — Solution : combler les angles morts

LLM01/02/07/09 sont couverts ailleurs. Voici les **risques peu traités**, chacun = menace → défense.

- **LLM05 — Mauvais traitement des sorties** : la sortie du LLM est une **entrée non fiable** pour l'aval. Si elle alimente une requête **SQL**, du **HTML**, un **shell** ou un appel d'API → injection (SQLi, XSS, RCE). **Défense :** échapper/valider la sortie **comme une entrée utilisateur** ; requêtes **paramétrées** (jamais de concaténation) ; pas d'`eval` ; **sortie structurée + validation** ([26](26-structured-output.md)).
- **LLM06 — Agentivité excessive** : trop de permissions, d'autonomie, d'outils → l'agent fait plus que nécessaire (ou qu'une injection lui demande). **Défense :** **moindre privilège** sur les outils (capacités étroites, scope minimal, [02](02-mcp-tool-calling.md)) ; **human-in-the-loop** sur les actions à fort impact ([04](04-securite-gouvernance.md)) ; **borner l'autonomie** (nb d'étapes, pas d'action irréversible sans validation).
- **LLM04 — Empoisonnement** : un attaquant corrompt les **données d'ingestion RAG**, le **dataset de finetuning**, ou introduit un **backdoor** dans un modèle tiers. **Défense :** **provenance/lineage** des données ([18](18-gouvernance-conformite.md)), contrôle des sources d'ingestion, évals de sécurité, modèles de **source fiable**.
- **LLM03 — Supply chain** : modèles, libs, datasets, **serveurs MCP tiers** = dépendances compromissibles (modèle piégé, lib malveillante, **MCP rug-pull**, licence). **Défense :** **épingler les versions**, vérifier l'intégrité (checksums/signature), **SBOM**, registres de confiance, **auditer les serveurs MCP tiers** ([02](02-mcp-tool-calling.md)).
- **LLM08 — Faiblesses vecteurs/embeddings** : le RAG est une surface d'attaque — **injection indirecte** via docs ingérés ([04](04-securite-gouvernance.md)), **fuite cross-tenant** si l'ACL n'est pas **au retrieval**, **inversion d'embedding** (reconstruire le texte depuis le vecteur). **Défense :** **ACL au retrieval obligatoire** ([03](03-rag-data-pipelines.md), [04](04-securite-gouvernance.md)), **isolation par tenant** dans la vector DB (y compris **sous concurrence**, [29](29-multi-user-sessions.md)), contenu ingéré = **non fiable**, index chiffré.
- **LLM10 — Consommation non bornée** : prompts coûteux, **boucles d'agent** infinies, requêtes massives → épuisement ressources **et facture** (**denial-of-wallet**, propre au pay-per-token). **Défense :** **rate limiting + quotas + budgets plafonnés au gateway** ([05](05-ai-gateway-routing.md), [09](09-ai-finops.md)), **timeouts**, **borne du nb d'étapes** d'agent, taille max entrée/sortie, détection d'abus.
- **Secrets** : clés API/modèle, **tokens OAuth** des outils — jamais dans le prompt, le code, ni les logs/traces ([06](06-observabilite.md)). **Secret store** (Vault/secret manager), **rotation**, scope minimal.
- **Transverse — threat modeling & test** : **modéliser les menaces par frontière** (entrée · RAG · outils · sortie · **mémoire**, [10](10-memory.md)) en réutilisant le schéma défense-en-profondeur de [04](04-securite-gouvernance.md) ; **red teaming** IA + **tests de sécurité en CI** (ex. Giskard, [07](07-llmops-evaluations.md)) ; mapper son système sur **l'OWASP Top 10 comme checklist**.

## E — Exemple (DORA)

Plusieurs menaces **chaînées** sur l'agent DORA :
- Un **contrat empoisonné** (LLM04/LLM08) contient une injection indirecte + une instruction cachée.
- L'agent **sur-permissionné** (LLM06) pourrait **écrire dans l'ERP** sur la seule foi du texte.
- Son verdict alimente un **rapport HTML** (LLM05) → **XSS** si non échappé.
- Un utilisateur malveillant lance **10 000 analyses** (LLM10) → **denial-of-wallet**.

**Défenses cumulées :** ACL au retrieval + contenu ingéré non fiable ; outils à moindre privilège + **human approval** ; sortie **échappée/structurée** ; **budgets + rate limit** au gateway ; **lineage** des contrats ingérés ; **tout tracé** ([06](06-observabilite.md)). Aucune couche seule ne suffit → **défense en profondeur**.

**Limite / piège :** aucune défense n'est parfaite et le paysage de menaces **évolue** ; la sécurité est un **processus continu** (threat model vivant, red teaming récurrent), pas une case cochée. Mapper l'OWASP Top 10 **réduit** les angles morts, ne les **élimine** pas.

## Erreurs fréquentes
- Traiter la **sortie du LLM comme fiable** en aval (SQL/HTML/shell) → injection (LLM05).
- Agent **sur-permissionné** « pour que ça marche » → agentivité excessive (LLM06).
- Pas d'**ACL au retrieval** → **fuite cross-tenant** dans le RAG (LLM08).
- Ingestion RAG / dataset **sans contrôle de provenance** → empoisonnement (LLM04).
- Pas de **budget/rate limit/timeout** → **denial-of-wallet** (LLM10).
- Dépendances (modèles, **MCP tiers**) **non épinglées/non vérifiées** (LLM03).
- **Secrets** dans le prompt ou les logs.
- Ne **jamais mapper** son système à un référentiel (OWASP/ATLAS) → angles morts.
