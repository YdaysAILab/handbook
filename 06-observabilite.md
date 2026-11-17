# 06 — Observabilité

> Module 05 — Déployer et fiabiliser. Couche **transversale**.

## P — Problème

Un système IA est **non déterministe** : la même question peut donner des réponses différentes, les coûts varient, les erreurs sont silencieuses (une hallucination ne « plante » pas). Sans visibilité, impossible de déboguer *« pourquoi l'agent DORA a-t-il donné cette réponse ? »*, ni de prouver la qualité, ni de maîtriser les coûts.

## D — Définition

- **Observabilité LLM** : capacité à voir **ce qui se passe à l'intérieur** de chaque requête : prompt exact, documents RAG récupérés, appels d'outils, réponses intermédiaires, tokens, latence, coût.
- **Trace** : l'enregistrement complet d'une exécution (une « span » par étape : retrieval, LLM, tool…).
- **OpenTelemetry (OTel)** : le **standard ouvert et vendor-neutral** d'instrumentation — les trois signaux **traces · métriques · logs**. On **instrumente une seule fois** (SDK ou auto-instrumentation) et on exporte en **OTLP** vers **n'importe quel** backend (Langfuse, Grafana/Tempo, Jaeger, Datadog…) : changer de backend ne force pas à ré-instrumenter. C'est l'inverse d'un SDK propriétaire qui enferme.
- **Conventions sémantiques GenAI** : OTel normalise les **noms d'attributs** d'un appel LLM — `gen_ai.system`, `gen_ai.request.model`, `gen_ai.usage.input_tokens` / `output_tokens`, `temperature`… Grâce à ce vocabulaire commun, les librairies d'auto-instrumentation (OpenLLMetry/Traceloop, OpenInference) émettent et les backends affichent **sans parseur maison**.
- **OTel Collector** : un **point de passage** unique entre vos apps et les backends — c'est là qu'on **batch**, qu'on **échantillonne**, et surtout qu'on **masque les PII** avant export.
- Outils : **Langfuse** (observabilité spécialisée LLM : traces, prompts, évals, coûts — **ingère l'OTLP**), **OpenTelemetry** (le standard d'instrumentation ci-dessus), **Grafana** (dashboards/visualisation + alertes).
- **Coût / licence** : toute la pile est **open-source et gratuite, auto-hébergeable** — OpenTelemetry (Apache 2.0), **Langfuse** (OSS, Docker), Grafana/Tempo/Prometheus (OSS). Elle tourne dans le **même `docker compose`** que le reste, **sans GPU**. C'est la raison même pour laquelle on la préfère à un SaaS type **LangSmith** (exclu : données hors périmètre, coût à l'usage).

## S — Solution

Instrumenter **chaque étape** du workflow avec **OpenTelemetry** (une span par étape, attributs aux conventions GenAI), puis exporter en **OTLP** vers un ou plusieurs backends :
```
Chaque requête → trace OTel {
   span retrieval  (query, docs, scores)
   span llm        (gen_ai.request.model, prompt, réponse, tokens in/out, coût, latence)
   span tool call  (outil, args, résultat, durée)
   span guardrail  (verdicts)
}  → OTel Collector (batch · échantillonnage · masquage PII)
                → Langfuse (traces/évals/coûts LLM) + Grafana (dashboards + alertes)
```
- **traces** pour le debugging requête par requête ;
- **métriques** agrégées : latence p95, taux d'erreur, coût/jour, tokens/requête ;
- **corrélation** avec l'identité utilisateur et l'audit trail ([04](04-securite-gouvernance.md)) ;
- base des **évaluations** ([07](07-llmops-evaluations.md)) et du **FinOps** ([09](09-ai-finops.md)).

### Pile de référence (gratuite, auto-hébergée)

> Squelette **100 % OSS, sans GPU**, dans le même `docker compose` qu'Ollama. Le flux : **app → (OTLP) → OTel Collector (masque les PII) → Langfuse + Tempo/Grafana**.

```yaml
# docker-compose.yml (extrait — à fusionner avec vos services ollama/agent)
services:
  ollama:
    image: ollama/ollama
    ports: ["11434:11434"]

  # --- Instrumentation : point de passage unique ---
  otel-collector:
    image: otel/opentelemetry-collector-contrib:latest
    command: ["--config=/etc/otel/config.yaml"]
    volumes: ["./otel-collector-config.yaml:/etc/otel/config.yaml"]
    ports: ["4317:4317", "4318:4318"]   # OTLP gRPC / HTTP
    depends_on: [langfuse, tempo]

  # --- Backend LLM spécialisé (traces, évals, coûts) ---
  langfuse:
    image: langfuse/langfuse:2           # v2 = minimal (Postgres seul)
    environment:
      DATABASE_URL: postgresql://postgres:postgres@langfuse-db:5432/postgres
      NEXTAUTH_SECRET: changeme
      SALT: changeme
      NEXTAUTH_URL: http://localhost:3000
    ports: ["3000:3000"]
    depends_on: [langfuse-db]
  langfuse-db:
    image: postgres:16
    environment: { POSTGRES_PASSWORD: postgres }

  # --- Backend traces génériques + dashboards ---
  tempo:
    image: grafana/tempo:latest
    command: ["-config.file=/etc/tempo.yaml"]
    volumes:
      - ./tempo.yaml:/etc/tempo.yaml       # config
      - tempo-data:/var/tempo              # persistance des traces/WAL
  grafana:
    image: grafana/grafana:latest
    environment: { GF_AUTH_ANONYMOUS_ENABLED: "true" }   # accès direct en dev
    # Datasource Tempo provisionnée au démarrage (pas de clic manuel)
    volumes:
      - ./grafana-datasources.yaml:/etc/grafana/provisioning/datasources/tempo.yaml
    ports: ["3001:3000"]
    depends_on: [tempo]

volumes:
  tempo-data: {}        # persiste les traces Tempo entre les redémarrages
```

```yaml
# grafana-datasources.yaml — branche Tempo dans Grafana automatiquement
apiVersion: 1
datasources:
  - name: Tempo
    type: tempo
    uid: tempo
    access: proxy
    url: http://tempo:3200        # port HTTP de l'API Tempo
    isDefault: true
    jsonData:
      # chercher les métriques/logs corrélés à une trace (optionnel)
      tracesToLogsV2: { datasourceUid: "tempo" }
```

```yaml
# tempo.yaml — reçoit l'OTLP (du Collector) et sert l'API de requête à Grafana
server:
  http_listen_port: 3200          # API interrogée par la datasource Grafana
distributor:
  receivers:
    otlp:
      protocols:
        grpc: { endpoint: "0.0.0.0:4317" }   # cible de l'exporter otlp/tempo
storage:
  trace:
    backend: local
    local: { path: /var/tempo/traces }
    wal: { path: /var/tempo/wal }
```

```yaml
# otel-collector-config.yaml — masquage PII AVANT export (cf. fiche 23)
receivers:
  otlp:
    protocols: { grpc: {}, http: {} }
processors:
  batch: {}
  # Caviarder emails / IBAN dans les attributs de span avant de sortir du périmètre
  redaction:
    allow_all_keys: true
    blocked_values:
      - '[\w.\-]+@[\w\-]+\.\w+'                 # emails
      - '[A-Z]{2}\d{2}[A-Z0-9]{10,30}'          # IBAN
exporters:
  otlphttp/langfuse:
    endpoint: http://langfuse:3000/api/public/otel   # Langfuse ingère l'OTLP
    headers: { Authorization: "Basic ${LANGFUSE_AUTH}" }  # base64(pk:sk)
  otlp/tempo:
    endpoint: tempo:4317
    tls: { insecure: true }
service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [redaction, batch]
      exporters: [otlphttp/langfuse, otlp/tempo]
```

```python
# app : instrumenter UNE fois, pointer l'OTLP sur le Collector (pas le backend)
# pip install traceloop-sdk   (OpenLLMetry — émet déjà les conventions GenAI)
from traceloop.sdk import Traceloop
Traceloop.init(app_name="dora-agent",
               api_endpoint="http://otel-collector:4318")  # OTLP HTTP
# → vos appels LLM / LangChain / tools sont tracés automatiquement.
# Changer de backend = éditer le Collector, PAS ce code.
```

> **Note :** `langfuse:2` reste minimal (Postgres seul) — idéal pour le cours. La **v3** ajoute ClickHouse/Redis/MinIO : utilisez alors le `docker compose` officiel Langfuse. Le reste (Collector, Tempo, Grafana) ne change pas.

## E — Exemple (DORA)

Un juriste signale : *« L'agent a conclu "pas de risque" sur un contrat qui en avait un. »*
Grâce à la trace Langfuse, on rejoue l'exécution : on voit que le **retrieval** n'a pas remonté l'article DORA pertinent (mauvais chunking) → le LLM a raisonné sans la bonne exigence. On corrige l'ingestion, pas le prompt. Sans observabilité, on aurait tâtonné à l'aveugle.

**Limite / piège :** les traces contiennent des **données sensibles** (contenu des contrats, PII). L'observabilité doit elle-même respecter les ACL et la gouvernance (masquage/rétention).

## Erreurs fréquentes
- Logger seulement l'entrée/sortie finale, pas les étapes intermédiaires → impossible de localiser la cause.
- Pas de corrélation identité ↔ trace → pas d'audit exploitable.
- Stocker les prompts sans masquage PII → nouvelle surface de fuite.
- Métriques sans alertes → on découvre les régressions en production, trop tard.
