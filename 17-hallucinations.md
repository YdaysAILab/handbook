# 17 — Gérer les hallucinations

> Couche **transversale** (fiabilité/qualité). Consolide ce qui était dispersé et ajoute la **détection**. (Livre ch. 2 & 4)

## P — Problème

Un LLM peut énoncer des **faits faux avec assurance** — sans aucun attaquant, juste par sa nature probabiliste ([15](15-model-internals.md)). Pour l'agent DORA, une hallucination = un **risque de conformité** : un article réglementaire inventé, une citation qui n'existe pas, un verdict injustifié. On ne peut pas « faire confiance » au modèle ; il faut **prévenir, détecter et gérer** les hallucinations.

> À ne pas confondre avec la **sécurité** ([04](04-securite-gouvernance.md)) : là, un attaquant manipule le modèle ; ici, le modèle se trompe tout seul.

## D — Définition

- **Hallucination** : sortie non fondée sur les faits ou sur le contexte fourni.
- Deux types :
  - **Faithfulness (cohérence locale)** : la réponse **contredit le contexte fourni** (ex. le contrat/les articles donnés).
  - **Factuality (cohérence globale)** : la réponse contredit le **savoir du monde réel**, même sans contexte.
- Mécanismes (ch. 2) : *self-delusion*, **snowballing** (une erreur en entraîne d'autres), *mismatched internal knowledge*.

## S — Solution : prévenir → détecter → gérer

**1. Prévenir**
- **Grounding par RAG + citations obligatoires** ([03](03-rag-data-pipelines.md)) : répondre **uniquement** à partir des sources récupérées, et citer chaque article.
- **Température basse** ([15](15-model-internals.md)) pour les tâches factuelles.
- **Prompt** qui restreint explicitement au contexte et autorise « je ne sais pas » ([11](11-prompt-engineering.md)).
- **Ne pas finetuner les faits** (ils périment → hallucination figée, cf. [12](12-finetuning.md)).

**2. Détecter** (le volet qui manquait)
- **Factual consistency locale vs globale** : vérifier que la réponse est **bien supportée par les sources** (locale) et/ou par un savoir de référence (globale).
- **Self-verification / SelfCheckGPT** : échantillonner **plusieurs** réponses ; si elles divergent, le modèle est probablement en train d'halluciner.
- **NLI / textual entailment** : un modèle vérifie si la réponse est **entailée** (impliquée) par les passages sources ; sinon → drapeau.
- **AI-judge « faithfulness »** ([16](16-evaluation-quantitative.md)) : juger si la réponse est fidèle au contexte.
- **Confiance via logprobs** : une faible probabilité des tokens peut signaler l'incertitude.
- **SAFE / knowledge-augmented** : décomposer en faits atomiques et vérifier chacun contre une source.

**3. Gérer en production**
- **Guardrail de sortie** ([04](04-securite-gouvernance.md)) : bloquer/signaler une réponse non fondée.
- **Vérifier que chaque citation existe réellement** dans la base (pas d'article inventé).
- **Fallback** : « je ne sais pas » / escalade plutôt qu'une réponse inventée.
- **Human-in-the-loop** si la confiance est faible (branche LangGraph).
- **Observabilité + évals** ([06](06-observabilite.md) / [07](07-llmops-evaluations.md)) : tracer, mesurer le taux d'hallucination, l'améliorer en continu.

## E — Exemple (DORA)

L'agent doit dire si un contrat présente un risque DORA, **en citant les articles**.
1. **Prévenir** : RAG sur les exigences DORA + consigne « cite l'article, sinon dis que tu ne trouves pas ».
2. **Détecter** : un **faithfulness judge** vérifie que le verdict découle des passages récupérés ; un contrôle programmatique vérifie que **chaque article cité existe** réellement dans la base (sinon = hallucination).
3. **Gérer** : si aucun article pertinent n'est trouvé ou si la confiance est faible → **pas d'invention**, escalade au juriste (human-in-the-loop) ; l'événement est journalisé pour enrichir les évals.

**Limite / piège :** aucune méthode ne supprime 100 % des hallucinations. On **réduit** (grounding) et on **attrape** (détection + human-in-the-loop) ; en conformité, le défaut sûr est **refuser/escalader**, pas deviner.

## Erreurs fréquentes
- Compter sur le seul prompt (« ne hallucine pas ») — inefficace sans grounding ni détection.
- Citations **non vérifiées** → l'agent invente des numéros d'articles crédibles.
- Finetuner les faits au lieu d'utiliser le RAG.
- Pas de fallback « je ne sais pas » → le modèle comble le vide par une invention.
- Confondre hallucination (modèle qui se trompe) et attaque (modèle détourné) → voir [04](04-securite-gouvernance.md). La désinformation est le risque **LLM09** de la carte des menaces ([28](28-securite-llm-threats.md)).
