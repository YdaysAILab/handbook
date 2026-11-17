# 23 — Protection des PII & anonymisation (au gateway egress)

> Module 04/05 — Sécuriser & router. Un contrôle **de confidentialité** placé au point de sortie vers les modèles externes.

## P — Problème

Les prompts envoyés aux LLM contiennent presque toujours des **données personnelles** (noms, emails, téléphones, IBAN, adresses, identifiants, signataires de contrats). Les envoyer à un **fournisseur externe**, c'est :
- une **violation RGPD** potentielle (données qui quittent le périmètre, parfois hors UE) ;
- un risque de **persistance** : la PII peut rester dans les **logs/traces** ([06](06-observabilite.md)) et les **caches** ([08](08-serving-inference.md)).

Il faut **détecter** et **anonymiser/rédiger** les PII **avant** qu'elles ne sortent — et le faire à **un seul endroit** pour toutes les applis.

## D — Définition

- **PII** (*Personally Identifiable Information*) : toute donnée identifiant une personne.
- **Détection d'entités (NER)** : repérer noms, emails, téléphones, IBAN, cartes, adresses, identifiants nationaux + **entités métier custom** (n° de contrat, identifiant fournisseur).
- **Rédaction (redaction)** : supprimer/masquer la PII — **irréversible**.
- **Pseudonymisation réversible** : remplacer par un **placeholder** (`<PERSON_1>`) avec un **dictionnaire de correspondance** pour **ré-identifier** la réponse ensuite.
- **Egress** : le point de **sortie** vers un service externe (ici, le gateway).
- **Microsoft Presidio** : outil open-source de détection (*analyzer*) + anonymisation (*anonymizer*) de PII, déployable comme **guardrail**.

## S — Solution : anonymiser au gateway egress

```
App ─▶ AI Gateway ─▶ [Presidio: analyze → anonymize] ─▶ LLM externe
                           (placeholders)                    │
App ◀── [de-anonymize via dictionnaire] ◀──────── réponse ◀──┘
```

- **Placer la protection au gateway** ([05](05-ai-gateway-routing.md)) : **un seul point de contrôle** pour toutes les applications (pas de réimplémentation par appli).
- **Pipeline** : *analyze* (NER) → *anonymize/redact* → envoyer au modèle → **optionnellement de-anonymize** la réponse via le dictionnaire.
- **Choisir la stratégie** :
  - **rédaction irréversible** pour la PII **non nécessaire** à la tâche ;
  - **pseudonymisation réversible** (placeholders) quand le modèle doit **raisonner sur l'entité** et que la réponse doit être **ré-identifiée** pour l'utilisateur.
- **Reconnaisseurs custom** pour le domaine (n° de contrat DORA, identifiants fournisseurs).
- **Ordre critique** : anonymiser **avant** de **logger/tracer** ([06](06-observabilite.md)) et avant tout **cache** ([08](08-serving-inference.md)) — sinon la PII persiste.
- **Cas du streaming** : la réponse **streamée** token par token **contourne** un masquage fait seulement en fin de réponse. Si on streame ([21](21-ux-livraison.md)) : soit **masquer au fil de l'eau** (retenir les tokens susceptibles d'**ouvrir** une entité PII avant de les émettre), soit **bufferiser** le segment concerné avant de l'envoyer au navigateur/aux logs. La **ré-identification par placeholders** a besoin de segments **complets** → ces zones se bufferisent, elles ne se streament pas brutes.
- **Articulation** : c'est un **input guardrail** ([04](04-securite-gouvernance.md)) et une mesure **RGPD de minimisation** ([18](18-gouvernance-conformite.md)). Pour les données **les plus** sensibles, **combiner** avec le routage « confidentiel → modèle interne » ([05](05-ai-gateway-routing.md)).

> **Implémentation de référence :** Presidio déployé comme **guardrail LiteLLM** au gateway (ex. `05-presidio.yaml` dans le bundle LiteLLM), appliqué à l'**egress**.

## E — Exemple (DORA)

Un contrat contient le **nom, l'email, l'IBAN** du signataire et un **n° de contrat**. Avant l'envoi au LLM externe pour analyse de risque :
1. Presidio **détecte** et remplace → `<PERSON_1>`, `<EMAIL_1>`, `<IBAN_1>`, `<CONTRACT_ID_1>` ;
2. le modèle **analyse le risque** sur le texte **pseudonymisé** (il n'a pas besoin des vraies valeurs) ;
3. la réponse est **ré-identifiée** via le dictionnaire avant affichage au juriste ;
4. **logs et caches** ne contiennent que les **placeholders** — la PII réelle n'a jamais quitté le périmètre.

Pour un contrat marqué **confidentiel**, on **cumule** : anonymisation **+** routage vers le **modèle interne** ([05](05-ai-gateway-routing.md)).

**Limite / piège :** la détection n'est **jamais parfaite** — **faux négatifs** (PII qui fuit) et **faux positifs** (sur-masquage qui dégrade l'analyse). On calibre, on ajoute des reconnaisseurs custom, et on ne s'y repose **pas seul** pour les données les plus sensibles (préférer le modèle interne). L'anonymisation **ne remplace pas** le contrôle d'accès ([04](04-securite-gouvernance.md)) ; elle s'inscrit dans la **carte des menaces** globale (LLM02, [28](28-securite-llm-threats.md)).

## Erreurs fréquentes
- Anonymiser **dans chaque appli** au lieu du **gateway** → chaque appli réinvente, trous de couverture.
- **Logger ou cacher avant** d'anonymiser → PII dans les traces/caches ([06](06-observabilite.md), [08](08-serving-inference.md)).
- **Streamer la réponse** vers l'utilisateur/les logs **avant** masquage/ré-identification → fuite PII **token par token** ([21](21-ux-livraison.md)).
- **Rédaction irréversible** là où il fallait pouvoir **ré-identifier** la réponse.
- Pas de **reconnaisseurs custom** → les identifiants métier (n° de contrat) passent au travers.
- Croire que l'anonymisation **remplace** le routage confidentiel ou l'ACL — ce sont des couches **complémentaires**.
