# 19 — Compréhension documentaire & multimodalité

> Module 03 — Connecter les données. Le **sous-système d'extraction** que le handbook tenait pour acquis.

## P — Problème

Le RAG ([03](03-rag-data-pipelines.md)) part de « texte ». Mais un contrat réel est un **PDF**, un **scan**, un document avec **mise en page, tableaux, signatures**. « Extraire le texte » est un **pipeline à part entière** — et s'il est mauvais, tout le reste est faux (*garbage in, garbage out*) : chunks incohérents, RAG qui rate les clauses, analyse erronée. C'est souvent **là** que la qualité d'un système « analyse de contrats » se gagne ou se perd.

## D — Définition

- **Document parsing / OCR** : convertir un document (natif ou scanné) en texte exploitable. L'**OCR** gère les images/scans.
- **Layout analysis** : reconstruire la **structure** (titres, sections, colonnes, tableaux) — pas juste un flux de mots.
- **Table extraction** : récupérer les tableaux (SLA, pénalités) en préservant lignes/colonnes.
- **Modèles multimodaux (LMM)** : traitent image + texte (voir [15](15-model-internals.md)).
- **RAG multimodal** : indexer et récupérer de l'image **et** du texte.

## S — Solution : un pipeline d'ingestion documentaire

```
Document → détection type (PDF natif vs scan)
   → OCR si scan → layout analysis (structure) → extraction tableaux
   → chunking structuré (+ n° de page / position)  → embeddings → index   (fiche 03)
```
- **Détecter le type** : PDF texte (extraction directe) vs scan (OCR requis).
- **Préserver la structure** pour un **chunking** sensé ([03](03-rag-data-pipelines.md)) : ne pas couper un tableau en plein milieu.
- **Métadonnées de provenance** (page, position) → **citations vérifiables** ([17](17-hallucinations.md)) : « article 12, page 4 ».
- **Mesurer la qualité d'extraction** comme une métrique ([16](16-evaluation-quantitative.md)) ; signaler les pages à **faible confiance OCR**.
- **Choisir** : OCR classique (rapide, pas cher) vs **modèle multimodal** (meilleur sur mises en page complexes, plus coûteux — arbitrage [09](09-ai-finops.md)).
- **RAG multimodal** si des informations sont **dans l'image** (clause tamponnée, signature, schéma).

### Outils d'extraction (paysage) — *où ils se branchent dans le pipeline*

| Rôle | Outils (OSS d'abord) | Quand l'utiliser |
| --- | --- | --- |
| Parsing texte simple/rapide | **PyMuPDF** (fitz), pdfplumber | PDF **natif** simple, besoin de vitesse |
| **Layout + tableaux + ordre de lecture** | **Docling** (IBM, OSS), **Unstructured**, Marker, LlamaParse | cas **général** : contrats/financiers structurés |
| **OCR** (scans, pas de couche texte) | **Tesseract** (défaut repo), PaddleOCR, Surya | pages **scannées**/images |
| Tableaux pointus | Docling **TableFormer**, Camelot, Tabula | gros tableaux (SLA, financiers) |
| Pages très dures / info dans l'image | **modèle multimodal** (Qwen-VL, Nougat) | schémas, **tampons**, signatures, manuscrit |
| Managé (cloud, **payant**) | Azure Document Intelligence, AWS Textract | prod — **hors** contrainte « 0 € » du lab |

> **Règle de choix (2 temps)** : (1) **couche texte ? → parser direct** (PyMuPDF) ; **scan ? → OCR** (Tesseract) — ne pas OCRiser un PDF qui a déjà son texte. (2) Puis un **parser *layout-aware*** (Docling/Unstructured) pour garder **structure + tableaux + n° de page** (la page est indispensable aux **citations**).
>
> **Défaut conseillé (stack OSS, 0 €) : Docling** — convertit PDF/DOCX/images → **Markdown/JSON** avec layout, tableaux (**TableFormer**), ordre de lecture et OCR optionnel ; s'intègre à **LangChain/LlamaIndex** → se branche dans le service `ingestion`. Dans le repo, `ingestion` part de **tesseract/poppler** ; **Docling/Unstructured** est l'**upgrade naturel** (choix d'architecte à justifier — surtout B4/B10/B14, riches en tableaux).

## E — Exemple (DORA)

Un contrat arrive **scanné** :
1. OCR → texte + **layout** (on identifie la section « sous-traitance critique ») ;
2. **extraction du tableau** de SLA et pénalités en préservant la structure ;
3. chunks enrichis du **n° de page** → RAG ;
4. l'analyse cite « clause 7.3, **page 9** » — citation **vérifiable** par le juriste ([21](21-ux-livraison.md)) ;
5. une page au **scan illisible** (faible confiance OCR) est **signalée** plutôt que traitée en silence.

**Limite / piège :** *garbage in, garbage out*. Un RAG parfait sur un texte mal extrait donne une analyse fausse **avec assurance**. L'extraction est souvent le **vrai goulot qualité**, pas le LLM.

## Erreurs fréquentes
- Supposer que « extraire le texte » est trivial/gratuit.
- OCR sans **layout** → tableaux aplatis, structure perdue, chunks absurdes.
- Pas de **n° de page/position** → citations invérifiables (porte ouverte aux hallucinations [17](17-hallucinations.md)).
- Ne pas mesurer la **qualité d'extraction** ni signaler les pages douteuses.
- Oublier l'info **dans l'image** (signatures, tampons) en ne traitant que le texte.
