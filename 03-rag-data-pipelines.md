# 03 — RAG & Data Pipelines

> Module 03 — Connecter les données.

## P — Problème

Le LLM ne connaît pas tes documents internes et il **hallucine** quand on lui demande des faits qu'il ne possède pas. Pour l'assistant DORA, les réponses doivent s'appuyer sur les **exigences réglementaires réelles** et les **contrats réels** — pas sur la mémoire approximative du modèle. Il faut aussi respecter les **droits d'accès** aux documents.

## D — Définition

- **RAG (Retrieval-Augmented Generation)** : on **récupère** d'abord les passages pertinents dans une base de connaissances, puis on les **injecte dans le prompt** pour que le LLM réponde en s'appuyant dessus (grounding).
- **Pipeline d'ingestion** : la chaîne qui prépare les documents : extraction → découpage (chunking) → **embeddings** → indexation dans une base vectorielle (+ métadonnées et ACL).

## S — Solution : les deux temps

**1. Ingestion (hors ligne)**
```
Document → extraction texte → chunking → embeddings → index vectoriel (+ métadonnées + ACL)
```
- chunking adapté (taille + overlap) pour ne pas couper le sens ;
- stocker avec chaque chunk ses **métadonnées** (source, date, confidentialité, propriétaire) → indispensable pour le filtrage par droits.

**2. Retrieval + génération (en ligne)**
```
Question → embedding → recherche (vector + lexical) → reranking → top-k passages → prompt → LLM → réponse citée
```
- **Hybrid search** : combiner recherche vectorielle (sémantique) et recherche lexicale (mots-clés, type BM25) → meilleure robustesse.
- **Reranking** : un modèle de rerank reclasse les candidats pour mettre les plus pertinents en tête avant de les donner au LLM.
- **Permissions documentaires (ACL)** : filtrer les passages selon ce que **l'utilisateur** a le droit de voir — le filtrage se fait au retrieval, avant d'atteindre le LLM.
- **Citations** : demander au modèle de citer ses sources → traçabilité et confiance.

## E — Exemple (DORA)

Base de connaissances = texte des exigences DORA + guides internes. À la question *« Ce contrat présente-t-il un risque DORA ? »* :
1. le texte du contrat (extrait via l'outil SharePoint) et la question servent à interroger la base ;
2. hybrid search + reranking remontent les articles DORA pertinents (ex. exigences sur la sous-traitance critique, droits d'audit, réversibilité) ;
3. ces passages + le contrat sont injectés dans le prompt ;
4. le LLM compare et répond **en citant** les articles.

**Limite / piège :** si l'ingestion n'embarque pas les ACL, un utilisateur peut recevoir, via les passages récupérés, des informations issues de documents auxquels il n'a pas droit. Le contrôle d'accès doit vivre **dans le retrieval**, pas seulement dans l'UI.

## RAG classique vs RAG agentique (distinction clé)

Le RAG décrit ci-dessus est **« naïf »** : un **pipeline figé** — `question → retrieve top-k → générer`. Une seule passe, **aucune décision**. Le **RAG agentique** confie le retrieval à un **agent** ([01](01-langchain-langgraph-crewai.md)) qui **raisonne et décide** autour de la récupération.

| | **RAG classique** | **RAG agentique** |
| --- | --- | --- |
| Flux | figé, **une passe** | **boucle décisionnelle** |
| Faut-il récupérer ? | toujours | **l'agent décide** (sinon : répond, ou appelle un outil) |
| Requête | telle quelle | **reformulée / décomposée** (sous-questions, multi-hop) |
| Sources | une base | **routage** entre plusieurs bases/outils (SQL, web…) |
| Itération | non | **retrieve → raisonne → re-retrieve** si insuffisant |
| Qualité | — | **auto-évalue la pertinence** (*Corrective RAG / Self-RAG*) et recommence |

**Quand quoi :**
- **Classique** : Q&A directe, une base, faible enjeu de complétude → **moins de latence/coût**.
- **Agentique** : questions **complexes / multi-sources / multi-étapes**, besoin de **vérification** → meilleure couverture, **au prix de latence/coût** ([08](08-serving-inference.md)/[09](09-ai-finops.md)).

**Exemple DORA :**
- *« Que dit DORA sur le droit d'audit ? »* → **RAG classique** suffit.
- *« Ce contrat de 40 pages est-il conforme DORA ? »* → **agentique** : décomposer **par exigence**, router vers (KB DORA + texte du contrat), **itérer** article par article, **auto-évaluer** si un passage manque et re-récupérer (moins d'hallucinations, [17](17-hallucinations.md) ; pertinence jugée par un **LLM-juge**, [24](24-llm-as-judge.md)).

> Le RAG agentique **est** un agent qui orchestre le retrieval → mêmes **choix de framework** ([01](01-langchain-langgraph-crewai.md)) et mêmes **garde-fous de coût** (routage, [09](09-ai-finops.md)). Ne l'adopte que si la complexité des questions le justifie.

## Erreurs fréquentes
- Utiliser un **RAG agentique** là où un **classique** suffit (latence/coût inutiles) — ou l'inverse (**sous-récupération** sur des questions multi-hop).
- Chunks trop gros (bruit) ou trop petits (perte de contexte).
- Recherche purement vectorielle sans lexical → rate les termes exacts (numéros d'article, identifiants).
- Pas de reranking → le top-k contient du quasi-pertinent, le LLM dérive.
- ACL appliquées après génération au lieu du retrieval → fuite de données.
- Pas de citations → impossible de vérifier/auditer.
- Index jamais rafraîchi → réponses périmées.
