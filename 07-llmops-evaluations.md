# 07 — LLMOps, Évaluations & Fiabilité

> Module 05 — Déployer et fiabiliser. Pour le **socle chiffré** des métriques (perplexity, BLEU/BERTScore, pass@k, Elo, biais des juges, dimensionnement du jeu d'éval), voir [16 — Évaluation quantitative](16-evaluation-quantitative.md).

## P — Problème

Comment faire évoluer un système IA (changer un prompt, un modèle, le RAG) **sans régression** ? Comment prouver qu'une nouvelle version est meilleure, et pas juste différente ? Et comment rendre le système **fiable** face aux pannes (fournisseur qui timeout, action rejouée deux fois) ?

## D — Définition

- **LLMOps** : les pratiques d'ingénierie pour développer, tester, déployer et exploiter des applis LLM (équivalent MLOps/DevOps pour les LLM).
- **Évaluations (evals)** : jeux de tests qui mesurent la qualité des sorties (exactitude, pertinence, respect du format, absence de fuite) sur un **dataset de référence**, via métriques automatiques et/ou **LLM-as-a-judge** (technique détaillée en [24](24-llm-as-judge.md)).
- **Quality gate** : seuil dans la CI/CD qui **bloque** le déploiement si les évals régressent.
- **Fiabilité** : retries, timeouts, **idempotence**, reprise après interruption.

## S — Solution

**Évaluer en continu**
```
Dataset de cas DORA (entrées + réponses attendues / critères)
        │
Nouvelle version (prompt / modèle / RAG)  ──▶  evals  ──▶  score
        │                                                   │
   CI/CD  ◀──────────── quality gate (bloque si régression) ┘
```
- construire un **dataset d'évaluation** représentatif (cas faciles, pièges, cas limites) ;
- métriques : exactitude du verdict de risque, bonnes citations, pas d'hallucination, format respecté ;
- intégrer les évals dans la **CI/CD** avec un seuil de blocage.

**Fiabiliser l'exécution**
- **retries** avec backoff sur erreurs transitoires ;
- **timeouts** explicites ;
- **idempotence** : une action répétée (ex. création de ticket) ne doit pas produire de doublon → clé d'idempotence ;
- **reprise** : l'état LangGraph persisté permet de reprendre après crash au lieu de tout rejouer.

## E — Exemple (DORA)

On veut passer l'analyse de risque à un modèle moins cher. On lance les évals sur 200 contrats annotés :
- si l'exactitude du verdict chute de 92 % à 85 % → le **quality gate bloque** le déploiement ;
- si elle tient à 91 % pour un coût divisé par 3 → on déploie (gain FinOps, voir [09](09-ai-finops.md)).

Côté fiabilité : si l'étape « créer ticket GLPI » est rejouée après un timeout, la **clé d'idempotence** empêche un second ticket ; le workflow **reprend** à l'étape interrompue grâce à l'état persisté.

**Limite / piège :** les évals ne valent que ce que vaut le dataset. Un dataset non représentatif donne une fausse confiance. Il doit être enrichi avec les vrais échecs observés en production ([06](06-observabilite.md)).

## Outillage d'évaluation (paysage 2026)

Le handbook enseigne les **concepts** ; ces outils les **implémentent**. On n'en choisit **pas** « le meilleur » : on prend celui qui correspond au besoin (RAG vs agent, dev vs prod, qualité vs sécurité).

| Catégorie | Outils | Rôle | Fiche |
| --- | --- | --- | --- |
| **Éval RAG** | **Ragas** | métriques RAG automatiques (voir ci-dessous) | 03 · 16 |
| **Tests unitaires LLM (TDD)** | **DeepEval** (façon PyTest) | asserter hallucinations/biais/toxicité/exactitude | 16 · 17 |
| **CI / régression + sécurité** | **Promptfoo** (CLI/CI) | tests de régression des prompts/RAG + **jailbreaks** | 16 · 04 |
| **Observabilité + éval** | **Langfuse** (notre stack) · *alt. SaaS :* Arize Phoenix, TruLens, LangSmith | tracer, déboguer, évaluer RAG & **agents** (groundedness) | 06 · 24 |
| **Sécurité / robustesse** | **Giskard** | scanner vulnérabilités, biais, hallucinations, toxicité | 04 · 17 |
| **Plateforme entreprise** | **Braintrust**, LangSmith | jeux de données, comparaison de modèles, **coût/latence/qualité** | 09 · 16 |

> **Dans notre plateforme, observabilité+éval = Langfuse** (OSS, auto-hébergé, **dans le périmètre** → pas de fuite de données). **LangSmith** (propriétaire, SaaS) en est l'équivalent commercial : on le cite pour le paysage, mais on **ne l'utilise pas** — ce serait contraire à nos principes de confidentialité ([04](04-securite-gouvernance.md)). **Phoenix**/**TruLens** (OSS) restent des compléments utiles pour déboguer des traces d'agents.

**Les 4 métriques RAG (Ragas)** — ce que « évaluer un RAG » veut dire concrètement :
- **Faithfulness** : la réponse est-elle **fondée** sur les passages récupérés (pas d'invention) ? ([17](17-hallucinations.md))
- **Answer relevance** : la réponse répond-elle à la question ?
- **Context precision** : les passages récupérés sont-ils **pertinents** (peu de bruit) ?
- **Context recall** : a-t-on récupéré **tout** le nécessaire ?

**Évaluer un agent (≠ évaluer une réponse)** — un agent est une **boucle** `perception → raisonnement → action` ([02](02-mcp-tool-calling.md)) : on ne juge pas seulement la sortie finale, mais le **chemin**. Métriques dédiées (ex. **DeepEval**) :
- **Tool correctness** : l'agent a-t-il appelé **le bon outil** avec les **bons arguments** ? (ex. `dora_kb.search` plutôt que `tickets.create`, bon `contract_id`).
- **Task / goal completion** : la tâche multi-étapes a-t-elle **réellement abouti** (analyse complète, verdict rendu), pas juste produit un texte plausible ?
- **Trajectory** : la **séquence** d'étapes est-elle saine (pas de boucle inutile, pas d'étape manquante) — distinct de « la réponse est-elle bonne ».
- **G-Eval** : critère de jugement **sur mesure** (LLM-as-judge, [24](24-llm-as-judge.md)) quand aucune métrique standard ne colle.

La trace multi-étapes (**Langfuse**, [06](06-observabilite.md)) fournit le *chemin* ; DeepEval **asserte** dessus en CI façon PyTest. ⚠️ Une réponse finale correcte **par chance** malgré une mauvaise trajectoire (mauvais outil, étape sautée) reste un bug — d'où l'évaluation du chemin, pas seulement du résultat.

**Quand quoi**
- **Chatbot RAG simple** (B1) → **Ragas** (qualité RAG) + **Promptfoo** (régression en CI).
- **Agent autonome complexe** (B3/B4) → **Langfuse** (traces multi-étapes, déjà en stack) + **DeepEval** ; **Phoenix** en debug local.
- **Enjeu sécurité** → **Giskard** / **Promptfoo** (jailbreak, fiche 04).
- **Comparaison coût/latence/qualité** → **Langfuse** (déjà en stack) ou **Braintrust** (FinOps, [09](09-ai-finops.md)).

> Le `eval-runner` du projet est un **scaffold** (pour comprendre le principe quality gate/régression). En réel, on **branche l'un de ces outils** — beaucoup s'appuient sur le **LLM-as-judge** ([24](24-llm-as-judge.md)) et alimentent l'**observabilité** ([06](06-observabilite.md)).

## Erreurs fréquentes
- Déployer « au feeling » sans dataset d'évaluation.
- Pas de quality gate → régressions silencieuses en prod.
- Actions non idempotentes → doublons (tickets, écritures) après retry.
- Pas de reprise → un crash relance tout le workflow coûteux depuis le début.
- LLM-as-a-judge non calibré → scores trompeurs.
- **Ajuster le seuil du quality gate *après* avoir vu les résultats** → *goalpost-moving* / cherry-picking. Fixer la barre **avant** de lancer les candidats (pré-enregistrement), comme la baseline figée ; complément de l'anti-contamination ([16](16-evaluation-quantitative.md)).
