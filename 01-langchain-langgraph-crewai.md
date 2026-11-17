# 01 — LangChain vs LangGraph vs CrewAI

> Module 01 — Construire l'intelligence. **La fiche la plus importante du kit.** Pour le cadre conceptuel *un agent ou plusieurs ?*, voir [30 — systèmes multi-agents](30-multi-agent-systems.md).

## P — Problème

Trois frameworks reviennent sans cesse pour construire des applications LLM. On croit souvent devoir « choisir le meilleur ». C'est le mauvais réflexe : ils ne résolvent pas le même problème et se combinent. La vraie question est : **de quelles capacités mon système a-t-il besoin ?**

> 🧭 **Encadré — « assistant » vs « agent » (à clarifier d'abord)**
>
> Avant de choisir un framework, décide **combien d'agentivité** (capacité à agir) ton système requiert — c'est le même esprit que le choix de framework.
>
> | | **Assistant** | **Agent** |
> | --- | --- | --- |
> | Rôle | **aide / répond** (Q&A, RAG) | **planifie, décide et agit** |
> | Comportement | **réactif** (attend une question) | **actif** (utilise des outils, enchaîne des étapes, prend des décisions) |
> | Outils / actions | peu ou pas | **tool calling**, écrit dans des systèmes (ticket, email, base) |
> | Autonomie | faible, humain dans la boucle | variable (semi → autonome) |
>
> **Ce n'est pas binaire** : c'est un **spectre d'agentivité**. Un RAG simple = **assistant** (agentivité faible) ; dès qu'il **appelle des outils, branche, agit** → il devient **agent**.
>
> **En pratique :** « assistant » est le **terme métier** (ce que le client/l'entreprise demande) ; « agent » est **l'implémentation** quand il faut *agir*. Plus l'agentivité requise est élevée, plus on va vers **LangGraph** (état/branches) ou **CrewAI** (équipe d'agents) ; un assistant à faible agentivité reste en **LangChain**. Déterminer ce niveau est **la première décision**.

## D — Définition

| Framework | En une phrase | Métaphore |
| --- | --- | --- |
| **LangChain** | Une boîte de **briques** de haut niveau pour assembler vite LLM + prompts + tools + retrievers + memory + output parsers. | Les Lego. |
| **LangGraph** | Un moteur d'**orchestration** basé sur un graphe d'états : nœuds, transitions, conditions, boucles, interruptions, reprise. | Le chef d'orchestre / la machine à états. |
| **CrewAI** | Un framework **multi-agents** : plusieurs agents aux rôles différents, avec des tâches et des dépendances, collaborent vers un but commun. | Une équipe projet. |

## S — Solution : le critère de choix

```
            De quoi mon système a-t-il besoin ?
                        │
   ┌────────────────────┼─────────────────────────┐
   │                    │                          │
 Assembler des      Workflow stateful,        Équipe d'agents
 briques IA vite    conditions, boucles,      aux rôles distincts
 (LLM, RAG, tools)  reprise, human-in-loop    qui collaborent
   │                    │                          │
 LangChain           LangGraph                   CrewAI
```

### Quand LangChain
- Un seul agent / une chaîne simple : `question → LLM → éventuel tool → réponse`.
- Pas de mémoire complexe, pas de branches conditionnelles lourdes, pas de validation humaine.
- On veut aller vite avec des abstractions prêtes (retrievers, parsers, memory, intégrations).

### Quand LangGraph
- Le problème dominant est **le contrôle du flux et de l'état**.
- Étapes, branches `if/else`, boucles, interruptions, **reprise après crash**, validation humaine au milieu du processus.
- On a besoin de revenir à une étape précédente, de persister l'état, de tracer les transitions.

### Quand CrewAI
- Plusieurs agents **spécialisés** (ex. Researcher, Analyst, Writer) dont le résultat de l'un alimente l'autre.
- Le cœur du besoin est la **collaboration et la répartition des rôles**, pas la mécanique du workflow.
- CrewAI coordonne des agents **dans un même système**. Pour faire collaborer des agents **entre systèmes/équipes/éditeurs** (interopérabilité), c'est le protocole **A2A** → voir [25](25-a2a-interop-agents.md).

### Ils se combinent
- On peut appeler **LangChain à l'intérieur d'un nœud LangGraph** (chaque nœud fait un appel LLM + RAG).
- CrewAI devient pertinent quand l'architecture passe d'« un workflow » à « une équipe d'agents ».

> ⚠️ Piège classique : *« plusieurs agents = CrewAI »*. Faux. Un enchaînement Researcher → Analyst → Writer peut aussi se faire en LangGraph. Le discriminant n'est pas le *nombre* d'agents mais la **nature du problème** (flux/état vs collaboration de rôles).

### 🔧 Code-first vs low-code : et **n8n** ?

Les trois frameworks ci-dessus sont **code-first** (Python). **n8n** est un orchestrateur de workflows **low-code** (nœuds visuels, **400+ connecteurs**, triggers/planification, **nœuds AI Agent**, support **MCP**) — **très demandé en entreprise** pour des workflows IA précis et riches en intégrations.

| | **Code-first** (LangChain/LangGraph/CrewAI) | **Low-code** (n8n) |
| --- | --- | --- |
| Nature | code **versionnable, testable** | **nœuds visuels** + connecteurs |
| Fort pour | logique d'agent **fine**, état complexe, embarqué dans une app, **tests/CI** | **intégrations**, automations, **triggers/planif**, human-in-the-loop visuel, prototypage |
| Contrôle | maximal (état, branches, reprise) | rapide, mais moins granulaire sur la logique complexe |
| IA | frameworks LLM natifs | nœuds *AI Agent* / LangChain + MCP |

**Quand n8n** : workflow **riche en intégrations** (connecteurs, déclencheurs, planifications, notifications) ou **automation métier** à livrer vite. **Ils se combinent** : n8n **déclenche/orchestre** et appelle un **agent code** (via webhook/MCP) pour la logique fine — ou l'inverse.

> 🎓 **Pour apprendre**, on **code** l'agent (LangGraph/CrewAI) afin de comprendre la mécanique (état, outils, reprise) ; n8n est **à connaître** (demande forte) et utile pour la **couche intégration/automation** — mais on ne l'utilise pas pour **esquiver** l'apprentissage de la logique d'agent.

> 📎 **Paysage (on cite, on n'utilise pas ici) :** **LlamaIndex** est une alternative **RAG-first** à LangChain (indexation/retrieval au cœur, [03](03-rag-data-pipelines.md)) — pertinente si le système est **dominé par le RAG** plutôt que par l'orchestration. On reste sur LangChain + LangGraph car le besoin DORA est l'**orchestration stateful**, pas seulement le retrieval.
>
> **PydanticAI** — framework **type-safe** où le modèle **Pydantic *est* le contrat** de l'agent (sortie structurée + validation/retry natifs, [26](26-structured-output.md)). Pertinent quand la **clarté/typage d'un agent simple** prime ; on reste sur LangChain + LangGraph car le besoin DORA est l'**orchestration stateful**, pas un agent isolé.

## E — Exemples (progression du cours)

**Cas 1 — un seul agent, météo.** `question → LLM → éventuel appel API météo → réponse`. Pas de mémoire, pas de branches, pas de validation humaine.
➡️ **LangChain.** Il fournit toutes les briques, on n'a pas besoin de la complexité des deux autres.

**Cas 2 — 3 agents : recherche → analyse → rédaction**, rôles clairs, collaboration vers un rapport.
➡️ **CrewAI** est naturel (rôles + tasks + dépendances). *Mais LangGraph le ferait aussi* — le besoin n'est pas tranché à 100 %.

**Cas 3 — dossier d'assurance stateful.** Extraction → analyse du risque → si risque élevé, validation humaine → sinon continue → rapport ; l'état persiste, on peut revenir en arrière et gérer plusieurs branches.
➡️ **LangGraph.** LangChain devient peu naturel sur du fortement stateful/conditionnel ; CrewAI résout la collaboration, pas le contrôle du flux.

**Cas 4 — plateforme DORA (enterprise).** SharePoint → extraction → RAG DORA → analyse → validation humaine si confiance faible → rapport → base → reprise après interruption.
➡️ **LangChain + LangGraph.** LangChain pour les briques IA (LLM, RAG, tools, structured output) ; LangGraph pour l'orchestration (état, branches, boucles, human-in-the-loop, reprise). **Pas CrewAI** : le besoin n'est pas la collaboration multi-agents.

**Le piège final.** Un collègue : *« Pour notre plateforme enterprise, utilisons CrewAI partout, on aura plusieurs agents donc c'est forcément le meilleur. »*
➡️ Réponse type : *« Pas d'accord. "Plusieurs agents" ne justifie pas CrewAI : notre problème dominant est l'orchestration d'un workflow stateful (branches, reprise, validation humaine), ce que LangGraph fait mieux. CrewAI n'a de valeur que là où des agents aux rôles réellement distincts doivent collaborer — sinon il ajoute de la complexité sans résoudre le vrai besoin. On choisit selon les capacités requises, pas selon le nombre d'agents. »*

## Erreurs fréquentes
- Choisir par popularité (« le meilleur ») au lieu des capacités requises.
- Assimiler « plusieurs agents » à « il faut CrewAI ».
- Mettre du workflow fortement conditionnel dans LangChain « parce qu'on a commencé avec ».
- Oublier qu'ils se composent (LangChain dans LangGraph).
