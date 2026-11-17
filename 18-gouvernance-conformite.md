# 18 — Gouvernance IA & conformité réglementaire

> Couche **transversale** (organisationnelle/réglementaire). Distincte de la sécurité technique ([04](04-securite-gouvernance.md)) : ici on gouverne **l'IA elle-même** face à un régulateur.

## P — Problème

Tout le fil rouge est un assistant **de conformité (DORA)** — mais le système IA doit lui-même **être conforme et gouvernable**. Sans cela : non-conformité **EU AI Act / DORA / RGPD**, décisions non traçables, et personne pour **répondre** d'une décision de l'IA devant un auditeur. La fiche 04 sécurise l'accès ; celle-ci répond à *« qui est responsable, comment le prouve-t-on, et a-t-on le droit ? »*.

## D — Définition

| Notion | Rôle |
| --- | --- |
| **Classification de risque (EU AI Act)** | Niveaux : inacceptable / **haut risque** / risque limité / minimal → obligations proportionnées. |
| **DORA** | Résilience opérationnelle numérique ; encadre la **sous-traitance TIC critique** (un fournisseur IA en fait partie). |
| **RGPD** | Données personnelles : base légale, minimisation, droits des personnes. |
| **Model card / documentation** | Fiche décrivant le modèle : usage prévu, limites, données, performances — exigible par un régulateur. |
| **Data lineage** | Traçabilité : d'où viennent les données (entraînement, RAG) et ce qui a nourri **chaque décision**. |
| **Human oversight** | Supervision humaine **obligatoire** sur les systèmes à haut risque. |
| **Accountability** | Un propriétaire nommé, une chaîne de responsabilité claire. |

## S — Solution

1. **Classer le système** : un assistant qui évalue le risque DORA d'un contrat est probablement **haut risque** → obligations : documentation, supervision humaine, journalisation, robustesse, transparence.
2. **Documenter** : **model cards** + documentation système (usage prévu, limites connues, taux d'erreur mesurés via [16](16-evaluation-quantitative.md)).
3. **Tracer** : **data lineage** de bout en bout + **audit trail** ([04](04-securite-gouvernance.md), [06](06-observabilite.md)) exploitable par un auditeur (qui, quoi, sur quelle donnée, quelle source).
4. **Garder l'humain** : décision finale **humaine** sur les cas à enjeu (human-in-the-loop, [21](21-ux-livraison.md)) ; l'IA **recommande**, elle ne tranche pas seule.
5. **Nommer un responsable** : accountability — un owner répond des décisions de l'IA.
6. **Cycle de vie des données** : **rétention**, **droit à l'oubli**, **data residency** (où sont stockées les données, combien de temps, dans quelle juridiction).
7. **Minimisation des PII** : anonymiser les données personnelles avant tout traitement externe → [23 — Protection des PII](23-pii-anonymisation.md).

### Cadres de référence & piliers opérationnels (*enterprise builder*)

**Les 3 cadres à connaître** — on *mappe* le système dessus (comme l'OWASP LLM Top 10 côté sécurité, [28](28-securite-llm-threats.md)) :

| Cadre | Nature | Apport |
| --- | --- | --- |
| **EU AI Act** | **obligatoire** (UE) | classe par **niveau de risque** (inacceptable / **haut** / limité / minimal) + **évaluation de conformité** ; un assistant d'analyse de risque = probablement **haut risque** |
| **NIST AI RMF** | **volontaire** (référentiel) | 4 fonctions **Govern · Map · Measure · Manage** — identifier/atténuer le risque sur **tout le cycle de vie** |
| **ISO/IEC 42001** | **certifiante** | établit un **SMIA** (système de management de l'IA) **auditable** |

**Les 5 piliers à implémenter au niveau plateforme** (communs à tous les produits, pas refaits par cas d'usage) :

1. **AI Asset Registry** — inventaire centralisé des **modèles, agents, pipelines** (savoir ce qui tourne, et dans quelle version).
2. **Model cards + data lineage** — provenance, limites, preuves de vérification → **rejouer « pourquoi cette décision »** (cf. S.2-S.3).
3. **Contrôles plateforme** — accès (ACL/OPA), **limites d'action des agents** (moindre privilège), gestion des prompts, **surveillance des sorties** (anti-hallucination/fuite PII) : le mur commun ([04](04-securite-gouvernance.md)/[05](05-ai-gateway-routing.md)/[28](28-securite-llm-threats.md)).
4. **Stage-gates / quality gates** — tests **biais / sécurité / conformité obligatoires avant prod** (en CI, [07](07-llmops-evaluations.md)) : rien ne passe sans franchir la porte.
5. **Human-in-the-loop** — supervision humaine sur les décisions à enjeu (cf. S.4).

> **Distinction clé** : les **cadres** disent *quoi prouver* (et à qui) ; les **piliers** sont *comment* on l'implémente dans la plateforme. La gouvernance se **mappe** (EU AI Act / NIST AI RMF / ISO 42001) **et** se **prouve** (registry + cards + lineage + gates + audit).

## E — Exemple (DORA)

L'assistant **ne décide pas seul** : il produit une **recommandation documentée** (verdict + articles cités + confiance). Chaque recommandation est **traçable** (data lineage : quelles sources/versions de modèle), **revue par un juriste responsable**, et **journalisée** pour un audit. Une **model card** décrit les limites (« ne remplace pas une analyse juridique ») et les données utilisées. La rétention des contrats et des logs respecte RGPD + la politique de data residency.

**Limite / piège :** la gouvernance **n'est pas qu'un document** — c'est un processus vivant (revue, mise à jour, réévaluation). Et la conformité ne **remplace pas** la qualité : un système conforme mais mauvais reste inutile.

## Erreurs fréquentes
- Confondre sécurité technique ([04](04-securite-gouvernance.md)) et gouvernance réglementaire.
- Automatiser une décision à enjeu sans supervision humaine (interdit en haut risque).
- Pas de data lineage → impossible de prouver *pourquoi* l'IA a conclu ainsi.
- Model card absente ou obsolète.
- Ignorer rétention / droit à l'oubli / data residency jusqu'au premier audit.
- Personne de nommé comme **responsable** des décisions de l'IA.
- Pas d'**inventaire** (AI Asset Registry) → **shadow AI** non gouvernée ; pas de **stage-gate** → un modèle part en prod sans test biais/sécurité/conformité.
- Traiter la gouvernance comme **purement locale** à un produit, au lieu de **cadres mappés** (EU AI Act / NIST AI RMF / ISO 42001) + **piliers plateforme** réutilisés.
