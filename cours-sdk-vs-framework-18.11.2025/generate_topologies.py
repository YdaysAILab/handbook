#!/usr/bin/env python3
"""Figure de référence : les 6 topologies de flux (quand LangGraph se mérite).

Génère 6 mini-schémas (diagrams/Graphviz) puis les assemble en une grille 3×2 (PIL)
→ assets/ref-topologies-flux.png — support « 1 slide » pour la séance.

Lancer :  python3 generate_topologies.py
"""
import os
from diagrams import Diagram, Edge
from diagrams.programming.flowchart import Action, Decision, StartEnd, Delay

HERE = os.path.dirname(os.path.abspath(__file__))
TOPO = os.path.join(HERE, "assets", "_topo")
os.makedirs(TOPO, exist_ok=True)

GA = {"fontsize": "22", "labelloc": "t", "pad": "0.3", "bgcolor": "white", "margin": "0.2"}
NA = {"fontsize": "14"}
EA = {"fontsize": "12"}


def topo(name, fn, direction="LR"):
    return Diagram(name, filename=os.path.join(TOPO, fn), show=False, outformat="png",
                   direction=direction, graph_attr=GA, node_attr=NA, edge_attr=EA)


# 1 — Linéaire (ordre fixe connu d'avance) — PAS besoin de LangGraph
with topo("1. Lineaire (ordre fixe)  —  chaine suffit", "1-lineaire"):
    StartEnd("A") >> Action("B") >> Action("C")

# 2 — Branches (conditionnel : un nœud décide la suite)
with topo("2. Branches (conditionnel)", "2-branches"):
    a = Action("A")
    d = Decision("choix")
    a >> d
    d >> Edge(label="oui") >> Action("B")
    d >> Edge(label="non") >> Action("C")

# 3 — Boucle / cycle (répéter jusqu'à condition) — LA raison d'être de LangGraph
with topo("3. Boucle / cycle  ⭐ LangGraph", "3-boucle"):
    a = Action("A")
    b = Action("B")
    d = Decision("fini ?")
    fin = StartEnd("fin")
    a >> b >> d
    d >> Edge(label="non : reboucle") >> a
    d >> Edge(label="oui") >> fin

# 4 — Parallèle (fan-out / fan-in)
with topo("4. Parallele (fan-out / fan-in)", "4-parallele"):
    a = Action("A")
    m = Action("merge")
    for lbl in ("B1", "B2", "B3"):
        a >> Action(lbl) >> m
    m >> Action("C")

# 5 — Interruption + reprise (human-in-the-loop / crash) — LangGraph
with topo("5. Interruption + reprise  (humain / crash)", "5-reprise"):
    a = Action("A")
    b = Action("B")
    pause = Delay("pause\n(humain / crash)")
    c = Action("C")
    a >> b >> pause >> Edge(label="reprise") >> c

# 6 — Dynamique : la suite décidée par le LLM au runtime (boucle agentique)
with topo("6. Dynamique (l'agent decide)", "6-dynamique"):
    llm = Action("LLM")
    tool = Action("outil")
    fin = StartEnd("fini")
    llm >> Edge(label="appelle") >> tool
    tool >> Edge(label="observe") >> llm
    llm >> Edge(label="\"j'ai fini\"") >> fin


# ---- Composition en grille 3×2 avec PIL ----
from PIL import Image  # noqa: E402

def flatten_on_white(path):
    """Aplatit le PNG (fond transparent) sur blanc — sinon convert('RGB') rend le fond NOIR."""
    im = Image.open(path).convert("RGBA")
    bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
    return Image.alpha_composite(bg, im).convert("RGB")


order = ["1-lineaire", "2-branches", "3-boucle", "4-parallele", "5-reprise", "6-dynamique"]
imgs = [flatten_on_white(os.path.join(TOPO, f"{n}.png")) for n in order]

COLS, ROWS = 3, 2
PAD = 28
cell_w = max(im.width for im in imgs)
cell_h = max(im.height for im in imgs)
grid_w = COLS * cell_w + (COLS + 1) * PAD
grid_h = ROWS * cell_h + (ROWS + 1) * PAD
canvas = Image.new("RGB", (grid_w, grid_h), "white")

for i, im in enumerate(imgs):
    r, c = divmod(i, COLS)
    x = PAD + c * (cell_w + PAD) + (cell_w - im.width) // 2
    y = PAD + r * (cell_h + PAD) + (cell_h - im.height) // 2
    canvas.paste(im, (x, y))

out = os.path.join(HERE, "assets", "ref-topologies-flux.png")
canvas.save(out)
print("OK —", out, canvas.size)
