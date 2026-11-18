# Handbook — Ingénierie des plateformes IA d'entreprise

Kit de fiches de référence pour concevoir, construire, sécuriser et opérer une plateforme IA d'entreprise. Chaque fiche est autonome mais renvoie aux autres ; commencez par la [fiche 00 — Architecture globale](00-architecture-globale.md) pour le cadrage d'ensemble.

## Comment lire ce kit

Les fiches sont organisées par phase du cycle de vie (« modules »), avec des couches **transversales** qui s'appliquent partout :

- **Module 00 — Décision amont** : faut-il construire ?
- **Module 01 — Construire l'intelligence** : frameworks, prompts, mémoire, fondamentaux des modèles.
- **Module 02 — Connecter les systèmes** : MCP, tool calling, interopérabilité agent↔agent.
- **Module 03 — Connecter les données** : RAG, pipelines, compréhension documentaire.
- **Module 04 — Sécuriser & gouverner** : contrôles, menaces, conformité, PII.
- **Module 05 — Déployer & fiabiliser** : gateway, observabilité, LLMOps, évaluations, SRE.
- **Module 06 — Optimiser & faire évoluer** : FinOps, feedback utilisateur, UX.

## Index des fiches

### Cadrage
- [00 — Architecture globale](00-architecture-globale.md)
- [22 — Décision amont : faut-il seulement construire ça ?](22-decision-amont.md)

### Construire l'intelligence
- [01 — LangChain vs LangGraph vs CrewAI](01-langchain-langgraph-crewai.md)
- [10 — Memory (mémoire des agents)](10-memory.md)
- [11 — Prompt Engineering](11-prompt-engineering.md)
- [15 — Fondamentaux des modèles (Foundation Model Internals)](15-model-internals.md)
- [26 — Sortie structurée (structured output)](26-structured-output.md)
- [27 — Paramètres de génération (decoding / sampling)](27-generation-parameters.md)
- [30 — Systèmes multi-agents (MAS)](30-multi-agent-systems.md)

### Connecter les systèmes
- [02 — MCP & Tool Calling](02-mcp-tool-calling.md)
- [25 — A2A & interopérabilité multi-agents](25-a2a-interop-agents.md)

### Connecter les données
- [03 — RAG & Data Pipelines](03-rag-data-pipelines.md)
- [19 — Compréhension documentaire & multimodalité](19-document-understanding.md)

### Sécuriser & gouverner
- [04 — Sécurité & Gouvernance](04-securite-gouvernance.md)
- [18 — Gouvernance IA & conformité réglementaire](18-gouvernance-conformite.md)
- [23 — Protection des PII & anonymisation (gateway egress)](23-pii-anonymisation.md)
- [28 — Sécurité des systèmes IA (OWASP LLM Top 10 & threat model)](28-securite-llm-threats.md)

### Déployer & fiabiliser
- [05 — AI Gateway & Model Routing](05-ai-gateway-routing.md)
- [06 — Observabilité](06-observabilite.md)
- [07 — LLMOps, Évaluations & Fiabilité](07-llmops-evaluations.md)
- [08 — Serving & Inference](08-serving-inference.md)
- [16 — Évaluation quantitative (métriques & ranking)](16-evaluation-quantitative.md)
- [17 — Gérer les hallucinations](17-hallucinations.md)
- [20 — Déploiement & fiabilité en prod (SRE pour l'IA)](20-deploiement-fiabilite.md)
- [24 — LLM-as-Judge](24-llm-as-judge.md)
- [29 — Multi-utilisateur, concurrence & isolation des sessions](29-multi-user-sessions.md)

### Model development
- [12 — Finetuning & adaptation des modèles](12-finetuning.md)
- [13 — Dataset Engineering](13-dataset-engineering.md)

### Optimiser & faire évoluer
- [09 — AI FinOps](09-ai-finops.md)
- [14 — User Feedback](14-user-feedback.md)
- [21 — UX produit & livraison](21-ux-livraison.md)

## Cours & séances

- [**SDK natif ou framework ?** (séance 18.11.2025)](cours-sdk-vs-framework-18.11.2025/01-cas-pratiques-apprenants.md) — cas pratiques de décision d'outillage (SDK natif / LangChain / LangGraph / CrewAI / n8n). Prolonge la [fiche 01](01-langchain-langgraph-crewai.md). *Corrigé instructeur (ne pas distribuer) : [`02-corrige-instructeur.md`](cours-sdk-vs-framework-18.11.2025/02-corrige-instructeur.md).*

---

*Dépôt interne — YdaysAILab.*
