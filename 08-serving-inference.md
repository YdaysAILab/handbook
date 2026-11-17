# 08 — Serving & Inference

> Module 05/06 — Déployer, fiabiliser, optimiser.

## P — Problème

Appeler une API LLM externe est simple mais pose des limites : **coût** à grande échelle, **confidentialité** (les données sortent de l'entreprise), **latence** et **dépendance** à un tiers. Pour des cas comme DORA (contrats confidentiels, gros volumes), on veut souvent **héberger soi-même** des modèles — ce qui introduit la question du *serving* efficace sur GPU.

## D — Définition

- **Serving / inference** : exécuter un modèle pour produire des réponses, de façon performante et scalable.
- **vLLM** : moteur d'inférence open source haute performance pour LLM (débit élevé, gestion mémoire optimisée).
- **GPU** : le matériel qui exécute les modèles ; ressource rare et coûteuse → à maximiser.
- **Batching** : regrouper plusieurs requêtes pour mieux utiliser le GPU.
- **KV cache** : cache des clés/valeurs d'attention réutilisées entre tokens → accélère la génération et réduit le recalcul.
- **Quantification** : réduire la précision des poids (ex. FP16 → INT8/INT4) → modèle plus petit/rapide, léger coût de qualité.
- **Ollama** : moteur de serving **facile et CPU-friendly** pour modèles open-weights (Llama, Qwen…). Équivalent « simple » de vLLM ; idéal quand on n'a **pas de GPU**.

> 📦 **Encadré — « Ollama, c'est un provider ? » (à ne pas confondre)**
>
> On confond souvent trois rôles distincts :
>
> | Rôle | Définition | Exemples |
> | --- | --- | --- |
> | **Fournisseur (provider)** | expose des modèles **via API** (souvent cloud, commercial) | OpenAI, Anthropic, Google, Mistral |
> | **Moteur de serving / inférence** | **fait tourner les poids** du modèle (chez toi) | **Ollama**, vLLM, TGI, llama.cpp |
> | **Gateway** | couche **devant** qui unifie tout derrière une seule API | LiteLLM ([05](05-ai-gateway-routing.md)) |
>
> **Ollama est un moteur de serving self-hosted**, pas un provider commercial. Mais **le gateway le traite comme un “provider”** : dans la config LiteLLM, `ollama/qwen2.5:3b` = *(provider `ollama`, modèle `qwen2.5:3b`)*, au même titre que `openai/…`. La différence qui compte : avec Ollama, **les données ne quittent pas le périmètre** (confidentialité, [05](05-ai-gateway-routing.md)/[23](23-pii-anonymisation.md)) — alors qu'un provider externe les fait sortir.

### Taxonomie des modèles — 4 axes **orthogonaux** (un modèle coche plusieurs cases)

« Reasoning », « open-weight », « multimodal » ne sont **pas trois modèles différents** : ce sont des **axes indépendants**. Le **même** modèle peut être reasoning **et** open-weight **et** multimodal.

| Axe | Valeurs (exemples) |
| --- | --- |
| **Capacité** | général · **reasoning** (o-series, DeepSeek-R1, QwQ) · coding · instruct · **tool-use/function-calling** · **embedding** (BGE, E5) · **reranking** (BGE Reranker, Cohere) · domaine (FinGPT, Meditron) · **multimodal** (Qwen-VL, Gemini) · **SLM** (Phi, Gemma, SmolLM) |
| **Architecture** | encoder-only (BERT → classif/embeddings/NER) · **decoder-only** (GPT/Llama → chat/agents) · encoder-decoder (T5 → traduction/résumé) · dense vs **MoE** (Mixtral) · hybrides |
| **Ouverture / déploiement** | propriétaire/API · **open-weight** · fully-open · cloud / **self-hosted** / on-prem / edge · taille (SLM → frontier) · base / instruct / fine-tuné / preference-optimized · standard / **quantifié** / distillé |
| **Modalité** | texte→texte · **VLM** (image+texte) · audio/speech · vidéo |

> Un **Qwen quantifié servi en local via Ollama** reste **le même modèle** : quantification + déploiement décrivent **comment il tourne**, pas une nouvelle catégorie. **Embedding/reranking** = composants **encoder-based**, **pas** des LLM génératifs (ils vectorisent/réordonnent pour le RAG, [03](03-rag-data-pipelines.md)).

**⚠️ Distinction cruciale — modèle ≠ architecture de système IA.**

| Type de **LLM** (le modèle qui infère) | Architecture / **processus** (ce qu'on construit *autour*) |
| --- | --- |
| reasoning LLM · embedding model · VLM… | **RAG** (fournit du contexte, [03](03-rag-data-pipelines.md)) · **agent** ([01](01-langchain-langgraph-crewai.md)) · **MCP** (protocole d'outils, [02](02-mcp-tool-calling.md)) · **multi-agent** ([30](30-multi-agent-systems.md)) · **fine-tuning** ([12](12-finetuning.md)) · **LLMOps** ([07](07-llmops-evaluations.md)) |

Confondre les deux → on choisit un **modèle** (« il nous faut un *reasoning model* ») quand le vrai besoin est une **architecture** (RAG, agent). **Choisis selon la tâche** (qualité · coût · latence · **confidentialité** · fiabilité des outils), en gardant **3 catalogues séparés** : **Model** (quels modèles) · **Capability** (ce que le système sait faire) · **Integration Pattern** (comment ça se branche). Boussole : *problème → **capacité** → **architecture** → **techno*** (exercice workshop 31).

## S — Solution

```
Requêtes ─▶ serveur d'inférence (vLLM) ─▶ GPU
             ├─ continuous batching   (débit)
             ├─ KV cache              (latence / réutilisation)
             └─ quantification        (mémoire / coût)
```
- choisir entre **API managée** (simple, pas de GPU à gérer) et **self-hosted** (contrôle, confidentialité, coût maîtrisé à l'échelle) ;
- **vLLM** pour maximiser le débit par GPU (continuous batching, paged KV cache) ;
- **quantifier** quand la qualité le permet pour tenir sur moins de GPU ;
- dimensionner la **capacité GPU** selon le débit cible (voir FinOps, [09](09-ai-finops.md)) ; sous **forte concurrence** (N utilisateurs simultanés), ajouter **file + backpressure** devant le serving → [29](29-multi-user-sessions.md).

Le Gateway ([05](05-ai-gateway-routing.md)) route vers ces modèles self-hosted pour les données confidentielles.

## E — Exemple (DORA)

Les contrats sont **confidentiels** : on ne les envoie pas à un fournisseur externe. On sert un modèle open-weights en interne via **vLLM** sur GPU, **quantifié** pour tenir sur le parc disponible. Le **batching** absorbe les pics (campagne d'analyse de centaines de contrats), le **KV cache** réduit la latence des longues analyses. Le Gateway envoie les données confidentielles **uniquement** vers ce déploiement interne.

**Limite / piège :** self-hosting = responsabilité opérationnelle (capacité GPU, mises à jour, disponibilité). À réserver aux cas où confidentialité/coût/volume le justifient ; sinon l'API managée est plus simple.

## Erreurs fréquentes
- Self-hoster par principe alors qu'une API managée suffirait (surcoût opérationnel).
- Sous-dimensionner le GPU → file d'attente, latence.
- Quantifier trop agressivement sans valider la qualité par les évals ([07](07-llmops-evaluations.md)).
- Ignorer le batching → GPU sous-utilisé, coût par requête élevé.

## Ollama en pratique (CPU — le vrai frein d'un lab sans GPU)

Ollama est **gratuit et universel**, mais en **CPU** l'inférence est **lente** et dépend fortement du **modèle** et des **ressources de la machine** (RAM surtout). Stratégie pour que ça reste utilisable :

**1. Dimensionner le modèle à la machine**

| RAM dispo | Modèle conseillé (quantifié Q4) | Usage |
| --- | --- | --- |
| 4–8 Go | `qwen2.5:1.5b` (FR) / `llama3.2:1b` | classif, extraction, sous-tâches (le modèle « fast ») |
| 8–16 Go | `qwen2.5:3b` (FR, défaut) / `llama3.2:3b` | chatbot/RAG interactif |
| 16–32 Go | `qwen2.5:7b-instruct` | analyses (le modèle « smart »), plus lent |
| < 4 Go | → **Ollama partagé** (voir ci-dessous) | la machine ne suit pas |

> Règle : **petit modèle quantifié par défaut**, gros modèle réservé aux rares étapes complexes (routage « fast » vs « smart » via le gateway, [05](05-ai-gateway-routing.md)).

**2. Masquer / réduire la latence**
- **Streaming** ([21](21-ux-livraison.md)) : afficher au fil de l'eau → latence *perçue* bien plus faible.
- **Prompts courts** + contexte ciblé (moins de tokens = plus rapide) ; **prompt/KV caching**. Les **paramètres de génération** (`num_ctx`, `num_predict`, `temperature`…) se règlent côté serving → [27](27-generation-parameters.md).
- **Quantification** (Q4_K_M) : modèles plus petits/rapides, qualité à valider par évals ([16](16-evaluation-quantitative.md)).

**3. L'astuce clé pour une promo : un Ollama PARTAGÉ**
Plutôt que chaque PC rame à faire tourner un modèle, **une seule machine costaude (serveur/instructeur) héberge Ollama** ; tous les agents pointent vers **le gateway partagé** :
```
Agents des apprenants ─▶ Gateway (LiteLLM partagé) ─▶ Ollama (1 serveur)
```
- côté apprenant : `LITELLM_BASE_URL=http://<serveur>:4000` (au lieu de localhost) ;
- côté gateway : `OLLAMA_API_BASE=http://<serveur>:11434`.
- Avantage : on **mutualise** l'inférence, les PC faibles suivent, et le modèle reste **self-hosted** (données dans le périmètre).

**4. Finetuning** : l'entraînement LoRA se fait sur **Colab** (GPU gratuit), puis l'adapter (petit) est servi par Ollama en inférence (léger) — voir [12](12-finetuning.md).

**5. Adéquation modèle ↔ besoin (benchmarks 2026)**

Pourquoi les petits modèles suffisent **ici** : l'orchestration (LangGraph, [01](01-langchain-langgraph-crewai.md)) et le grounding (RAG, [03](03-rag-data-pipelines.md)) font que le modèle ne traite que des **tâches courtes et ancrées** (classer, extraire, répondre depuis des passages, appeler **un** outil) — précisément ce que les petits modèles font bien. Leur faiblesse (planning autonome multi-étapes) est **évitée par design**.

| Besoin | Modèle Ollama conseillé | Confiance |
| --- | --- | --- |
| RAG + citations + FR (chatbot, conformité) | `qwen2.5:3b` → `7b` | ✅ élevée |
| Extraction + JSON + classification (KYC, formulaires) | `qwen2.5:3b/7b` (JSON/function mode) | ✅ élevée |
| Classification à l'échelle | **petit modèle finetuné** (LoRA, [12](12-finetuning.md)) | ✅ élevée |
| Workflow multi-étapes **piloté par LangGraph** | `qwen2.5:7b` | ✅ bonne (le graphe planifie, pas le modèle) |
| **Function calling** fiable (outils) | `qwen2.5:7b` (≫ 3B ; Llama 3.2 3B ≈ 67 % BFCL = triage seulement) | 🟡 garder des schémas d'outils simples |
| **Raisonnement + multi-agents** (conformité réglementaire) | `qwen2.5:7b`, sinon **14B via Ollama partagé** | 🟡 le cas le plus exigeant |

- **Français** : **Qwen2.5** et **Mistral** > Llama 3.2 (Mistral = éditeur français ; Qwen2.5 fort multilingue) → défaut = **Qwen2.5**.
- **Garde-fou** : toute adéquation se **valide par les évals** ([16](16-evaluation-quantitative.md)) ; si le quality gate régresse, on monte d'un cran (7B → 14B via Ollama partagé).

> En résumé : Ollama **est** le « provider » du projet (via le gateway) ; le frein n'est pas conceptuel mais **matériel** → petit modèle quantifié + streaming + **Ollama mutualisé** = lab fluide sans GPU.

## Pour aller plus loin — optimisation d'inférence avancée (niveau livre, ch. 9)

> Approfondissement de la fiche pour qui veut dimensionner et optimiser sérieusement. Les principes ci-dessus suffisent pour concevoir ; cette section sert à **mesurer et accélérer**.

### Les bonnes métriques (au-delà de « latence/débit »)
- **TTFT / TPOT** : *Time To First Token* (lié au **prefill**) et *Time Per Output Token* (lié au **decode**). Latence totale ≈ TTFT + TPOT × nb_tokens. Raisonner en **percentiles** (p90/p95/p99), jamais en moyenne.
- **Goodput** : requêtes/s qui **respectent le SLO** (≠ throughput brut). C'est la vraie métrique business.
- **MFU / MBU** : *Model FLOP/s Utilization* et *Model Bandwidth Utilization* — l'utilisation **réelle** du GPU. `nvidia-smi` est trompeur (il montre « occupé », pas « efficace »).

### Pourquoi le decode est le goulot
- **Compute-bound vs memory-bandwidth-bound** (roofline / arithmetic intensity) : le **prefill** est parallèle et compute-bound ; le **decode** est token-par-token et **bandwidth-bound** → c'est lui qui plafonne. Comprendre ça oriente toutes les optimisations.

### Réduire le KV cache (souvent le vrai mur mémoire)
- **MQA / GQA** (*Multi-Query* / *Grouped-Query Attention*) : partagent les têtes K/V → KV cache réduit jusqu'à ~10-20×.
- **PagedAttention** (vLLM) : mémoire KV non-contiguë, moins de gaspillage. **KV quantization/compression** en complément.

### Battre le bottleneck autorégressif
- **Speculative decoding** : un petit *draft model* propose K tokens, le grand les **vérifie en parallèle** → latence ↓ sans perte de qualité.
- **Parallel decoding** (Medusa, Lookahead/Jacobi) et **inference with reference** (recopie de spans depuis l'input : RAG, code, multi-turn).

### Mise à l'échelle & service
- **5 types de parallelism** : *replica* (débit), **tensor** (intra-op → latence ↓ + gros modèles), **pipeline** (débit ↑ mais latence ↑), *context*, *sequence*.
- **Continuous (in-flight) batching** : renvoie chaque réponse dès qu'elle est finie (≠ static batching).
- **Prefill/decode disaggregation** (DistServe) : instances séparées, ratios typiques 2:1–4:1.
- **Prompt caching** (prefix/context cache) : réutilise les segments communs (system prompt, long doc) → jusqu'à −75/90 % de coût/latence sur l'input. ⚠️ **risque de fuite** : ne pas partager un cache entre utilisateurs aux droits différents (lien [04](04-securite-gouvernance.md)).
- **Kernels & compilers** : FlashAttention, Triton/CUDA, `torch.compile`/TensorRT, *operator fusion*.

**Pour DORA :** campagne d'analyse de centaines de contrats → viser le **goodput** (pas le débit brut), **continuous batching** + **prompt caching** du prompt système DORA (attention à l'isolation par tenant), **GQA** pour tenir le KV cache sur de longs contrats, **speculative decoding** pour accélérer les analyses CoT longues.
