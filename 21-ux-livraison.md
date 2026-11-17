# 21 — UX produit & livraison

> Module 06 — Le côté **humain** du système. La valeur **perçue** dépend de l'expérience, pas seulement de l'exactitude.

## P — Problème

Un système exact mais **mal livré** n'est pas adopté : réponses lentes à apparaître, pas de sources, confiance mal calibrée, passage de relais à l'humain brutal. En contexte réglementé, la **transparence** et la **confiance** ne sont pas des options — l'utilisateur doit pouvoir **vérifier** et l'humain doit pouvoir **reprendre la main**.

## D — Définition

- **Streaming** : afficher la réponse **au fil de la génération** (voir [08](08-serving-inference.md), [15](15-model-internals.md)) → réduit la **latence perçue**.
- **Perceived latency** : le ressenti ≠ le temps réel ; indicateurs de progression pour les tâches longues (agent multi-étapes).
- **Transparence / trust calibration** : montrer sources et niveau de confiance pour que l'utilisateur ne fasse ni **trop** ni **trop peu** confiance.
- **Human handoff** : le design du **passage de relais** à l'humain.

## S — Solution

- **Streaming + progression** : streamer l'analyse ; pour un agent multi-étapes, montrer l'étape en cours (« recherche des articles DORA… »). Transport : **SSE** (HTTP unidirectionnel, reconnexion auto) suffit ; WebSocket seulement si interruption/bidirectionnel.
- **Streamer pour l'humain, bufferiser pour la machine** : le streaming **n'inspecte pas ce qu'il a déjà envoyé**. On streame le **texte d'explication** (affichage) ; on **bufferise + valide** tout ce qui franchit une **frontière** — la **décision structurée** ([26](26-structured-output.md)), les **guardrails de sortie** et le **masquage PII** ([04](04-securite-gouvernance.md), [23](23-pii-anonymisation.md)), et toute **action** — **avant** émission. Règle d'or : **ne rien streamer** vers le navigateur / les logs / une action qu'un guardrail **n'a pas validé**.
- **Erreur en cours de stream** : un `200` + texte partiel est déjà parti → on ne peut plus repasser en `500` ; émettre un **événement d'erreur** dans le flux + **mode dégradé** ([20](20-deploiement-fiabilite.md)). Couper la génération (libérer le serving) si le client se déconnecte.
- **Transparence** : afficher les **citations** ([03](03-rag-data-pipelines.md), [17](17-hallucinations.md)) **cliquables** vers la source (page du contrat, [19](19-document-understanding.md)) ; afficher le **niveau de confiance**.
- **Trust calibration** : signaler explicitement l'**incertitude** (« confiance faible → revue recommandée ») — ni surconfiance (l'utilisateur gobe tout) ni sous-confiance (il ignore l'outil).
- **Design du handoff humain** ([18](18-gouvernance-conformite.md)) : définir **quand** escalader (faible confiance, enjeu élevé) et **comment** — présenter au juriste un **dossier complet** (ce que l'agent a fait, sources, points de doute), pas une boîte noire.
- **La décision « répondre ou escalader » est un garde-fou déterministe, pas un choix du LLM.** Le LLM **rationalise vers la réponse** (biais) et est **manipulable par injection** ([28](28-securite-llm-threats.md)) → confier *l'auto-escalade* au modèle est dangereux. Une **fonction** (code, testable) tranche à partir de **signaux** : score de retrieval sous un **plancher** → escalader ; **drapeau de risque** (fraude, suppression de données, enjeu financier) → escalader ; juges de faithfulness ([24](24-llm-as-judge.md)) en désaccord → escalader. Même esprit que « contrôle du flux en Python, pas dans le LLM » ([08](08-serving-inference.md)).
  - **Par défaut, l'incertitude → escalade** (jamais « tenter quand même ») — [17](17-hallucinations.md).
  - **Trois issues, pas deux** : répondre (ancré+cité) · **décliner par modèle** (hors-sujet bénin, sans humain) · escalader (risqué/incertain).
  - **Seuils asymétriques** : barre de confiance **plus stricte** pour les tickets à risque que pour les FAQ routinières.
- **Feedback intégré** ([14](14-user-feedback.md)) : capter la correction du juriste sans friction.

## E — Exemple (DORA)

L'agent **streame** son analyse et montre sa progression. Chaque article cité est **cliquable** → ouvre la page exacte du contrat ([19](19-document-understanding.md)). Un bandeau indique « **confiance : faible** → revue juriste recommandée ». À l'escalade, le juriste reçoit un **dossier** : verdict, articles, extraits sources, et les points où l'agent a hésité — il corrige en un clic (feedback [14](14-user-feedback.md)).

**Limite / piège :** la transparence **mal dosée** nuit (surcharge d'informations, faux sentiment de certitude). Calibrer : montrer ce qui aide à **décider et vérifier**, pas tout déverser.

## Erreurs fréquentes
- Réponse qui apparaît **d'un bloc** après 30 s (pas de streaming) → perçue comme cassée.
- **Streamer les tokens bruts** sans masquage → **fuite PII** avant que le guardrail voie la sortie complète ([23](23-pii-anonymisation.md)).
- Déclencher une **action** (ticket, écriture ERP) sur du **texte streamé non validé** au lieu d'attendre la **sortie structurée validée** ([26](26-structured-output.md)).
- Afficher un **verdict/confiance en streaming** avant validation → l'utilisateur voit une décision qui peut encore changer.
- **Aucune source affichée** → l'utilisateur ne peut pas vérifier (et croit ou rejette en bloc).
- Confiance **non calibrée** → surconfiance dangereuse en conformité.
- Handoff humain **brutal** (« je ne peux pas répondre ») sans contexte transmis.
- Laisser le **LLM décider lui-même** s'il doit répondre ou escalader → il penche vers « répondre » et une **injection** peut forcer la réponse ; la décision doit être un **garde-fou déterministe** ([28](28-securite-llm-threats.md)).
- Feedback utilisateur **non capté** faute d'intégration fluide ([14](14-user-feedback.md)).
