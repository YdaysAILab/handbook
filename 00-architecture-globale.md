# 00 — Architecture globale d'une plateforme IA d'entreprise

> Fiche de cadrage. Elle situe toutes les autres fiches les unes par rapport aux autres.

## P — Problème

Une simple API LLM (`prompt → réponse`) ne suffit pas en entreprise. Dès qu'on veut un assistant **fiable, sécurisé, connecté aux données internes et exploitable à grande échelle**, on fait face à une dizaine de problèmes distincts qui n'ont pas la même solution :

- le modèle n'a pas accès aux documents internes → **RAG** ;
- il doit agir sur des systèmes (SharePoint, GLPI, base de données) → **MCP / tool calling** ;
- il doit suivre un processus métier avec étapes, conditions et validation humaine → **orchestration (LangGraph)** ;
- il ne doit pas fuiter de données ni halluciner sans contrôle → **guardrails / IAM / gouvernance** ;
- 20 applications consomment plusieurs fournisseurs LLM → **AI Gateway** ;
- on doit savoir ce qui se passe et prouver la qualité → **observabilité + évaluations** ;
- il faut maîtriser les coûts GPU/tokens → **serving + FinOps**.

## D — Définition

Une plateforme IA d'entreprise est un **empilement de couches** où chaque technologie résout **un** problème précis, et où les contrôles transversaux (sécurité, observabilité, coûts) s'appliquent à **chaque frontière**.

## S — Solution : les couches

```
            Utilisateurs / Applications
                       │
          Authentification · API Gateway        ← qui a le droit d'appeler ?
                       │
   ┌───────────────────┴────────────────────┐
   │  Agent / Workflow — LangGraph + LangChain │   ← le cerveau : état, raisonnement, tools
   └───────┬───────────────┬──────────────┬───┘
           │               │              │
          RAG          AI Gateway        MCP
     connaissances    routage/coûts    actions sur les systèmes
           │               │              │
   ────────┴───────────────┴──────────────┴────────
   Transverses : IAM · Guardrails · Governance · Observability · LLMOps · FinOps
```

| Couche | Rôle | Fiche |
| --- | --- | --- |
| Build | Intelligence : LLM, chaînes, agents, orchestration | [01](01-langchain-langgraph-crewai.md) |
| Connect | Brancher l'agent aux systèmes | [02](02-mcp-tool-calling.md) |
| Data | Donner des connaissances fiables | [03](03-rag-data-pipelines.md) |
| Secure | IAM, permissions, guardrails, audit | [04](04-securite-gouvernance.md) |
| Route | Routage multi-modèles, quotas, fallbacks | [05](05-ai-gateway-routing.md) |
| Observe | Traces, métriques, debugging | [06](06-observabilite.md) |
| Evaluate / Operate | Évals, quality gates, CI/CD, fiabilité | [07](07-llmops-evaluations.md) |
| Serve | vLLM, GPU, inference | [08](08-serving-inference.md) |
| Optimize | Coûts, routage, gouvernance du cycle de vie | [09](09-ai-finops.md) |

## E — Exemple (fil rouge DORA)

> *« Analyse ce contrat fournisseur et dis-moi s'il présente un risque DORA. »*

Le système doit : récupérer le contrat depuis SharePoint → extraire le texte → chercher les exigences DORA pertinentes dans une base documentaire → analyser le contrat → si la confiance est faible, demander une validation humaine → sinon, générer le rapport → enregistrer en base → pouvoir reprendre après une interruption.

Chaque verbe de ce scénario pointe vers une couche :

| Besoin du scénario | Couche / techno |
| --- | --- |
| « récupérer depuis SharePoint », « enregistrer en base » | MCP / tool calling |
| « chercher les exigences DORA » | RAG |
| « analyser le contrat » | LLM via LangChain |
| « si confiance faible → validation humaine », « reprendre après interruption » | LangGraph (état + branches + human-in-the-loop) |
| « document confidentiel », « droits de l'utilisateur » | IAM / guardrails / ACL |
| « 20 applis, plusieurs modèles » | AI Gateway |
| « prouver la qualité », « coûts » | Évals / Observabilité / FinOps |

**Limite à retenir :** on n'a pas *besoin* de CrewAI ici. Le problème dominant est l'orchestration d'un workflow stateful, pas la collaboration entre agents aux rôles distincts. CrewAI ne devient pertinent que si l'architecture évolue vers une **équipe** (Researcher → Risk Agent → Reviewer).
