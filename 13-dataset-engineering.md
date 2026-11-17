# 13 — Dataset Engineering

> Model development. « Data-centric AI » : souvent, améliorer les **données** bat l'amélioration du modèle. (Livre ch. 8)

## P — Problème

La qualité d'un modèle finetuné ([12](12-finetuning.md)) **et** celle d'une évaluation ([16](16-evaluation-quantitative.md)) dépendent entièrement du dataset. Construire de bonnes données est plus difficile que les annoter : il faut définir ce qui est « bon », couvrir la diversité réelle, et éviter les pièges (données synthétiques toxiques, contamination, fuites de PII).

## D — Définition

- **Dataset engineering** : construire le **meilleur dataset possible** (entraînement/finetuning/éval) dans un budget donné.
- **Triade de curation** : **quality · coverage · quantity**.
- **Data augmentation vs synthesis** : dériver du réel (perturbation, back-translation) vs **générer** du neuf (souvent par IA : Alpaca, reverse instruction, self-play).
- **Model distillation** : un petit modèle *student* apprend à imiter un grand *teacher* (ex. DistilBERT, Alpaca).
- **Processing** : inspect → deduplicate → clean & filter → format.

## S — Solution

**Les 3 critères**
- **Quality** : pertinent, cohérent, correctement formaté, unique, **conforme** (pas de PII/toxique/copyright — lien [04](04-securite-gouvernance.md)). Les *guidelines d'annotation* sont les mêmes que les guidelines d'éval ([16](16-evaluation-quantitative.md)).
- **Coverage** : couvrir la diversité des usages réels (domaines, longueurs, styles) ; soigner le *data mix*.
- **Quantity** : dépend de la technique (full vs PEFT), de la complexité de tâche, et du base model ; rendements décroissants.

**Format par usage** : `(instruction, response)` pour SFT ; `(instruction, winning, losing)` pour preference finetuning ; `((instruction,response), score)` pour un reward model.

**Synthèse de données (AI-powered)** : utile pour la quantité, la couverture, la **privacy** et la distillation — **mais toujours vérifiée** (correction fonctionnelle, AI-judge [07](07-llmops-evaluations.md), filtres heuristiques).

**Processing** : **déduplication** (MinHash, Bloom filter ; éviter la contamination train/test), nettoyage (retrait HTML/PII/toxique), **format** conforme au chat template attendu.

**Data flywheel** : les **données applicatives/utilisateur** (lien [14 — User Feedback](14-user-feedback.md)) sont souvent la meilleure source et un avantage concurrentiel durable.

## E — Exemple (DORA)

Pour finetuner le petit modèle « classif de clause » :
1. **Curation** : rassembler des clauses de contrats réelles, annotées (type + risque), couvrant la diversité des fournisseurs et formats.
2. **Synthèse** : générer des variantes de clauses rares (reverse instruction) pour la **couverture**, puis **vérifier** chaque exemple (AI-judge + revue humaine sur un échantillon).
3. **Processing** : dédupliquer (MinHash), **retirer la PII/les données confidentielles**, formater au template attendu.
4. Ce dataset sert **à la fois** au finetuning ([12](12-finetuning.md)) et au jeu d'évaluation ([16](16-evaluation-quantitative.md)).

**Limite / piège :** trop de données **synthétiques non vérifiées** → **model collapse** (le modèle imite ses propres approximations), biais amplifiés et *data lineage* obscur (risque de contamination/copyright). La synthèse accélère, elle ne remplace pas la vérification.

## Erreurs fréquentes
- Optimiser la quantité en négligeant qualité/couverture.
- Données synthétiques non vérifiées → model collapse.
- Pas de déduplication → contamination train/test, évals faussées.
- Oublier PII/conformité dans le dataset (fuite, non-conformité).
- Réutiliser un dataset dont on ignore la provenance (lineage/copyright).
