# 10 — Memory (mémoire des agents)

> Module 01 — Construire l'intelligence. Capacité **transversale au Build** : conditionne le choix de framework et se combine avec RAG et l'état LangGraph.

## P — Problème

Un LLM est **sans état (stateless)** : chaque appel API ignore tout des précédents. Tout ce qu'il « sait » d'une conversation tient dans le **contexte** qu'on lui renvoie à chaque tour. Deux limites concrètes :
1. le **contexte a une taille finie** (fenêtre de tokens) et un coût qui croît avec sa longueur → on ne peut pas tout réinjecter indéfiniment ;
2. rien ne persiste **entre deux sessions** : l'agent DORA « oublie » qu'un juriste a déjà validé un contrat la semaine dernière, ou ses préférences de format.

La mémoire est ce qui transforme un *appel LLM* en *agent* capable de continuité.

## D — Définition

La **mémoire** = les mécanismes qui décident **quoi retenir, où le stocker, et quoi réinjecter** dans le contexte au bon moment.

| Type | Horizon | Contenu | Où ça vit |
| --- | --- | --- | --- |
| **Short-term / working** | la session en cours | historique de conversation, variables de travail, état du workflow | buffer / état LangGraph |
| **Long-term** | entre sessions | faits durables, décisions passées, préférences | store externe (souvent vectoriel) |
| **Semantic** | durable | faits/connaissances (« ce fournisseur est critique ») | base de faits / vector store |
| **Episodic** | durable | événements passés (« le 03/10, l'analyste a rejeté la clause 4 ») | log / vector store |
| **Procedural** | durable | savoir-faire appris, instructions récurrentes | prompts/outils, parfois fine-tuning |

### Ne pas confondre — mémoire vs contexte vs RAG

- **Contexte (context window)** = l'espace de tokens d'un appel. C'est le « bureau », pas la mémoire.
- **Mémoire** = ce qui **choisit** ce qu'on pose sur le bureau à chaque tour (et le fait persister).
- **RAG** ([03](03-rag-data-pipelines.md)) récupère des **connaissances documentaires** (des documents de référence). La mémoire récupère **l'historique propre à l'utilisateur/à la conversation**. Techniquement proches (souvent un vector store), **finalité différente** : RAG = « ce que l'organisation sait », mémoire = « ce qu'il s'est passé avec cet utilisateur ».

## S — Solution

Trois décisions à prendre :

**1. Short-term : gérer l'historique de conversation**
- **buffer** : réinjecter les N derniers tours (simple, mais grossit vite) ;
- **summarization** : résumer les anciens tours pour tenir dans la fenêtre (compromis coût/fidélité) ;
- **working state** : dans **LangGraph**, l'état du graphe EST la mémoire de travail du workflow — et sa **persistance (checkpointer)** permet la **reprise après interruption** (voir [07](07-llmops-evaluations.md)).

**2. Long-term : persister au-delà de la session**
```
Fin de tour → extraire les faits à retenir → FILTRE d'admission → écrire dans un store (vectoriel + métadonnées)
Début de tour → requête → récupérer les souvenirs pertinents → injecter dans le prompt
```
- **Filtre d'admission** (opérationnalise « mémoriser *sélectivement* ») : n'écrire un candidat que s'il est **durable** (utile au-delà de cette session), **réutilisable** (influence de futures décisions) **et** **sûr** (pas de PII/secret → détection au write, [23](23-pii-anonymisation.md)). Un fait « juste pour cette session » reste en **working memory**, pas en long-terme.
- **Écriture asynchrone** : persister la mémoire **ne doit pas bloquer** l'agent (écrire hors du chemin critique de la réponse).
- scoper **par utilisateur / par tenant** (clé d'isolation) ;
- des stores dédiés existent (type *mem0*, ou un vector store maison) ; côté frameworks, LangChain/LangGraph exposent des abstractions de mémoire, CrewAI gère une mémoire par équipe/agent.

**3. Gouvernance de la mémoire (critique en entreprise)**
- **isolation stricte par utilisateur** : la mémoire de l'un ne doit jamais fuiter vers l'autre — **y compris sous concurrence** (clé de scope, pas d'état de process partagé → [29](29-multi-user-sessions.md)) ;
- **ACL & confidentialité** : la mémoire peut contenir des données sensibles → mêmes règles que [04](04-securite-gouvernance.md) (masquage, rétention, droit à l'oubli) ;
- **expiration/rétention** : ne pas garder indéfiniment ; définir une durée de vie ;
- **memory poisoning** (menace, voir [28](28-securite-llm-threats.md)) : une **injection** peut planter un **faux souvenir persistant** qui détourne les sessions **futures** (l'injection survit au-delà d'une requête). Défense : **valider ce qui est écrit** en mémoire (ne pas mémoriser du contenu non fiable tel quel), isoler, et pouvoir **auditer/corriger/effacer** un souvenir.

### Lien avec le choix de framework ([01](01-langchain-langgraph-crewai.md))

- Besoin de mémoire **simple** (historique de conversation) → **LangChain** suffit.
- Besoin de mémoire **de travail persistante** avec reprise/branches → l'**état LangGraph** est la bonne primitive.
- Mémoire **partagée entre agents** collaborant → gérée côté **CrewAI**.

## E — Exemple (DORA)

1. **Short-term** : pendant l'analyse d'un contrat, l'agent garde en mémoire de travail le texte extrait, les articles DORA récupérés et les scores intermédiaires — c'est l'**état LangGraph**. Si le processus est interrompu (validation humaine en attente, crash), le **checkpoint** permet de **reprendre** exactement là où on s'était arrêté, sans tout rejouer.
2. **Long-term / episodic** : l'agent se souvient que *ce fournisseur* a déjà fait l'objet d'une analyse le mois dernier et qu'un risque « droit d'audit insuffisant » avait été relevé → il le signale au lieu de repartir de zéro.
3. **Procedural / préférences** : l'équipe Conformité veut toujours le rapport au format « synthèse + tableau d'articles » → mémorisé une fois, appliqué ensuite.

**Limite / piège :** la mémoire long-terme est une **nouvelle surface de fuite et de biais**. Si elle n'est pas scopée par utilisateur, l'agent peut révéler à un utilisateur ce qu'un autre a soumis. Et une mémoire erronée (un faux « souvenir ») se propage : il faut pouvoir **corriger/effacer** un souvenir, et l'auditer comme le reste.

## Erreurs fréquentes
- **Confondre mémoire et RAG** → on mélange connaissances documentaires et historique utilisateur dans le même store sans distinction de finalité ni d'ACL.
- **Buffer non borné** → le contexte grossit, la latence et le coût explosent, puis on dépasse la fenêtre.
- **Pas d'isolation par utilisateur** → fuite de données entre utilisateurs (incident de confidentialité).
- **Tout mémoriser** → bruit, coût, et risque RGPD ; mémoriser *sélectivement*.
- **Mémoire jamais expirée ni corrigible** → faux souvenirs persistants, pas de droit à l'oubli.
- Croire que « plus de mémoire = mieux » : souvent, un bon résumé + un retrieval ciblé battent un historique brut massif.
- Croire que la mémoire = l'agent qui « apprend » (modèle naïf où l'agent s'améliore seul au fil du temps) : **le modèle est figé**, ses poids ne changent pas. La « continuité » vient du **retrieval + état persisté**, pas d'un apprentissage en ligne. Faire évoluer le modèle lui-même = boucle **hors-ligne** feedback → dataset → finetuning ([14](14-user-feedback.md), [13](13-dataset-engineering.md), [12](12-finetuning.md)).
