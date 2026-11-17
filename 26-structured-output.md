# 26 — Sortie structurée (structured output)

> Module 01 — Construire l'intelligence. Le **contrat machine** entre le LLM et le reste du système. Sous-tend le tool calling ([02](02-mcp-tool-calling.md)), l'extraction ([19](19-document-understanding.md)), la classification et le [24 — LLM-as-judge](24-llm-as-judge.md).

## P — Problème

Par défaut, un LLM produit du **texte libre**. Or un système a besoin de **données exploitables par la machine** : un verdict `{conforme: bool, articles: [...], score}`, des champs extraits d'un contrat, une étiquette de classe, les arguments d'un outil, la note d'un juge. **Parser du texte libre** (regex, « découpe après `:` ») est **fragile** : le modèle ajoute de la prose, encadre en ` ```json `, change de format d'une fois sur l'autre, renvoie `N/A`… → le pipeline casse en production, silencieusement. Il faut **garantir la forme** de la sortie.

## D — Définition

- **Sortie structurée** : contraindre le LLM à émettre des données conformes à un **schéma** (JSON Schema / **Pydantic**), au lieu de texte libre.
- **Niveaux de garantie** (du plus faible au plus fort) :

| Niveau | Mécanisme | Garantie |
| --- | --- | --- |
| 1. Prompt seul | « réponds en JSON » | **aucune** (le modèle peut dévier) |
| 2. **JSON mode** | `response_format=json_object` | JSON **valide**… mais pas forcément **ton** schéma |
| 3. **Tool / function calling** | arguments typés (JSON Schema) — fiche [02](02-mcp-tool-calling.md) | args validés par le schéma de l'outil |
| 4. **Décodage contraint** | grammaire / `json_schema` / guided decoding | **conforme au schéma, garanti** (le décodeur ne peut pas produire autre chose) |

- **Décodage contraint (constrained/guided decoding)** : au moment de l'inférence, on **restreint les tokens possibles** à ceux qui respectent la grammaire du schéma. C'est le niveau robuste — il se règle côté **serving** ([08](08-serving-inference.md)) : **Ollama** (`format: <json-schema>`), **vLLM** (`guided_json` / Outlines), **llama.cpp** (GBNF). Via le gateway, **LiteLLM** propage `response_format`.
- **Validation + reask** : valider chaque sortie contre le schéma (Pydantic) ; si invalide → **réparer/re-demander** (retry borné) ou escalader.

## S — Solution

1. **Définir le schéma = le contrat** (Pydantic/JSON Schema) : champs **requis**, **types**, **enums** pour les valeurs fermées (classes, statuts), **descriptions** (le modèle les lit).
2. **Choisir le niveau** selon la criticité : décision à enjeu → **décodage contraint** (garanti) ; sinon tool calling / JSON mode **+ validation**.
3. **Valider systématiquement** ; sur échec → **retry borné** puis **fallback/escalade** (jamais laisser passer un objet non conforme).
4. **Séparer** le raisonnement de l'objet final si besoin : chain-of-thought libre **puis** extraction structurée (ou champ `reasoning` + champs stricts).

Bonnes pratiques :
- **enum > chaîne libre** partout où les valeurs sont connues (statut, classe, niveau de risque) ;
- schéma **étroit** et **versionné** ; ne pas surcharger un seul schéma géant ;
- **température basse** (+ `seed`) pour la reproductibilité ([15](15-model-internals.md)) ; réglage complet des paramètres en [27](27-generation-parameters.md) ;
- garder le schéma **proche du code** qui le consomme (une seule source de vérité).

## E — Exemple (DORA)

L'analyse de risque doit renvoyer un **verdict structuré par exigence**, consommé directement par le générateur de rapport et la mise à jour ERP :
```json
{
  "exigence": "droit_audit",
  "statut": "non_conforme",            // enum: conforme | non_conforme | indetermine
  "articles": ["Art.30(2)(a)"],        // pattern vérifié
  "preuve": "La clause 7.2 ne prévoit pas d'accès sur site.",
  "confiance": 0.82                    // 0.0–1.0
}
```
On l'impose par **décodage contraint** sur le modèle local (Ollama `format`) + validation **Pydantic**. Un `statut` hors enum est **impossible** ; un article au mauvais format est **rejeté** → appui direct de l'exigence **« aucune citation d'article inexistante »** ([B4](../sujet/themes/B4-regulatory-compliance.md)). Le [24 — LLM-as-judge](24-llm-as-judge.md) réutilise ce patron pour renvoyer `{verdict, justification, score}`.

**Limite / piège :** le décodage contraint garantit **la forme, pas la vérité** — un JSON conforme peut rester **faux/halluciné** ([17](17-hallucinations.md)). Et **trop contraindre** peut dégrader la qualité (modèle « enfermé »). La structure ne remplace donc ni le grounding (RAG + citations) ni la validation métier.

## Erreurs fréquentes
- **Parser du texte libre** à la regex au lieu d'imposer un schéma.
- Confondre **JSON mode** (JSON valide) et **schema-constrained** (conforme à **ton** schéma).
- **Pas de validation ni de retry** → un output non conforme casse le pipeline en prod.
- Champs en **texte libre** là où un **enum** s'impose (classes, statuts).
- Croire que **structuré = exact** (forme ≠ vérité → toujours grounder/valider).
