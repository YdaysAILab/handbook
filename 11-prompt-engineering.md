# 11 — Prompt Engineering

> Module 01 — Construire l'intelligence. Le levier d'adaptation **le moins cher** : à épuiser avant RAG, et bien avant le finetuning. (Livre ch. 5)

## P — Problème

On veut adapter le comportement d'un modèle (format, ton, exactitude, respect d'instructions) **sans toucher aux poids ni à l'infra**. Mal fait, le prompt produit des sorties instables, des hallucinations, ou se fait détourner. Bien fait, il résout une grande part des besoins pour un coût quasi nul.

## D — Définition

- **Prompt engineering** : concevoir l'entrée textuelle (instructions + contexte + exemples) pour obtenir le comportement voulu.
- **In-context learning (zero-/few-shot)** : le modèle apprend la tâche à partir d'**exemples dans le prompt**, sans mise à jour de poids.
- **System prompt vs user prompt** : instruction/persona durable vs requête concrète. Les modèles respectent une **instruction hierarchy** (le system prompt prime).
- **Chat template** : le format de tokens spéciaux attendu par *ce* modèle (Llama, etc.). Un mismatch cause des **échecs silencieux**.

## S — Solution

**Best practices (ordre d'impact)**
1. **Instructions claires et explicites** : persona, format de sortie attendu, marqueurs de fin, contraintes.
2. **Fournir un contexte suffisant** : le contexte réduit les hallucinations ; le restreindre au contexte fourni (« réponds uniquement à partir de ces documents ») — c'est le pont avec le RAG ([03](03-rag-data-pipelines.md)).
3. **Décomposer / chaîner les prompts** : une sous-tâche par appel (ex. classification → analyse). Avantages : debug, monitoring, parallélisation, et possibilité d'un **modèle moins cher** par sous-tâche ([09](09-ai-finops.md)).
4. **Laisser le modèle réfléchir (chain-of-thought, self-critique)** : « raisonne étape par étape » → moins d'erreurs, au prix de la **latence**.
5. **Itérer et évaluer** systématiquement dans le système complet (lien évals [07](07-llmops-evaluations.md)).
6. **Versionner** : séparer prompts et code, métadonnées, **prompt catalog** versionné indépendamment du git.
7. **Verbaliser les données structurées** : présenter une ligne de BD / un schéma / un JSON en **langage naturel** dans le prompt (plutôt que du JSON brut) améliore le grounding et réduit les hallucinations ([17](17-hallucinations.md)). C'est le sens **inverse** de la **sortie structurée** ([26](26-structured-output.md)), qui, elle, contraint la *sortie* du modèle.

**Pièges de contexte**
- **Lost in the middle** : l'info au milieu d'un long contexte est moins bien utilisée que celle au début/fin → placer l'essentiel aux extrémités ; tester (NIAH/RULER).

**Volet défensif** : prompt injection, jailbreak, défenses → couverts en [04 — Sécurité](04-securite-gouvernance.md).

## E — Exemple (DORA)

- **System prompt** : « Tu es un analyste de conformité DORA. Tu réponds uniquement à partir des articles fournis, tu cites chaque article, et tu produis `{verdict, articles[], justification}`. »
- **Few-shot** : 2-3 exemples de clauses étiquetées (risque / pas risque) pour cadrer le jugement.
- **Chaînage** : prompt 1 = classifier le type de clause (modèle économique) → prompt 2 = analyse de risque (grand modèle) → prompt 3 = rédaction.
- **CoT** sur l'étape d'analyse ; **prompt catalog** versionné pour rejouer/comparer les versions via les évals.

**Limite / piège :** un prompt n'est **pas** un contrôle de sécurité ni une garantie de format — le **format garanti** vient des **paramètres de génération / décodage contraint** ([27](27-generation-parameters.md), [26](26-structured-output.md)), pas du texte ; il faut aussi des guardrails ([04](04-securite-gouvernance.md)) et des évals ([07](07-llmops-evaluations.md)).

## Erreurs fréquentes
- Sauter au finetuning avant d'avoir épuisé prompt + few-shot + RAG.
- Mauvais chat template → échecs silencieux.
- Tout mettre dans un seul prompt géant au lieu de chaîner.
- Prompts non versionnés → impossible de reproduire une régression.
- Compter sur le prompt pour la sécurité ou le format garanti.
