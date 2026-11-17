# 20 — Déploiement & fiabilité en prod (SRE pour l'IA)

> Module 05 — Déployer et fiabiliser. Complète la fiche [07](07-llmops-evaluations.md) : **comment** déployer un changement sans casser la prod, et **survivre aux pannes**.

## P — Problème

Changer un prompt, un modèle ou le RAG en production est **risqué** : le système est non déterministe, une « amélioration » peut régresser silencieusement. Et le système **dépend de fournisseurs** qui tombent (rate limit, panne). La fiche 07 donne les *quality gates* et l'idempotence ; il manque le **déploiement sûr** et la **dégradation gracieuse**.

## D — Définition

- **Shadow deployment** : la nouvelle version tourne **en parallèle** sur du trafic réel, **sans impacter** l'utilisateur ; on compare.
- **Canary** : exposer la nouvelle version à un **petit %** d'abord, surveiller, puis élargir.
- **A/B / blue-green** : router une fraction d'utilisateurs ; bascule/rollback instantané.
- **Rollback** : revenir à la version précédente **immédiatement**.
- **Incident response** : détecter (MTTD), réparer (MTTR), apprendre ; **kill switch**, runbook.
- **Graceful degradation** : continuer à fonctionner **en mode dégradé** quand une dépendance est down.

## S — Solution

**Déployer sûrement**
- **Versionner** modèles **et** prompts ([11](11-prompt-engineering.md)) ; tout changement est une version traçable ([18](18-gouvernance-conformite.md)).
- **Quality gate avant** ([07](07-llmops-evaluations.md)) → **shadow** (comparer sans risque) → **canary** (5 %) → 100 %, avec **monitoring après** ([06](06-observabilite.md)).
- **Rollback** en un geste si les métriques se dégradent.

**Survivre aux pannes (graceful degradation)**
- **Fournisseur LLM down** → **fallback** via l'AI Gateway ([05](05-ai-gateway-routing.md)) vers un autre modèle.
- **Tout l'IA indisponible** → mode dégradé : file d'attente, réponse déterministe, ou **escalade humaine** plutôt qu'une erreur brute.
- **Retries/timeouts/idempotence** ([07](07-llmops-evaluations.md)) pour absorber les erreurs transitoires sans doublons.

**Réagir aux incidents**
- **Alertes** sur les métriques clés ([06](06-observabilite.md)), **kill switch** si l'agent dérive, **runbook** (qui fait quoi), post-mortem.

## E — Exemple (DORA)

- Nouveau modèle d'analyse → déployé en **shadow** sur des contrats réels, comparé au modèle en place ; s'il bat l'ancien sur les évals ([16](16-evaluation-quantitative.md)) → **canary 5 %** → 100 %.
- Le fournisseur LLM tombe → le **Gateway bascule** vers le modèle interne ; s'il n'y a plus rien → l'agent met la demande en file et **prévient le juriste** (pas d'erreur silencieuse).
- Dérive détectée (verdicts incohérents) → **kill switch** + rollback, incident journalisé pour l'audit.

**Limite / piège :** en conformité, un rollback ou un mode dégradé doit rester **traçable** ([18](18-gouvernance-conformite.md)) — on doit pouvoir expliquer *quelle version* a produit *quelle décision*.

## Erreurs fréquentes
- Déployer un changement de prompt/modèle **directement en prod** sans shadow/canary.
- Pas de **rollback** rapide → un incident dure des heures.
- Aucune **dégradation gracieuse** → une panne fournisseur casse tout.
- Pas de **kill switch** ni de runbook → panique en incident.
- Changements non **versionnés** → impossible de savoir ce qui a régressé.
- Valider **à 1 utilisateur** et supposer que ça tient **sous charge** (concurrence + isolation des sessions) → voir [29](29-multi-user-sessions.md).
