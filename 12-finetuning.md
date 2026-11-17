# 12 — Finetuning & adaptation des modèles

> Model development. Le levier d'adaptation **le plus coûteux** : à n'envisager qu'après prompt engineering et RAG. (Livre ch. 7)

## P — Problème

Quand le prompt et le RAG ne suffisent pas — besoin d'un **format très spécifique**, d'un **ton/comportement** constant, d'un petit modèle **spécialisé et moins cher**, ou de combler une lacune de capacité — il faut modifier les **poids** du modèle. Mais le finetuning coûte (données, GPU, talent, maintenance) et peut **dégrader** d'autres capacités.

## D — Définition

- **Finetuning** : adapter un modèle en **ajustant ses poids** (vs méthodes prompt-based). Forme de *transfer learning*.
- Variantes : **SFT** (supervised, sur paires instruction→réponse), **preference finetuning** (RLHF/DPO), continued pre-training, long-context, infilling.
- **PEFT** (*Parameter-Efficient FineTuning*) : n'entraîner qu'une petite fraction des paramètres.
  - **LoRA** : injecte des matrices **low-rank** (A·B) ; on n'entraîne qu'elles → peu de mémoire, adapters légers.
  - **QLoRA** : LoRA sur un modèle **quantifié en 4 bits** → finetuning sur un seul GPU.
- **Model merging / task arithmetic** : combiner plusieurs modèles/adapters (SLERP, task vectors, TIES/DARE, frankenmerging).

## S — Solution

**La décision clé — finetuning vs RAG vs prompting**
> **« Finetuning for form, RAG for facts. »**
- Échec **information-based** (il manque des faits) → **RAG** ([03](03-rag-data-pipelines.md)).
- Échec **behavior-based** (mauvais format/ton/style) → **finetuning**.
- Toujours dans cet ordre : prompt → few-shot → RAG → **finetuning en dernier**.

**Si on finetune**
- **Memory math** : prévoir weights + activations + gradients + optimizer states (≫ la mémoire d'inférence). Leviers : gradient checkpointing, CPU offloading, **quantization** côté training (QAT, mixed precision).
- **PEFT/LoRA** par défaut (full finetuning rarement justifié).
- **Multi-LoRA serving** : un seul *base model* partagé + N adapters légers commutables → au lieu de N modèles complets (fort impact serving/coût, lien [08](08-serving-inference.md)).
- **Tactiques** : learning rate + schedule, batch size + gradient accumulation, epochs selon la taille du dataset. Les données viennent de la fiche [13 — Dataset Engineering](13-dataset-engineering.md).
- **Valider par les évals** ([07](07-llmops-evaluations.md)) : vérifier le gain **et** l'absence de régression (catastrophic forgetting).

## E — Exemple (DORA)

- Besoin **form** : l'agent doit toujours sortir le même JSON structuré et classer le type de clause → **finetuner un petit modèle** (LoRA) sur des clauses annotées. Moins cher, plus rapide, routé pour les 80 % de requêtes simples ([09](09-ai-finops.md)).
- Besoin **facts** : les exigences DORA évoluent → **rester en RAG**, surtout pas finetuner les faits (ils périment).
- Déploiement : **multi-LoRA** sur le base model interne (un adapter « classif clause », un adapter « style rapport ») sans multiplier les GPU.

**Limite / piège :** finetuner les **faits** est un anti-pattern (coût de ré-entraînement à chaque évolution réglementaire, risque d'hallucination figée). Le finetuning fige un **comportement**, pas une base de connaissances.

## Erreurs fréquentes
- Finetuner avant d'avoir épuisé prompt + RAG (complexité et coût prématurés).
- Finetuner des connaissances qui changent (→ RAG).
- Ignorer le **catastrophic forgetting** (gain sur une tâche, perte ailleurs) faute d'évals.
- Full finetuning là où LoRA suffirait.
- Oublier le coût de **maintenance** (re-finetuning quand le base model évolue).
