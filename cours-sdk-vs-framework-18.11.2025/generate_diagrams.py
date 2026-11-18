#!/usr/bin/env python3
"""Génère un schéma (PNG) par cas pratique de la séance « SDK natif ou framework ? ».

Librairie : mingrammer `diagrams` (+ Graphviz). Vocabulaire neutre (flowchart) :
on représente la FORME du système — flux simple, branches/reprise, intégrations —
sans jamais afficher la réponse (SDK natif / LangChain / LangGraph / n8n…).

Scénarios volontairement « grand public » (boutique, asso, location, freelance,
cabinet, e-commerce) : le domaine parle à tout le monde, l'axe pédagogique reste
identique. Pour I et K, l'image reste DANS LE MENU (pas de gateway/infra).

Lancer :  python3 generate_diagrams.py   →  écrit dans ./assets/*.png
"""
import os
from diagrams import Diagram, Cluster, Edge
from diagrams.custom import Custom
from diagrams.programming.flowchart import (
    Action, Decision, Document, Database, Delay, PredefinedProcess,
    ManualInput, Inspection, MultipleDocuments, Display, StartEnd,
)

# Icônes de marque (PNG) — voir icons/ (OpenAI avatar GitHub, Slack avatar, etc.).
# Chemins ABSOLUS obligatoires : Graphviz ne résout pas les chemins relatifs pour les nœuds image.
_HERE = os.path.dirname(os.path.abspath(__file__))
IC_OPENAI = os.path.join(_HERE, "icons/openai.png")
IC_SLACK = os.path.join(_HERE, "icons/slack.png")
IC_MISTRAL = os.path.join(_HERE, "icons/mistralai.png")
IC_OUTLOOK = os.path.join(_HERE, "icons/outlook.png")
IC_CLAUDE = os.path.join(_HERE, "icons/claude.png")

os.makedirs("assets", exist_ok=True)

GRAPH_ATTR = {"fontsize": "20", "labelloc": "t", "pad": "0.4", "nodesep": "0.5", "ranksep": "0.7", "bgcolor": "white"}
NODE_ATTR = {"fontsize": "13"}
EDGE_ATTR = {"fontsize": "12"}


def diagram(name, filename, direction="LR"):
    return Diagram(
        name, filename=f"assets/{filename}", show=False, direction=direction,
        outformat="png", graph_attr=GRAPH_ATTR, node_attr=NODE_ATTR, edge_attr=EDGE_ATTR,
    )


# Cas A — 50 000 avis d'une boutique en ligne (batch, une passe, pas d'outil/mémoire)
with diagram("Cas A — 50 000 avis d'une boutique à classer (1x/semaine)", "cas-a-batch"):
    src = MultipleDocuments("50 000 avis\n(boutique en ligne)")
    llm = PredefinedProcess("1 appel LLM\n(sortie structurée)")
    out = Document("tableur CSV\n{sentiment, thème}")
    src >> Edge(label="une passe") >> llm >> out

# Cas A′ — même batch, MAIS comparer les modèles par coût/qualité chaque semaine
with diagram("Cas A′ — batch + comparaison des modèles (coût/qualité)", "cas-a2-portable"):
    src = MultipleDocuments("50 000 avis")
    router = Decision("routeur\ncoût / qualité")
    openai = Custom("OpenAI", IC_OPENAI)
    mistral = Custom("Mistral", IC_MISTRAL)
    claude = Custom("Claude Haiku", IC_CLAUDE)
    out = Document("classe\n+ métriques coût/qualité")
    evalw = Inspection("éval hebdo :\ngarde le meilleur")
    src >> router
    router >> openai >> out
    router >> mistral >> out
    router >> claude >> out
    out >> Edge(style="dashed", label="chaque semaine") >> evalw >> Edge(style="dashed") >> router

# Cas B — Démo chatbot d'association (RAG simple, jetable, 4 jours)
with diagram("Cas B — Démo chatbot d'asso (jetable, 4 jours)", "cas-b-proto"):
    q = ManualInput("question\nd'un membre")
    rag = Action("RAG\n30 PDF (statuts…)")
    llm = PredefinedProcess("1 appel LLM")
    rep = Display("réponse")
    q >> rag >> llm >> rep

# Cas C — Dossier de location (stateful, branches, validation humaine, reprise crash)
with diagram("Cas C — Dossier de location (stateful + reprise)", "cas-c-stateful"):
    start = StartEnd("dossier\nde location")
    extr = Action("extraction\n(fiches de paie, pièce ID)")
    score = Action("scoring\ndu dossier")
    dec = Decision("dossier\ndouteux ?")
    human = ManualInput("VALIDATION\nHUMAINE")
    rapport = Document("compte-rendu")
    base = Database("base")
    reprise = Delay("reprise\naprès crash")
    start >> extr >> score >> dec
    dec >> Edge(label="oui") >> human >> rapport
    dec >> Edge(label="non") >> rapport
    rapport >> base
    reprise >> Edge(label="l'état doit survivre", style="dashed") >> score

# Cas D — Même assistant vendu à plusieurs clients (portabilité provider)
with diagram("Cas D — Même assistant, plusieurs clients (portabilité)", "cas-d-portabilite"):
    assistant = Action("assistant\n(même logique)")
    sw = Decision("modèle\nselon le client")
    p1 = Custom("OpenAI", IC_OPENAI)
    p2 = Custom("Mistral / local\n(cloud US interdit)", IC_MISTRAL)
    p3 = PredefinedProcess("??? autre")
    assistant >> sw
    sw >> Edge(label="client 1") >> p1
    sw >> Edge(label="client 2") >> p2
    sw >> Edge(label="client 3") >> p3

# Cas E — Comparatif d'achat (3 rôles qui se passent la main)
with diagram("Cas E — Comparatif d'achat (3 rôles)", "cas-e-roles"):
    with Cluster("3 rôles distincts — sortie de l'un = entrée du suivant"):
        chercheur = Action("Chercheur\n(web)")
        analyste = Action("Analyste\n(compare prix/avis)")
        redacteur = Action("Rédacteur\n(reco)")
        chercheur >> analyste >> redacteur
    rapport = Document("recommandation")
    redacteur >> rapport

# Cas E′ (a) — on AJOUTE un vrai besoin de flux : reboucler + reprise après crash -> LangGraph
with diagram("Cas E′ (a) — reboucler + reprise  →  LangGraph orchestre, rôles en nœuds", "cas-e2a-langgraph"):
    with Cluster("LangGraph : état + branches + reprise"):
        chercheur = Action("Chercheur\n(web)")
        analyste = Action("Analyste")
        redacteur = Action("Rédacteur")
        dec = Decision("comparatif\nsuffisant ?")
        chercheur >> analyste >> redacteur >> dec
        dec >> Edge(label="non : reboucler") >> chercheur
        reprise = Delay("reprise\naprès crash")
        reprise >> Edge(label="l'état survit", style="dashed") >> analyste
    rapport = Document("reco finale")
    dec >> Edge(label="oui") >> rapport

# Cas E′ (b) — l'Analyste appartient à une AUTRE équipe/éditeur : frontière de propriété -> A2A
with diagram("Cas E′ (b) — Analyste d'une autre équipe/éditeur  →  A2A", "cas-e2b-a2a"):
    with Cluster("Notre système"):
        chercheur = Action("Chercheur\n(web)")
        redacteur = Action("Rédacteur")
        rapport = Document("recommandation")
        redacteur >> rapport
    with Cluster("Autre équipe / éditeur (autre système)"):
        analyste = Action("Analyste\n(agent tiers)")
    chercheur >> Edge(label="A2A", color="firebrick", fontcolor="firebrick") >> analyste
    analyste >> Edge(label="A2A", color="firebrick", fontcolor="firebrick") >> redacteur

# Cas F — Automation freelance : email -> tâche -> Slack (intégrations + trigger + planif)
with diagram("Cas F — Email prospect → tâche → Slack (+ relance 48h)", "cas-f-automation"):
    email = Custom("Email prospect\n(déclencheur)", IC_OUTLOOK)
    extr = Action("extraire")
    clas = Action("classer")
    task = PredefinedProcess("tâche\n(Trello / Notion)")
    slack = Custom("notif Slack", IC_SLACK)
    relance = Delay("relance\nsi non traité < 48h")
    email >> extr >> clas >> task >> slack
    task >> Edge(style="dashed") >> relance

# Cas G — Agent en secteur contrôlé (3 outils, 5 ans, audit, 2 devs seniors)
with diagram("Cas G — Agent en secteur contrôlé (audit, 5 ans)", "cas-g-regule"):
    req = ManualInput("requête\n(ex: dossier bancaire)")
    with Cluster("audit : expliquer chaque prompt / décision"):
        agent = PredefinedProcess("agent\n(3 outils)")
    act = Action("action")
    insp = Inspection("traçabilité\n(conformité)")
    req >> agent >> act
    agent >> Edge(style="dashed") >> insp

# Cas H — Le débat (à trancher en groupe)
with diagram("Cas H — Le débat", "cas-h-debat"):
    c1 = ManualInput("Collègue 1 :\n« LangChain PARTOUT »")
    c2 = ManualInput("Collègue 2 :\n« JAMAIS de framework »")
    dec = Decision("Qui a raison ?")
    c1 >> dec
    c2 >> dec

# ---- Exigences « non-fonctionnelles » standard (réponse DANS LE MENU) ----

# Cas I — Observabilité & coût sur plusieurs petits outils IA (obs commune, pas de gateway)
with diagram("Cas I — Observabilité & coût (plusieurs apps IA)", "cas-i-observabilite"):
    with Cluster("4 petits outils IA (résumé réunion, tri CV, support, posts)"):
        a1 = Action("app 1")
        a2 = Action("app 2")
        a3 = Action("app 3")
    obs = PredefinedProcess("callbacks LangChain\n(chaque appel: tokens, coût, latence)")
    traces = Database("traces + coût/équipe\n+ logs d'audit")
    dash = Display("dashboards\nlatence / dépense")
    a1 >> obs
    a2 >> obs
    a3 >> obs
    obs >> Edge(style="dashed", label="chaque appel") >> traces >> dash

# Cas J — Confidentiel / tout en local (aucune API externe, modèle self-hosted)
with diagram("Cas J — Confidentiel / tout en local", "cas-j-souverainete"):
    with Cluster("Cabinet — machine locale (aucune sortie Internet)"):
        app = Action("app\n(SDK natif / n8n self-hosted)")
        model = PredefinedProcess("modèle self-hosted\n(vLLM, OpenAI-compatible)")
        app >> model
    externe = Custom("OpenAI / cloud externe", IC_OPENAI)
    app >> Edge(label="INTERDIT / bloqué", color="firebrick", fontcolor="firebrick", style="dashed") >> externe

# Cas K — Ne jamais tomber : fallback multi-modèle DANS LE CODE (LangChain .with_fallbacks)
with diagram("Cas K — Ne jamais tomber (fallback multi-modèle)", "cas-k-sla"):
    app = Action("assistant e-commerce\n(LangChain)")
    fb = Decision("fallback + retries\n(.with_fallbacks)")
    primary = Custom("OpenAI\n(primaire)", IC_OPENAI)
    secondary = Custom("Mistral\n(secours)", IC_MISTRAL)
    app >> fb
    fb >> Edge(label="nominal") >> primary
    fb >> Edge(label="si panne / rate-limit", color="firebrick", fontcolor="firebrick") >> secondary

print("OK — PNG générés dans ./assets/")
