# 16 — Évaluation quantitative (métriques & ranking)

> Module 05 — Déployer et fiabiliser. Le **socle chiffré** sous la fiche [07](07-llmops-evaluations.md) : pour que les quality gates soient crédibles, il faut les bonnes métriques. (Livre ch. 3-4)

## P — Problème

La fiche [07](07-llmops-evaluations.md) pose le **principe** (datasets, LLM-as-judge, quality gates). Mais *quelle métrique* mesure quoi ? Comment comparer deux modèles rigoureusement ? Comment éviter de se tromper (benchmark contaminé, jeu d'éval trop petit, juge biaisé) ? Sans ce socle, les scores donnent une **fausse confiance**.

## D — Définition : les familles de métriques

**1. Language modeling metrics** (mesurent la prédictibilité, pas la tâche)
- **Entropy / cross entropy / KL divergence** : difficulté de prédire le token suivant.
- **Perplexity (PPL)** = exp(cross entropy). Basse = modèle « sûr ». Usages concrets : détecter une **contamination** de benchmark, **dédupliquer** des données, repérer du texte anormal. ⚠️ mauvais proxy après SFT/RLHF/quantization.
- **BPC / BPB** (bits-per-character/byte) : variantes comparables entre tokenizations.

**2. Exact evaluation** (jugement sans ambiguïté)
- **Exact match** (réponses courtes/factuelles).
- **Functional correctness / pass@k** : exécuter le code/SQL généré contre des tests (HumanEval, Spider).

**3. Similarity vs référence**
- **Lexical** : BLEU, ROUGE, METEOR, edit distance (chevauchement de tokens — faible corrélation avec la correction).
- **Semantic / embedding** : cosine similarity, **BERTScore**, MoverScore.

**4. Comparative evaluation / ranking**
- **Win rate** + algorithmes **Elo / Bradley-Terry / TrueSkill** (ex. Chatbot Arena). Prédit les matchs futurs ; pas de « vrai » ranking de référence.

## S — Solution

- **Choisir la métrique selon la tâche** : exact match/pass@k pour du vérifiable ; AI-judge ([07](07-llmops-evaluations.md)) ou embedding similarity pour de l'open-ended ; comparative/Elo pour classer des modèles sur de la qualité subjective.
- **Se méfier des biais du juge IA** : *self-bias* (un modèle se préfère), *first-position bias*, *verbosity bias* → randomiser l'ordre, calibrer.
- **Détecter la contamination** (*data leakage*) : overlap n-gram, perplexité anormalement basse. Règle : « un benchmark cesse d'être utile dès qu'il devient public ».
- **Dimensionner le jeu d'éval** : **bootstrapping** pour tester la fiabilité ; détecter une petite différence demande **beaucoup** plus d'échantillons (règle OpenAI : 3× moins de diff → ~10× plus d'exemples).
- **Relier aux métriques métier** : mapper une métrique technique (ex. factual consistency) à un impact (% d'automatisation, *usefulness threshold*). Un **win rate de 51 % ≠ gain métier mesurable**.

## E — Exemple (DORA)

- **Verdict de risque** (élevé/faible) → **exact match / accuracy** contre un jeu annoté ; `pass@k` non applicable.
- **Justification rédigée** → **AI-judge** (faithfulness, citations correctes), en se méfiant du verbosity bias.
- **Choix du modèle** (grand vs petit pour le routing [09](09-ai-finops.md)) → **comparative evaluation** sur les contrats annotés.
- **Fiabilité du score** : bootstrapping pour s'assurer que l'écart 92 % vs 91 % est significatif avant de brancher le **quality gate** ([07](07-llmops-evaluations.md)).
- **Anti-contamination** : vérifier que le jeu d'éval DORA n'a pas fuité dans les données d'entraînement/few-shot.

**Limite / piège :** une **perf relative** (un modèle « gagne » 51 % des duels) ne se convertit pas trivialement en **valeur métier**. Et un jeu d'éval trop petit ou contaminé donne des scores rassurants mais faux.

## Erreurs fréquentes
- Utiliser la **perplexity** comme preuve de qualité sur un modèle post-entraîné.
- Confondre **lexical similarity** (BLEU/ROUGE) et correction réelle.
- Ignorer les **biais du juge** (self/position/verbosity).
- Jeu d'éval **trop petit** → différences non significatives prises pour des gains.
- Benchmark **contaminé** → surestimation ; ne pas vérifier le leakage.
- S'arrêter au **win rate** sans le relier à une métrique métier.
