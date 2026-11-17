# 14 — User Feedback

> Module 06 — Optimiser et faire évoluer. En production, le feedback utilisateur est la **boucle d'amélioration** et un **data flywheel** concurrentiel. (Livre ch. 10)

## P — Problème

Une fois en production, comment savoir si l'assistant est **réellement** utile et comment l'améliorer en continu ? Les évals hors-ligne ([07](07-llmops-evaluations.md), [16](16-evaluation-quantitative.md)) ne suffisent pas : il faut capter le signal des **vrais utilisateurs**. Mais ce signal est biaisé, parfois piégeux, et peut créer des **boucles de dégradation** si on l'utilise naïvement.

## D — Définition

- **User feedback** : signaux issus des utilisateurs, qui alimentent l'évaluation, le développement, la personnalisation et les **données d'entraînement futures** (data flywheel, lien [13](13-dataset-engineering.md)).
- **Explicit vs implicit** : noté volontairement (thumbs up/down, rating) vs **inféré** des actions.
- **Conversational feedback** : signaux propres aux interfaces LLM (voir ci-dessous).

## S — Solution

**Capter les signaux (surtout implicites)**
- **Correction / reformulation** : « Non… », « Je voulais dire… », une requête reformulée → signal d'échec.
- **User edits** : l'utilisateur corrige la sortie → paire de **preference data** (winning/losing) réutilisable en finetuning.
- **Early termination, regeneration, comparative (better/worse/same)**, organisation des conversations, refus (*refusal rate*).

**Feedback design — quand & comment collecter**
- **Quand** : à la **calibration initiale**, **quand quelque chose échoue** (downvote, handoff humain), et **quand le modèle a une faible confiance** (comparaison côte-à-côte).
- **Comment** : intégration **non-intrusive** dans le workflow (ex. Copilot : Tab = accept) ; consentement / *data donation* / gestion PII ; ne pas demander l'impossible à l'utilisateur.

**Se méfier des biais et des boucles**
- **Biais** : leniency (notes trop clémentes), position, verbosity/longueur, recency.
- **Degenerate feedback loop** : les prédictions influencent le feedback qui renforce les prédictions → amplification des biais (popularity bias, filter bubbles) et **sycophancy** (l'agent devient complaisant/« menteur » pour plaire). Risque de **gouvernance** (lien [04](04-securite-gouvernance.md)).

## E — Exemple (DORA)

- Le juriste **corrige** le verdict ou la justification → l'édition devient une paire de préférence (bon/mauvais) pour améliorer le modèle.
- Un **downvote** sur un rapport déclenche une revue et enrichit le jeu d'évaluation ([16](16-evaluation-quantitative.md)).
- **Faible confiance** → l'agent propose deux analyses côte-à-côte et laisse le juriste choisir (et ce choix est un signal).
- Ces signaux, agrégés et dépersonnalisés, alimentent le **data flywheel** ([13](13-dataset-engineering.md)).

**Limite / piège :** optimiser aveuglément le feedback positif pousse l'agent à la **sycophancy** — dire ce qui plaît plutôt que ce qui est **juste**. En conformité DORA, c'est dangereux : on veut l'exactitude réglementaire, pas la satisfaction. Le feedback se croise toujours avec des évals objectives.

## Erreurs fréquentes
- Ne se fier qu'au feedback **explicite** (rare et biaisé) en ignorant l'implicite.
- Collecter de façon **intrusive** → faible taux de réponse, biais de sélection.
- Optimiser le feedback sans garde-fou → **sycophancy** et boucle dégénérative.
- Utiliser le feedback comme donnée d'entraînement sans consentement / sans retirer la PII ([04](04-securite-gouvernance.md)).
- Confondre « utilisateurs contents » et « réponses correctes ».
- Croire que l'agent « apprend en temps réel » du feedback (modèle naïf du signal de récompense qui ajuste les décisions à la volée) : **le modèle est figé**. Le feedback part dans une boucle **hors-ligne** — évals ([16](16-evaluation-quantitative.md)), dataset ([13](13-dataset-engineering.md)), finetuning ([12](12-finetuning.md)) — pas un ajustement des poids à chaud. L'effet « immédiat » éventuel passe par la **mémoire/le retrieval** ([10](10-memory.md)), pas par de l'apprentissage en ligne.
