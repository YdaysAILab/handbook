# 25 — A2A & interopérabilité multi-agents

> Module 02 — Connecter les systèmes (volet **agent↔agent**). Complément de [02 — MCP](02-mcp-tool-calling.md), de [01 — frameworks/CrewAI](01-langchain-langgraph-crewai.md) et de [30 — systèmes multi-agents](30-multi-agent-systems.md) (intra-système).

## P — Problème

Dans une grande organisation, les agents ne vivent pas tous dans le **même** processus : l'agent DORA (équipe Conformité) peut avoir besoin de **déléguer** une sous-tâche à un agent « veille juridique » d'une **autre équipe**, bâti avec un **autre framework**, voire un **autre éditeur**. CrewAI/LangGraph coordonnent des agents **à l'intérieur** d'un système ; mais **entre systèmes/organisations**, il faut un **protocole standard** pour que les agents collaborent **sans connaître leur logique interne**.

## D — Définition

- **A2A (Agent2Agent)** : protocole **ouvert** de communication **entre agents** (couche **horizontale**). Gouvernance : **Agentic AI Foundation** (Linux Foundation), aux côtés de MCP.
- **Agent Card** : métadonnées (JSON) décrivant les **capacités, skills et endpoints** d'un agent → permet la **découverte**.
- **Tasks / messages / artifacts** : un agent délègue une **task**, échange des **messages**, reçoit des **artifacts** (résultats).

### La distinction clé (à retenir)

| | **MCP** ([02](02-mcp-tool-calling.md)) | **A2A** |
| --- | --- | --- |
| Relie | agent ↔ **outils / données** (vertical) | agent ↔ **agent** (horizontal) |
| Analogie | « USB » vers les systèmes | « téléphone » entre agents |
| Exemple | lire SharePoint, créer un ticket | déléguer une sous-tâche à un autre agent |

> **Pattern de production :** **MCP entre un agent et ses outils**, **A2A entre agents**. Les deux sont complémentaires, pas concurrents.

## S — Solution

- **Exposer un agent** via une **Agent Card** (capacités + endpoint) → les autres agents le **découvrent**.
- **Déléguer** une tâche à un agent distant via A2A (task → messages → artifact), **sans couplage** à son implémentation.
- **Quand l'utiliser** :
  - **intra-système** (un seul projet, agents du même framework) → **CrewAI/LangGraph** suffisent ([01](01-langchain-langgraph-crewai.md)), **pas besoin d'A2A**.
  - **au-delà d'une frontière** (autre équipe, autre éditeur, autre runtime) → **A2A** apporte l'interopérabilité standard.
- **Sécurité & gouvernance** : identité et **autorisation entre agents** (qui a le droit de déléguer quoi, au nom de qui), **audit** — mêmes principes que [04](04-securite-gouvernance.md). ⚠️ les protocoles d'interop **n'expriment pas tout** (politique, responsabilité) : la gouvernance reste à ta charge.

## E — Exemple (DORA)

L'assistant DORA doit vérifier une **jurisprudence récente** maintenue par un agent « Veille juridique » d'une autre direction. Plutôt que de réimplémenter cette capacité, il **découvre** cet agent via son **Agent Card**, lui **délègue une task** (« jurisprudence sur le droit d'audit TIC, 2026 »), et reçoit un **artifact** cité. Chaque agent **garde sa logique interne** ; seule l'interface A2A est partagée. En interne, chaque agent continue d'utiliser **MCP** pour ses propres outils (SharePoint, base DORA).

**Limite / piège :** standard **récent** (passé sous Linux Foundation en 2026) — maturité à vérifier. Et surtout, **over-engineering** : si tous tes agents sont dans **un seul** système, **CrewAI/LangGraph suffisent** ; A2A n'a de valeur que lorsqu'on **franchit une frontière** organisationnelle/éditeur. La **sécurité inter-agents** doit être cadrée explicitement.

## Erreurs fréquentes
- Confondre **A2A** (agent↔agent) et **MCP** (agent↔outils) — ils sont **complémentaires**.
- Introduire A2A là où **CrewAI/LangGraph** suffisent (un seul système) → complexité inutile.
- Déléguer à un agent distant **sans autorisation ni audit** (fiche 04).
- Croire qu'un protocole d'interop règle la **gouvernance** (responsabilité, politique) — il ne l'exprime pas.
