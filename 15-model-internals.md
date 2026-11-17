# 15 — Les fondamentaux des modèles (Foundation Model Internals)

> Module 01 — Construire l'intelligence. Comprendre **ce qu'on manipule** pour faire de bons choix d'architecture. (Livre ch. 2)

## P — Problème

On construit sur des foundation models sans forcément comprendre leur fonctionnement interne. Résultat : mauvais réglages (température, contexte), surprise face à la **latence** du decode, incompréhension des **hallucinations**, choix de modèle mal informés. Quelques notions internes évitent beaucoup d'erreurs en aval.

## D — Définition

- **Token / tokenization / vocabulaire** : le modèle manipule des **tokens** (sous-mots), pas des caractères ni des mots. Le coût (latence, prix) est **proportionnel au nombre de tokens** (lien [09](09-ai-finops.md)).
- **Transformer / attention** : mécanisme Q/K/V qui pondère le contexte. Deux phases : **prefill** (traite le prompt en parallèle) puis **decode** (génère token par token).
- **Model size / scaling laws** : plus de paramètres + plus de données + plus de compute → meilleures performances (Chinchilla : ~20 tokens par paramètre). La taille conditionne la **mémoire GPU** (lien [08](08-serving-inference.md)).
- **Post-training** : après le pré-entraînement, **SFT** (supervised) puis **preference finetuning** (RLHF/DPO) alignent le modèle.
- **Sampling** : la sortie est **probabiliste**. Leviers : **temperature** (aléa), **top-k / top-p** (troncature), greedy, stop tokens → **liste complète des paramètres de génération** en [27](27-generation-parameters.md).

## S — Solution : les implications pratiques

| Notion interne | Conséquence pour ta plateforme |
| --- | --- |
| Coût ∝ tokens ; tokenisation plus chère en langues non-anglaises | budget/latence (FinOps [09](09-ai-finops.md)), gestion du contexte |
| prefill parallèle / decode séquentiel | **decode = goulot** → KV cache, batching ([08](08-serving-inference.md)) |
| sampling probabiliste | **non-déterminisme** : fixer `temperature=0` et un seed pour des tâches exactes/reproductibles |
| scaling laws / taille | choix build-vs-buy et dimensionnement GPU ([08](08-serving-inference.md)) |
| post-training (RLHF) | explique le comportement « aligné » ; base du finetuning ([12](12-finetuning.md)) |

**Nature probabiliste & hallucinations** : le modèle **complète** du texte selon des probabilités → il peut produire des faits faux avec assurance. Taxonomie utile : *self-delusion*, **snowballing** (une erreur en entraîne d'autres), *mismatched internal knowledge*. Atténuations : température basse, **contexte/RAG** ([03](03-rag-data-pipelines.md)), **guardrails** ([04](04-securite-gouvernance.md)), **évals** ([07](07-llmops-evaluations.md) / [16](16-evaluation-quantitative.md)), **mémoire** cohérente ([10](10-memory.md)). Traitement complet (prévenir / **détecter** / gérer) → [17 — Gérer les hallucinations](17-hallucinations.md).

## E — Exemple (DORA)

- **Température basse** (≈0) pour l'analyse de risque : on veut des verdicts **reproductibles**, pas de créativité.
- Comprendre que les longues analyses CoT sont lentes **parce que** le decode est séquentiel → justifie le KV cache / speculative decoding ([08](08-serving-inference.md)).
- Les **hallucinations snowballing** (un article DORA inventé en entraîne un autre) → d'où RAG + citations + guardrails plutôt que « faire confiance » au modèle.

**Limite / piège :** ces internes évoluent vite (nouvelles architectures, MoE, etc.). L'important n'est pas de tout maîtriser, mais de connaître les **conséquences pratiques** (tokens→coût, decode→latence, sampling→non-déterminisme, probabiliste→hallucination).

## Erreurs fréquentes
- Raisonner en « mots » au lieu de **tokens** (mauvaise estimation coût/contexte).
- Laisser une **température élevée** sur une tâche qui exige du déterminisme.
- S'étonner de la latence du decode sans comprendre prefill/decode.
- Croire qu'un gros modèle « ne peut pas halluciner » — c'est intrinsèque au caractère probabiliste.
