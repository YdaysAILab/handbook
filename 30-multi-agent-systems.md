
# 30 — Systèmes multi-agents (MAS)

> Module 01 — Construire l'intelligence. Le **cadre conceptuel** derrière le choix de framework ([01](01-langchain-langgraph-crewai.md)) et l'interop ([25](25-a2a-interop-agents.md)) : *un agent ou plusieurs ?*

## P — Problème

Face à une tâche complexe (ex. analyser un contrat fournisseur sous l'angle DORA), le réflexe est de demander à **un seul** agent de tout faire : chercher les exigences, lire le contrat, juger clause par clause, rédiger le rapport. Ça marche… jusqu'à ce que le prompt devienne ingérable, que les responsabilités se mélangent, et qu'on ne sache plus *pourquoi* une conclusion est sortie. L'autre réflexe — « multiplions les agents » — est tout aussi piégeux : **plus d'agents ≠ plus intelligent**. C'est plus lent, plus cher ([fiche 09](09-ai-finops.md)) et plus dur à déboguer. La vraie question n'est pas « combien d'agents » mais **la tâche bénéficie-t-elle de rôles de décision distincts ?**

## D — Définition

Un **système multi-agents (MAS)** est une architecture où **plusieurs agents autonomes** collaborent (ou se challengent) vers un but commun, chacun **spécialisé** sur une sous-tâche, avec ses outils et sa capacité de décision. On **distribue les responsabilités** au lieu de tout confier à un modèle unique.

|                  | **Agent unique** | **Multi-agents (MAS)**                          |
| ---------------- | ---------------------- | ----------------------------------------------------- |
| Responsabilités | un agent fait tout     | un rôle distinct par agent                           |
| Coordination     | simple                 | nécessite une **orchestration** inter-agents   |
| Débogage        | plus facile            | plus dur à observer ([fiche 06](06-observabilite.md)) |
| Exécution       | séquentielle          | **parallélisme** possible                      |
| Coût / latence  | plus bas               | **plus élevé** (multi-appels)                 |
| Bon pour         | workflows ciblés      | workflows **complexes, décomposables**         |

> ⚠️ Un **agent n'a pas forcément besoin d'un LLM** : un MAS peut mêler agents LLM et agents à règles/algorithmes.

**Les composants d'un MAS :** (1) **agents** qui raisonnent et agissent ; (2) **LLM** fournissant le raisonnement ; (3) **outils** (APIs, bases, MCP — [fiche 02](02-mcp-tool-calling.md)) ; (4) **mémoire/état** partagé ou privé ([fiche 10](10-memory.md)) ; (5) **communication** (messages, événements, état partagé) ; (6) **orchestration** (délégation, dépendances) ; (7) **garde-fous & évaluation** ([fiches 04](04-securite-gouvernance.md) / [24](24-llm-as-judge.md)).

### MAS ≠ microservices (le piège d'ingénieur)

Un **microservice** est une unité de **déploiement** logiciel. Un **agent** est une unité de **décision/action**. Un agent **vit dans** un microservice, et **plusieurs agents peuvent tourner dans le même service**. → On ne crée **pas** un Deployment Kubernetes par agent : on démarre avec **un service, plusieurs agents logiques**, et on ne scinde que si le scaling, l'isolation ou la propriété l'exigent.

## S — Solution : choisir l'architecture

Plusieurs façons d'organiser la collaboration — du plus simple au plus structuré :

| Architecture                | Fonctionnement                                  | Bon pour                             |
| --------------------------- | ----------------------------------------------- | ------------------------------------ |
| **Séquentielle**     | A → B → C                                     | pipelines de traitement documentaire |
| **Superviseur**       | un agent central délègue aux spécialistes    | assistants d'entreprise              |
| **Hiérarchique**     | des superviseurs pilotent des équipes d'agents | workflows larges et complexes        |
| **Décentralisée**   | les agents collaborent directement              | résolution distribuée              |
| **Débat / critique** | les agents évaluent/challengent les sorties    | décisions à fort enjeu             |

**Intra-système**, un MAS se code avec **CrewAI** (équipe de rôles) ou **LangGraph** (état/branches) — [fiche 01](01-langchain-langgraph-crewai.md). **Au-delà d'une frontière** (autre équipe/éditeur/runtime), on passe par **A2A** — [fiche 25](25-a2a-interop-agents.md).

> 📎 **Paysage (on cite, on n'utilise pas ici) :** **AG2** (ex-**AutoGen**) est une alternative multi-agents à CrewAI, orientée **conversation entre agents** et **human-in-the-loop**. On reste sur CrewAI/LangGraph pour la cohérence du kit ; le **choix se fait sur la capacité requise**, pas sur la marque.

> **Stratégie de montée en complexité :** *agent unique → agent + outils → agents spécialisés → orchestration multi-agents*. On n'ajoute un niveau **qu'après avoir mesuré** le bénéfice. Pour un workflow **déterministe**, du **code ordinaire** est plus fiable qu'un agent ([fiche 22](22-decision-amont.md)).

> **Décision à fort enjeu :** l'IA **recommande**, l'humain autorisé (ou un process métier validé) **décide**. Jamais un verdict de conformité auto-appliqué.

## E — Exemple (DORA)

L'analyse d'un contrat fournisseur sous DORA se décompose naturellement en **rôles** → MAS en **superviseur** :

```
                 Contrat + politique DORA
                            │
                    Agent Superviseur
            (planifie, délègue, agrège, supervise)
         ┌──────────┬───────────────┬─────────────┐
      Researcher   Analyst         Reviewer      (humain)
      exigences    conformité      critique       valide
      DORA (RAG)   clause/clause   du verdict     le rapport
                            │
            Rapport consolidé (cité, traçable, audit-ready)
```

Le **Researcher** retrouve les exigences applicables (droit d'audit, réversibilité…) via RAG ([fiche 03](03-rag-data-pipelines.md)) ; l'**Analyst** confronte le contrat exigence par exigence et produit un verdict **schématisé** ([fiche 26](26-structured-output.md)) ; le **Reviewer** challenge (pattern **débat/critique**) pour attraper les écarts ; le **juriste** reste décideur. Chaque agent garde sa logique et appelle ses propres outils via **MCP** ; le passage de relais suit un contrat d'échange clair ([fiche 25](25-a2a-interop-agents.md)). On parallélise le Researcher sur plusieurs exigences → gain de latence.

**Limite / piège :** le brief projet impose **1 à 4 agents** et un **framework justifié** (voir [`sujet/BRIEF.md`](../sujet/BRIEF.md)). Un agent unique bien outillé suffit souvent pour un seul contrat ; le MAS ne se justifie **que** si la décomposition en rôles améliore réellement l'exactitude ou la traçabilité — et il faut alors **mesurer** le surcoût en latence/tokens.

## Erreurs fréquentes

- Croire qu'un MAS est **par nature** plus intelligent ou plus efficace qu'un agent unique — il est surtout plus **coûteux et complexe**.
- Introduire des agents pour un workflow **déterministe** → du code ordinaire serait plus fiable ([fiche 22](22-decision-amont.md)).
- Confondre **agent** (unité de décision) et **microservice** (unité de déploiement) → un Deployment par agent, inutilement.
- Laisser un agent (ou le MAS) **décider** une action à fort enjeu au lieu de **recommander** à un humain autorisé.
- Sauter les étapes : partir direct en multi-agents sans avoir épuisé *agent + outils* ni **mesuré** le bénéfice.
- Négliger l'**observabilité** : sans trace de bout en bout, un MAS devient une boîte noire indéboguable ([fiche 06](06-observabilite.md)).
