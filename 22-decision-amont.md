# 22 — Décision amont : faut-il seulement construire ça ?

> Module 00 — **Avant** toute l'ingénierie. La question qu'on a sautée : *devrait-on construire, et comment le justifier ?*

## P — Problème

Tout le handbook répond à « **comment** construire ». Mais on n'a jamais posé « **devrait-on** ? ». Résultat classique : des projets qui ne **valent pas leur coût**, ou des **démos impressionnantes** qui n'atteignent jamais la production (le *last-mile*). Décider **de ne pas construire** — ou de construire autrement — est parfois la meilleure décision d'ingénierie.

## D — Définition

- **Use case evaluation** : la valeur métier, le risque et la faisabilité **avant** de coder.
- **ROI** : gains attendus vs coûts **complets** (dev + inférence + maintenance + conformité).
- **Build vs buy** : construire, utiliser une API, ou acheter une solution existante (voir [05](05-ai-gateway-routing.md), [08](08-serving-inference.md)).
- **Last-mile challenge** : la démo à 80 % est facile ; les **20 % restants** (cas limites, hallucinations, conformité) coûtent le plus.
- **Usefulness threshold** : le seuil de qualité **en-dessous duquel** l'outil est inutile ou dangereux.

## S — Solution

1. **Évaluer le cas d'usage** : quelle **valeur** (temps juriste économisé, risque réduit) ? quel **rôle** pour l'IA (critique vs complémentaire, réactive vs proactive) ? quelle **faisabilité** ?
2. **Calculer le ROI complet** : coûts = dev + **inférence** ([09](09-ai-finops.md)) + **maintenance** (ré-évals, dérive, [20](20-deploiement-fiabilite.md)) + **conformité** ([18](18-gouvernance-conformite.md)). Ne pas oublier les coûts cachés.
3. **Build vs buy** : API managée (simple) vs self-host (contrôle/confidentialité, [08](08-serving-inference.md)) vs solution du marché.
4. **Définir l'usefulness threshold** : sous quelle exactitude l'outil DORA devient un **risque** plutôt qu'une aide ? (un faux négatif réglementaire coûte cher — [16](16-evaluation-quantitative.md)).
5. **Planifier le last-mile dès le départ** : budgéter les 20 % difficiles (contrats atypiques, langues, scans illisibles, hallucinations) — pas seulement la démo.

## E — Exemple (DORA)

Avant de lancer le projet : combien de **contrats/an** ? combien de **temps juriste** économisé (ROI) ? quel **seuil de qualité** acceptable (un risque DORA manqué = sanction) ? **build** (confidentialité des contrats) vs **buy** ? Et un **plan pour le last-mile** : les contrats scannés illisibles ([19](19-document-understanding.md)), les clauses ambiguës, les cas à faible confiance qui iront **au juriste** ([21](21-ux-livraison.md)). Si le volume est faible et le risque d'erreur élevé → peut-être **ne pas automatiser**, ou se limiter à une **aide** (pas une décision).

**Limite / piège :** le biais de l'ingénieur est de **construire**. Parfois, la bonne réponse est « non » ou « pas encore » — ou « un outil d'aide, pas un décideur ». La valeur se mesure en **impact métier**, pas en sophistication technique.

## Erreurs fréquentes
- Sauter à « comment construire » sans justifier la valeur.
- Oublier les coûts de **maintenance** et de **conformité** dans le ROI.
- Sous-estimer le **last-mile** (planifier la démo, pas la prod).
- Pas d'**usefulness threshold** → on déploie un outil « à moitié bon » qui crée du risque.
- Construire ce qu'on pourrait **acheter** (ou l'inverse).
