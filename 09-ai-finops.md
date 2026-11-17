# 09 — AI FinOps

> Module 06 — Optimiser et faire évoluer.

## P — Problème

Les coûts IA (tokens, GPU, fournisseurs) explosent vite et silencieusement. En entreprise, il faut **optimiser le rapport qualité/coût** et **prouver** qu'une optimisation (ex. routage vers un modèle moins cher) **réduit la facture sans dégrader la qualité**. Sinon on sur-paie, ou on dégrade le service sans s'en rendre compte.

## D — Définition

- **AI FinOps** : la discipline qui relie **coût**, **qualité** et **valeur** d'un système IA — mesurer, attribuer, optimiser et gouverner la dépense.
- Leviers : **model routing** (bon modèle pour la bonne tâche), **caching**, **batching/quantification**, choix API vs self-hosted, gouvernance du **cycle de vie des modèles** et éventuel **fine-tuning**.

## S — Solution

```
Mesurer → Attribuer → Optimiser → Prouver
  │          │           │          │
 coût/      par équipe,  routing,   A/B + évals :
 requête    projet,      cache,     coût ↓ ET qualité =
 (traces)   modèle       quantif.
```
- **mesurer** : coût par requête/feature via l'observabilité ([06](06-observabilite.md)) et le Gateway ([05](05-ai-gateway-routing.md)) ;
- **attribuer** : rattacher la dépense à une équipe/un cas d'usage (budgets, chargeback) ;
- **optimiser** : router les requêtes simples vers un petit modèle, mettre en cache, batcher, quantifier, fine-tuner un petit modèle sur une tâche répétitive ;
- **prouver** : toute optimisation passe par les **évals** ([07](07-llmops-evaluations.md)) — on ne réduit le coût que si la qualité tient.

> 💾 **Deux « caches » à ne pas confondre.** **Prompt/KV caching** ([08](08-serving-inference.md)) réutilise le **préfixe stable** (system prompt, long doc) → −75/90 % de coût/latence sur l'input, **sans risque sur la justesse**. **Semantic caching** réutilise une **réponse déjà produite** quand une **nouvelle requête est sémantiquement proche** — fort gain sur des questions **répétitives** (support, FAQ). ⚠️ **Dangereux sur des entrées uniques** : deux contrats « qui se ressemblent » n'ont pas le même verdict DORA → un cache sémantique servirait une **mauvaise** réponse. À réserver aux requêtes **idempotentes/factuelles**, jamais aux verdicts ; et **scoper par utilisateur** ([29](29-multi-user-sessions.md)) comme tout cache.

## E — Exemple (DORA)

**80 % des requêtes sont simples** (classer une clause, extraire une date), 20 % sont des analyses de risque lourdes.

- router les 80 % vers un **petit modèle** (ou un modèle fine-tuné) → forte baisse de coût ;
- garder le **grand modèle** pour les 20 % complexes ;
- **prouver** le gain : A/B sur le dataset d'évaluation → le coût total chute (ex. ÷3) et l'exactitude du verdict reste stable (91-92 %).

Sans la preuve par les évals, le routage « économique » pourrait dégrader les verdicts DORA — un risque de conformité, pas seulement de qualité.

**Limite / piège :** optimiser le coût ne doit jamais contourner les règles de **confidentialité** (un contrat confidentiel ne part pas vers un modèle externe moins cher) ni la **qualité réglementaire**. FinOps s'exerce **sous** les contraintes de sécurité et de qualité, pas au-dessus.

## Le FinOps réel exige des fournisseurs managés

Avec un modèle **self-hosted gratuit** (Ollama), il n'y a **pas de $/token** : on apprend le routage, mais pas la vraie **discipline FinOps**. Pour ça → **fournisseurs managés** (Azure AI Foundry, AWS Bedrock), via le même gateway ([05](05-ai-gateway-routing.md)).

- **Coût réel par token** : mesurable, **comparable** entre modèles/fournisseurs.
- **Budgets + clés virtuelles** (gateway) : plafond par équipe/apprenant, alertes, **chargeback**.
- **Spend reports** : qui a dépensé combien, sur quel modèle, pour quelle feature.
- **Choix par coût/capacité** : GPT-4o-mini vs Claude Haiku vs Llama-Bedrock vs Qwen local → **A/B + évals** ([16](16-evaluation-quantitative.md)) pour prouver le meilleur ratio.

**Pattern hybride (coût ET confidentialité)** : les **80 %** de requêtes simples/publiques → **cloud le moins cher** ; les **analyses confidentielles** → **modèle interne (Ollama)**. On optimise le coût **sous** la contrainte de confidentialité ([18](18-gouvernance-conformite.md)/[23](23-pii-anonymisation.md)).

> **Pour DORA** : routage « confidentiel → interne, public → cloud économique », **budget plafonné par apprenant**, et un **spend report** qui prouve l'économie — c'est l'expérience FinOps que le lab doit offrir.

## Erreurs fréquentes
- Optimiser le coût sans mesurer la qualité → régression invisible.
- Pas d'attribution des coûts → personne n'est responsable, rien ne s'optimise.
- Router sur le prix en ignorant la confidentialité.
- Fine-tuner avant d'avoir épuisé routing + prompt + RAG (complexité prématurée).
- Croire qu'un lab **100 % gratuit (Ollama seul)** enseigne le FinOps — sans **billing réel**, pas de vraie discipline coût.
