# 05 — AI Gateway & Model Routing

> Module 05 — Déployer et fiabiliser.

## P — Problème

Dans une entreprise, **20 applications IA** utilisent plusieurs fournisseurs LLM (cloud + modèles internes). Chacune gère ses propres clés, budgets, quotas et fallbacks. Résultat : clés éparpillées, coûts illisibles, aucune règle commune, pas de repli quand un fournisseur tombe. Impossible à gouverner.

## D — Définition

- **AI Gateway** : une **couche intermédiaire unique** entre les applications et les modèles. Toutes les applis passent par elle ; elle centralise authentification, routage, quotas, budgets, fallbacks et observabilité. (Implémentations type LiteLLM, passerelles cloud, etc.)
- **Model routing** : la logique qui choisit **quel modèle** sert **quelle requête** (selon complexité, coût, confidentialité, latence).

## S — Solution

Toutes les applications appellent le **Gateway**, qui applique :
- **centralisation des clés** et des budgets par équipe/projet ;
- **routage** : requêtes simples → modèle économique ; analyses complexes → modèle performant ; données confidentielles → **uniquement** modèles autorisés (on-prem/souverain) ;
- **fallbacks** : si le modèle A échoue/est saturé, bascule automatique vers B ;
- **quotas & rate limiting** par application ;
- **observabilité** : chaque requête tracée, coût attribué (voir [06](06-observabilite.md) et [09](09-ai-finops.md)) ;
- **protection des PII à l'egress** : détecter et anonymiser/rédiger les données personnelles **avant** qu'elles ne sortent vers un fournisseur externe → voir [23 — Protection des PII](23-pii-anonymisation.md).

```
20 applis ─▶ AI Gateway ─▶ ┌─ modèle économique (requêtes simples)
                           ├─ modèle performant (analyses complexes)
                           └─ modèle souverain/on-prem (données confidentielles)
              + clés, quotas, budgets, fallbacks, traces centralisés
```

## E — Exemple (DORA)

L'agent DORA pose beaucoup de petites questions (classification, extraction) et quelques analyses lourdes (évaluation de risque d'un contrat).

- les étapes simples (détecter le type de clause) → **petit modèle** peu cher ;
- l'analyse de risque finale → **grand modèle** ;
- un contrat marqué *confidentiel* → routé **uniquement** vers le modèle autorisé en interne, jamais vers un fournisseur externe.

Le Gateway applique ces règles **sans** que chaque application les réimplémente, et attribue le coût à l'équipe Conformité.

**Limite / piège :** le Gateway devient un **point de passage critique**. Il doit être hautement disponible et ne jamais être le maillon qui fuite des données (le routage « confidentiel → modèle autorisé » est une règle de **sécurité**, pas seulement de coût).

## Multi-fournisseurs : l'hybride local + cloud (le vrai pattern entreprise)

Un bon gateway n'est pas « 1 modèle derrière LiteLLM » : c'est un **routeur multi-fournisseurs**. En entreprise, on **combine** :

| Fournisseur | Rôle | Pourquoi |
| --- | --- | --- |
| **Ollama** (self-hosted) | dev + **données confidentielles** | gratuit, **in-perimeter** (data residency, [18](18-gouvernance-conformite.md)/[23](23-pii-anonymisation.md)) |
| **Azure AI Foundry / Azure OpenAI** | production, **FinOps** | billing réel, modèles managés, SLA |
| **AWS Bedrock** | production, variété | Claude, Llama, Titan… sous un même accès |

Le gateway expose tous ces fournisseurs derrière **la même API OpenAI-compatible** (`azure/gpt-4o-mini`, `bedrock/anthropic.claude-…`, `ollama/qwen2.5:7b`) → **ajouter un cloud = quelques lignes de config, pas une refonte**.

**Router selon 4 dimensions** (pas que le coût) :
- **capacité** : petit modèle pour classer/extraire, grand pour raisonner ([08](08-serving-inference.md)) ;
- **coût** : le moins cher qui tient la qualité (prouvé par évals, [09](09-ai-finops.md)) ;
- **latence** : le cloud est souvent plus rapide que le CPU local ;
- **confidentialité** : contrat confidentiel → **modèle interne (Ollama) uniquement** ; public/synthétique → cloud.

**Deux stratégies de routage :**
- **Classification en amont** : on juge la complexité de la requête, puis on route vers le bon palier (ce que décrit le schéma ci-dessus).
- **Cascade / escalade** : on commence au palier **le moins cher** et on **n'escalade que si nécessaire**. Le vrai gain vient d'un **palier 0 déterministe** (checks en **Python pur, 0 appel LLM, coût nul**) ; si la règle de code ne tranche pas → **petit modèle** qui *triage* ; s'il détecte une vraie difficulté → **grand modèle**. ⚠️ **Le routeur lui-même reste déterministe** : on n'utilise pas un LLM pour décider d'appeler un LLM. **Fallback** : en cas d'échec d'un palier, retomber sur le résultat du palier inférieur (plutôt que planter) et **taguer** la méthode (audit). Comme toujours, **prouver** l'économie par les évals ([09](09-ai-finops.md)) — et **la confidentialité prime sur la cascade** (jamais escalader un contrat confidentiel vers un modèle externe).

**Maîtriser la dépense — clés virtuelles** : le gateway émet une **clé virtuelle par équipe/apprenant** avec **budget plafonné + rate limit** → impossible de déraper, et chaque dépense est **attribuée** ([09](09-ai-finops.md)). Côté fournisseur : **BYOK** + **zero-data-retention** pour la conformité.

> C'est **ça** la vraie compétence gateway : choisir fournisseur/modèle par **coût · capacité · latence · confidentialité** — Ollama pour une partie du routage, le cloud pour l'autre.

## Erreurs fréquentes
- Laisser chaque appli gérer ses clés/fallbacks → chaos et surcoût.
- Router sur le coût sans tenir compte de la **confidentialité** → données sensibles chez un tiers.
- Pas de fallback → une panne fournisseur casse toutes les applis.
- Gateway sans observabilité → coûts et incidents invisibles.
