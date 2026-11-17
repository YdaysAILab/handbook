# 24 — LLM-as-Judge (évaluer l'IA par l'IA)

> Module 05 — Déployer et fiabiliser. Consolide une technique jusque-là dispersée (fiches [07](07-llmops-evaluations.md)/[16](16-evaluation-quantitative.md)/[17](17-hallucinations.md)) et en fait un outil à part entière. (Livre ch. 3)

## P — Problème

Beaucoup de sorties n'ont **pas de bonne réponse unique** : une analyse de risque DORA, une justification, un rapport. Les métriques lexicales (BLEU/ROUGE) **corrèlent mal** avec la qualité réelle, et l'annotation humaine ne **scale pas**. Comment évaluer ces sorties **open-ended**, à grande échelle, de façon reproductible ?

## D — Définition

- **LLM-as-judge** : utiliser un LLM pour **noter ou comparer** des sorties selon des critères.
- Un **juge = un modèle + un prompt** (tâche + critères + barème). Changer l'un **change le juge**.
- **3 approches** :
  1. **Notation isolée** : scorer une réponse sur des critères (ex. faithfulness 1-5).
  2. **Vs référence** : comparer à une réponse attendue.
  3. **Pairwise** : A vs B, « laquelle est meilleure ? ».
- **Juges spécialisés** : reward models, juges de référence (Prometheus/BLEURT), modèles de préférence.

## S — Solution

**Construire le prompt du juge**
- **Tâche claire** + **critères explicites** + **barème**. Préférer **classification** (bon/mauvais) ou **échelle discrète 1-5** à une note continue (plus stable). Le **few-shot** améliore.
- Demander une **justification** avant la note (chain-of-thought) fiabilise.

**Choisir le juge**
- Juge **plus fort** que le modèle évalué (idéal), **identique** (self-evaluation, à surveiller), ou **plus faible** (spot-check de masse).
- **Spot-checking** : juge bon marché sur 100 % + juge cher sur un échantillon → coût maîtrisé ([09](09-ai-finops.md)).

**Se méfier des biais (essentiel)**
- **Self-bias** (un modèle se préfère), **position bias** (favorise A ou B selon l'ordre), **verbosity bias** (préfère les réponses longues). → **randomiser l'ordre**, barème strict, calibrer.
- **Calibrer** : corréler le juge à un **petit set annoté humain** (30-50 cas) avant de s'y fier.

**Où l'utiliser**
- **Évals offline** et quality gates ([07](07-llmops-evaluations.md)/[16](16-evaluation-quantitative.md)).
- **Faithfulness / détection d'hallucination** ([17](17-hallucinations.md)).
- **Vérification de données synthétiques** ([13](13-dataset-engineering.md)).
- **Guardrail** en production (juger une sortie avant de la livrer).

## E — Exemple (DORA)

Pour évaluer les justifications de l'agent : un juge (`qwen2.5:7b-instruct`) note la **faithfulness** sur **1-5** — « le verdict découle-t-il **uniquement** des articles cités ? » — avec 2 exemples few-shot. En mode pairwise (comparer deux versions de prompt), on **randomise l'ordre** pour neutraliser le position bias. Le juge est **calibré** sur 40 cas annotés par un juriste (corrélation vérifiée) avant d'alimenter le quality gate.

**Limite / piège :** le juge est **lui-même faillible et biaisé** — ce n'est pas une vérité absolue. Toujours **calibrer** contre de l'humain, **randomiser**, et garder un **spot-check humain**. Et c'est un **coût/latence** supplémentaire.

## Erreurs fréquentes
- Traiter le score du juge comme une vérité **sans calibration** humaine.
- Oublier de **randomiser l'ordre** (position bias) en pairwise.
- Barème **continu/flou** → scores instables ; préférer 1-5 ou classification.
- Juge **non versionné** (modèle + prompt) → résultats non reproductibles.
- Self-evaluation naïve (le modèle se note lui-même) sans garde-fou.
