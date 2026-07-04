"""Generates the hand drawn style diagrams for this repo.

Everything is strictly black on white, xkcd style strokes, because a
whiteboard sketch communicates architecture better than a vendor deck.
Run:  python diagrams/make_diagrams.py
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import os

OUT = os.path.dirname(os.path.abspath(__file__))
BLACK = "#111111"

# ship the handwriting font with the repo so the diagrams render the same
# everywhere. plt.xkcd() no longer lists Humor Sans, so register and set it.
_FONT = os.path.join(OUT, "fonts", "Humor-Sans.ttf")
if os.path.exists(_FONT):
    font_manager.fontManager.addfont(_FONT)

def use_hand_font():
    plt.rcParams["font.family"] = ["Humor Sans", "xkcd", "Comic Neue",
                                   "Comic Sans MS", "DejaVu Sans"]


def box(ax, x, y, w, h, label, fs=11, lw=1.6):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                 boxstyle="round,pad=0.06,rounding_size=0.12",
                 fc="white", ec=BLACK, lw=lw))
    ax.text(x + w / 2, y + h / 2, label, ha="center", va="center",
            fontsize=fs, color=BLACK, wrap=True)


def arrow(ax, x1, y1, x2, y2, label=None, fs=9, style="-|>", ls="-"):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style,
                 mutation_scale=16, lw=1.5, color=BLACK, linestyle=ls))
    if label:
        ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 0.15, label,
                ha="center", va="bottom", fontsize=fs, color=BLACK)


def newfig(w=11, h=7.5, title=""):
    use_hand_font()
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")
    if title:
        ax.text(5, 9.6, title, ha="center", va="center",
                fontsize=16, color=BLACK)
    return fig, ax


def save(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=160, bbox_inches="tight",
                facecolor="white")
    plt.close(fig)
    print("wrote", name)


# 1. solution overview -------------------------------------------------
with plt.xkcd(scale=1.1, length=120, randomness=2):
    fig, ax = newfig(title="departmental EGRC service, the big picture")

    # legacy mess on the left
    box(ax, 0.3, 6.6, 2.0, 0.9, "legacy\ntool A", 10)
    box(ax, 0.3, 5.4, 2.0, 0.9, "legacy\ntool B", 10)
    box(ax, 0.3, 4.2, 2.0, 0.9, "CSV piles\n+ shared drives", 9)
    ax.text(1.3, 8.0, "today: three sources,\nzero answers", ha="center",
            fontsize=10, color=BLACK)

    # normalizer funnel
    box(ax, 3.1, 5.3, 1.9, 1.1, "csv\nnormalizer", 10)
    arrow(ax, 2.3, 7.0, 3.2, 6.2)
    arrow(ax, 2.3, 5.8, 3.1, 5.8)
    arrow(ax, 2.3, 4.6, 3.2, 5.4)

    # saas platform layers
    box(ax, 5.6, 2.6, 4.0, 5.2, "", 10)
    ax.text(7.6, 7.4, "GRC SaaS platform", ha="center", fontsize=12, color=BLACK)
    box(ax, 5.9, 6.1, 3.4, 0.8, "instance (vendor owned)", 9)
    box(ax, 5.9, 5.0, 3.4, 0.8, "tenant (ours)", 9)
    box(ax, 5.9, 3.9, 3.4, 0.8, "applications, one per office", 9)
    box(ax, 5.9, 2.8, 3.4, 0.8, "groups: CRUD x 28 modules", 9)
    arrow(ax, 5.0, 5.85, 5.6, 5.4, "migration\nwaves", 9)

    # entra below
    box(ax, 0.8, 0.7, 3.2, 1.3, "Entra ID\nSSO + claim mapped groups", 10)
    arrow(ax, 4.0, 1.4, 5.9, 3.0, "claims -> roles", 9)

    # exec reporting
    box(ax, 7.0, 0.7, 2.6, 1.2, "roll up reporting\nfor leadership", 9)
    arrow(ax, 7.9, 2.6, 8.2, 1.9)
    ax.text(5, 0.2, "target: launch with the first office wave, then repeat",
            ha="center", fontsize=10, color=BLACK)
    save(fig, "solution-overview.png")


# 2. rbac model ---------------------------------------------------------
with plt.xkcd(scale=1.1, length=120, randomness=2):
    fig, ax = newfig(title="the 450 group problem (and the way out)")

    ax.text(2.4, 8.9, "by hand", ha="center", fontsize=13, color=BLACK)
    box(ax, 0.5, 6.7, 3.8, 1.6,
        "3 roles x 50 apps x 3 envs\n= 450 groups + 450 roles\nin two systems", 10)
    box(ax, 0.5, 4.6, 3.8, 1.4, "clicked in a console\nby a tired human", 10)
    box(ax, 0.5, 2.5, 3.8, 1.4, "drift, typos,\naudit findings", 10)
    arrow(ax, 2.4, 6.7, 2.4, 6.0)
    arrow(ax, 2.4, 4.6, 2.4, 3.9)

    ax.text(7.4, 8.9, "generated", ha="center", fontsize=13, color=BLACK)
    box(ax, 5.6, 6.9, 3.6, 1.2, "6 role templates\n(yaml, version controlled)", 10)
    box(ax, 5.6, 5.0, 3.6, 1.2, "provisioner derives every name:\nGRC-ENV-APP-ROLE", 9)
    box(ax, 5.6, 3.1, 3.6, 1.2, "change request package\n-> directory team applies", 9)
    box(ax, 5.6, 1.2, 3.6, 1.2, "drift check verifies,\non a schedule, forever", 9)
    arrow(ax, 7.4, 6.9, 7.4, 6.2)
    arrow(ax, 7.4, 5.0, 7.4, 4.3)
    arrow(ax, 7.4, 3.1, 7.4, 2.4)

    ax.text(2.4, 1.4, "humans maintain intent,\nmachines maintain IDs",
            ha="center", fontsize=10, color=BLACK, style="italic")
    save(fig, "rbac-model.png")


# 3. data segregation ---------------------------------------------------
with plt.xkcd(scale=1.1, length=120, randomness=2):
    fig, ax = newfig(title="one site's data must not roll up")

    box(ax, 3.4, 7.3, 3.2, 1.3, "HQ roll up\nreporting", 11)

    box(ax, 0.6, 4.0, 2.6, 1.6, "SITE-ALPHA\nREPORTABLE\n(app 1)", 10)
    box(ax, 6.8, 4.0, 2.6, 1.6, "SITE-ALPHA\nRESTRICTED\n(app 2)", 10)

    arrow(ax, 1.9, 5.6, 4.2, 7.3, "rolls up", 9)
    # blocked arrow
    ax.add_patch(FancyArrowPatch((8.1, 5.6), (5.9, 7.3), arrowstyle="-|>",
                 mutation_scale=16, lw=1.5, color=BLACK, linestyle="--"))
    ax.text(7.6, 6.7, "never", fontsize=11, color=BLACK)
    ax.plot([6.6, 7.2], [6.2, 6.8], color=BLACK, lw=2.4)
    ax.plot([6.6, 7.2], [6.8, 6.2], color=BLACK, lw=2.4)

    box(ax, 0.6, 1.6, 4.2, 1.5,
        "same site, one workflow,\ntwo containers until vendor\nhierarchy ships", 9)
    box(ax, 5.6, 1.6, 3.9, 1.5,
        "tenant admins CAN see both.\nno setting fixes that. so:\nfew admins, logged, reviewed,\nrisk signed by the site", 8)
    arrow(ax, 8.1, 4.0, 7.7, 3.1)

    ax.text(5, 0.6, "honesty is a compensating control", ha="center",
            fontsize=11, color=BLACK, style="italic")
    save(fig, "data-segregation.png")


# 4. entra sync flow ----------------------------------------------------
with plt.xkcd(scale=1.1, length=120, randomness=2):
    fig, ax = newfig(title="provision by change request, verify by drift")

    box(ax, 0.4, 7.4, 2.4, 1.2, "1. PLAN\nderive all names", 10)
    box(ax, 3.8, 7.4, 2.4, 1.2, "2. PACKAGE\ncsv + json + summary", 9)
    box(ax, 7.2, 7.4, 2.4, 1.2, "3. REVIEW\ndirectory team", 10)
    arrow(ax, 2.8, 8.0, 3.8, 8.0)
    arrow(ax, 6.2, 8.0, 7.2, 8.0)

    box(ax, 7.2, 4.9, 2.4, 1.2, "4. APPLY\ntheir tooling,\ntheir directory", 9)
    arrow(ax, 8.4, 7.4, 8.4, 6.1)

    box(ax, 3.8, 4.9, 2.4, 1.2, "5. DRIFT CHECK\nexpected vs actual", 9)
    arrow(ax, 7.2, 5.5, 6.2, 5.5)

    box(ax, 0.4, 4.9, 2.4, 1.2, "6. TEMPLATER\napply CRUD sets", 9)
    arrow(ax, 3.8, 5.5, 2.8, 5.5)

    box(ax, 2.4, 2.0, 5.2, 1.4,
        "every run leaves a timestamped artifact\n= continuous monitoring evidence (AC-2, CA-7)", 9)
    arrow(ax, 5.0, 4.9, 5.0, 3.4)

    ax.text(5, 0.9, "we never ask for keys to their directory.\nwe make their fifteen minutes easy instead.",
            ha="center", fontsize=10, color=BLACK, style="italic")
    save(fig, "entra-sync.png")

print("done")
