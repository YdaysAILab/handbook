# 02 — MCP & Tool Calling

> Module 02 — Connecter les systèmes.

## P — Problème

Un LLM, seul, ne sait que produire du texte. Pour être utile en entreprise, l'agent doit **agir sur des systèmes réels** : lire un fichier SharePoint, interroger GLPI, écrire dans une base. Deux sous-problèmes :
1. comment le modèle **décide** quelle action appeler et avec quels arguments (tool calling) ;
2. comment **exposer** ces actions de façon standardisée, sécurisée et réutilisable entre plusieurs agents/applications (MCP).

## D — Définition

- **Tool calling (function calling)** : capacité du LLM à renvoyer, au lieu de texte, un appel structuré `nom_outil(arguments)` que ton code exécute, puis dont tu réinjectes le résultat dans la conversation. Les **arguments typés** sont un cas de **sortie structurée** ([26](26-structured-output.md)).
- **La boucle d'agent (ReAct)** : le schéma grand public `perception → raisonnement → action` se traduit ici en une boucle très concrète — `perception` = résultats d'outils réinjectés dans la conversation, `raisonnement` = une passe du LLM, `action` = le `tool_use` que **ton code** exécute. Ce motif *raisonnement puis action*, répété, est connu sous le nom **ReAct** (*Reason + Act*). ⚠️ On ne *programme* pas le raisonnement : le modèle **pilote** la boucle, le code ne fait qu'exécuter les outils et lui renvoyer les résultats jusqu'à ce qu'il décide d'arrêter. **Toujours borner la boucle** (`max_iterations` / *circuit breaker*) : un agent qui ne « décide » jamais d'arrêter part en boucle infinie — coût qui explose (*denial-of-wallet*, [28](28-securite-llm-threats.md)) et latence. Cette boucle s'**évalue** sur son *chemin* (bon outil, bons arguments, tâche aboutie), pas seulement sur la réponse finale → voir *Évaluer un agent* ([07](07-llmops-evaluations.md)).
- **MCP (Model Context Protocol)** : un **protocole standard** qui décrit comment un « serveur MCP » expose des *tools*, des *resources* et des *prompts* à n'importe quel client/agent. C'est le « port USB » entre agents et systèmes : on écrit le connecteur une fois, tous les agents l'utilisent.
- ⚠️ MCP relie un agent à ses **outils/données** (vertical). Pour la communication **entre agents** (horizontal), voir [25 — A2A](25-a2a-interop-agents.md). Les deux sont **complémentaires**.

| | Tool calling | MCP |
| --- | --- | --- |
| Niveau | Mécanisme modèle↔code | Protocole d'intégration réutilisable |
| Portée | Dans une appli | Partagé entre applis/agents |
| Analogie | « appeler une fonction » | « brancher un périphérique standard » |

## S — Solution

1. **Décrire** chaque outil par un schéma (nom, description, paramètres typés JSON Schema).
2. Le LLM choisit l'outil et produit des **arguments validés** contre le schéma.
3. Ton exécuteur lance l'action **avec les permissions de l'utilisateur** (pas celles de l'agent) — voir [04 — Sécurité](04-securite-gouvernance.md).
4. Le résultat est réinjecté ; l'agent continue son raisonnement.
5. Pour la réutilisation inter-applis, on expose les outils derrière un **serveur MCP** authentifié.

Bonnes pratiques :
- descriptions d'outils **claires et non ambiguës** (le modèle choisit sur la base du texte) ;
- **moindre privilège** : un outil = une capacité précise, scope minimal ;
- validation stricte des arguments avant exécution ; jamais de confiance aveugle ;
- outils **idempotents** quand c'est possible (voir [07](07-llmops-evaluations.md)) ;
- journaliser chaque appel (audit).

**Menaces spécifiques MCP** (voir la carte [28](28-securite-llm-threats.md)) :
- **Tool poisoning** : la **description** d'un outil (lue par le modèle) contient une injection → traiter la description d'un serveur tiers comme **non fiable**.
- **Confused deputy** : l'agent, plus privilégié que l'utilisateur, exécute une action que l'utilisateur n'aurait pas le droit de faire → **toujours agir avec l'identité de l'utilisateur** ([04](04-securite-gouvernance.md)), pas celle du service. **Mécanisme** : l'identité est **résolue côté serveur** (après authentification) et **injectée** dans l'exécuteur (contexte/closure) — **jamais un argument d'outil** que le modèle ou le client peut fixer, sinon l'outil devient un endpoint « *agir en tant que n'importe qui* ». Corollaire : le principal est soit **l'utilisateur** (appel interactif → **token délégué OAuth**, scope minimal), soit, pour un **job non supervisé** (batch/planifié, sans humain), un **compte de service dédié et scopé** — **jamais un token partagé ou trop large** qui contourne les permissions et casse l'audit. Preuve attendue : deux utilisateurs, même entrée d'outil → **deux identités, deux résultats** (test d'isolation, cf. accès différencié [29](29-multi-user-sessions.md)).
- **Serveur MCP tiers compromis / rug-pull** : dépendance de **supply chain** → épingler la version, auditer, isoler.
- **Outil non sandboxé** : l'implémentation de l'outil elle-même doit **confiner ses effets de bord** — un outil fichier doit bloquer le *path traversal* (`../../etc/passwd`) et rester dans son répertoire autorisé ; un outil SQL/shell doit être paramétré, jamais concaténé. Valider les arguments **ne suffit pas** si l'exécution peut s'échapper de son périmètre (OWASP **LLM06** agentivité excessive / **LLM05** sortie non maîtrisée, [28](28-securite-llm-threats.md)).
- **Vol de token** : les tokens OAuth/clés de l'outil sont des **secrets** → secret store, scope minimal, jamais dans le prompt/les logs.

## E — Exemple (DORA)

L'agent DORA a besoin de 3 outils, exposés via MCP :
- `sharepoint.get_contract(contract_id)` → récupère le PDF du contrat (lecture seule, scope SharePoint restreint).
- `dora_kb.search(query)` → interroge la base documentaire DORA (RAG) — voir [03](03-rag-data-pipelines.md).
- `tickets.create(summary, risk_level)` → crée un ticket GLPI si risque élevé.

Déroulé : l'utilisateur demande l'analyse → le LLM appelle `sharepoint.get_contract` → puis `dora_kb.search` pour les exigences pertinentes → il analyse → s'il faut agir, `tickets.create`.

**Limite / piège :** l'outil `sharepoint.get_contract` doit vérifier que **l'utilisateur** a le droit de lire ce contrat, pas seulement l'agent. Sinon un utilisateur peut faire lire par l'agent un document confidentiel auquel il n'a pas accès → c'est le cœur de l'exercice sécurité du workshop.

## Erreurs fréquentes
- Donner à l'agent un outil « admin » large au lieu d'outils étroits (violation du moindre privilège).
- Exécuter l'action avec les droits du *service* au lieu des droits de l'*utilisateur*.
- Descriptions d'outils floues → le modèle appelle le mauvais outil.
- Ne pas valider/typer les arguments → injection ou appel destructeur.
- Oublier l'audit trail des appels d'outils.
- Croire qu'on *programme* le raisonnement (modèle naïf `perception→raisonnement→action`) : c'est le LLM qui pilote la boucle ; le code ne fait qu'exécuter les outils et réinjecter les résultats.
