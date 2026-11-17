# 27 — Paramètres de génération (decoding / sampling)

> Module 01 — Construire l'intelligence. Les **leviers runtime** qui contrôlent *comment* le modèle génère. Consolide ce qui était épars dans [11](11-prompt-engineering.md), [15](15-model-internals.md), [08](08-serving-inference.md) et [26](26-structured-output.md).

## P — Problème

Même modèle, même prompt → des sorties **très différentes** selon les réglages. **Trop de hasard** = verdicts non reproductibles, non auditables ; **trop peu** = réponses plates/répétitives. Mauvais réglage de **longueur/contexte** = réponse tronquée **ou** coût qui explose. En contexte régulé, il faut savoir **quel bouton tourner et pourquoi** — un verdict DORA doit être **reproductible**.

## D — Définition

À chaque étape, le modèle produit une **distribution de probabilité** sur le prochain token ([15](15-model-internals.md)). Les paramètres **remodèlent** cette distribution puis **échantillonnent**. Cinq familles :

**1. Hasard / sampling**

| Paramètre | Effet | Plage |
| --- | --- | --- |
| **temperature** | aplatit (haut) / accentue (bas) la distribution. `0` ≈ déterministe (greedy) | 0–2 |
| **top_p** (nucleus) | garde le plus petit ensemble de tokens dont la proba cumulée ≥ p | 0–1 |
| **top_k** | ne garde que les k tokens les plus probables | 1–100 |
| **min_p** | écarte les tokens sous `min_p × proba(top token)` (alternative robuste) | 0–0.1 |
| **seed** | fixe le RNG → **reproductible** (même avec temp > 0) | entier |

**2. Répétition**

| Paramètre | Effet |
| --- | --- |
| **frequency_penalty** | pénalise un token proportionnellement à sa fréquence déjà vue |
| **presence_penalty** | pénalise tout token déjà apparu (pousse vers du nouveau) |
| **repetition_penalty** | pénalité multiplicative sur les tokens déjà vus (style Ollama/HF) |

**3. Longueur & contexte**

| Paramètre | Effet |
| --- | --- |
| **context window** (`num_ctx`) | tokens visibles = **entrée + sortie**. Le plafond dur. |
| **max_tokens** (`num_predict`) | plafond sur la **sortie** seule |
| **stop** | séquences qui **arrêtent** la génération |

**4. Structure de sortie** → voir [26](26-structured-output.md)

| Paramètre | Effet |
| --- | --- |
| **response_format** / `format` | JSON mode ou **schéma** (décodage contraint) |
| **tools** / **tool_choice** | déclarer / forcer / interdire les appels d'outils ([02](02-mcp-tool-calling.md)) |
| **logit_bias** | booster/supprimer des tokens précis (ex. forcer oui/non) |

**5. Observabilité / multi-sorties**

| Paramètre | Effet |
| --- | --- |
| **logprobs** / **top_logprobs** | probas des tokens → confiance, détection d'hallucination ([17](17-hallucinations.md)) |
| **n** / **best_of** | générer N complétions / garder la meilleure |
| **stream** | émettre les tokens au fil de l'eau (latence **perçue**, [21](21-ux-livraison.md)) |

> ⚠️ **context window ≠ max_tokens** : si l'entrée remplit la fenêtre, il ne reste **plus de place** pour la sortie.

## S — Solution

Le bon réflexe — ne régler que ce qui compte :
1. **Déterminisme** → `temperature` (bas) + `seed`.
2. **Diversité vs focus** → `top_p` **ou** `top_k` (pas les deux agressivement).
3. **Éviter le radotage** → `max_tokens` + `stop` + pénalités de répétition.
4. **Tenir le budget** → `num_ctx` dimensionné à l'entrée (coût ∝ tokens, [09](09-ai-finops.md)).
5. **Forme fiable** → `format`/schéma ([26](26-structured-output.md)).
6. **Confiance & debug** → `logprobs`, `stream`.

**Defaults DORA (décision à enjeu) :** `temperature=0`, `seed` fixé, `format=<schéma>`, `num_ctx` ≥ (prompt + docs RAG), `max_tokens` borné, `stop` défini. Toute valeur est **tracée** ([06](06-observabilite.md)) et **versionnée** avec le prompt.

> **Noms :** on cite ici les options **Ollama** (`num_ctx`, `num_predict`, `repeat_penalty`…) car le serving du kit est Ollama ([08](08-serving-inference.md)). Via le **gateway LiteLLM** ([05](05-ai-gateway-routing.md)), on utilise les noms **OpenAI-compatibles** (`max_tokens`, `temperature`, `top_p`, `response_format`, `logit_bias`…).

## E — Exemple (DORA) — réglage Ollama

Verdict de risque **reproductible et structuré** :
```json
// options passées au modèle (Ollama / via LiteLLM)
{
  "temperature": 0,            // déterministe
  "seed": 42,                  // reproductible
  "num_ctx": 8192,             // doit contenir prompt + extraits RAG
  "num_predict": 512,          // borne la sortie
  "stop": ["\n\n\n"],
  "format": {                  // décodage contraint (fiche 26)
    "type": "object",
    "properties": {
      "statut": {"enum": ["conforme", "non_conforme", "indetermine"]},
      "articles": {"type": "array", "items": {"type": "string"}},
      "confiance": {"type": "number"}
    },
    "required": ["statut", "articles", "confiance"]
  }
}
```
Deux exécutions sur le même contrat → **même verdict** (temp 0 + seed) ; le `statut` ne peut **pas** sortir de l'enum (format) ; `num_ctx` garantit que les articles DORA récupérés **tiennent** dans le contexte.

**Limite / piège :** `temperature=0` **réduit** le non-déterminisme mais ne le **garantit pas** à 100 % (ordre de batching/GPU, [15](15-model-internals.md)). Et une fenêtre trop grande coûte cher et dégrade la qualité (« lost in the middle », [11](11-prompt-engineering.md)).

## Erreurs fréquentes
- Confondre **context window** (`num_ctx`) et **max_tokens** → réponses tronquées sans comprendre pourquoi.
- Pousser **température haute** sur une décision à enjeu → verdicts non reproductibles, non auditables.
- Combiner **top_p ET top_k** agressivement → comportement imprévisible (en choisir un).
- Oublier `seed` quand on veut **rejouer** une exécution.
- Ne **pas versionner** les paramètres avec le prompt → régression silencieuse (relier aux évals, [07](07-llmops-evaluations.md)).
- Monter `num_ctx` « au cas où » → coût ↑ et qualité ↓ sans bénéfice.
