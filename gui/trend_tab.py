
import tkinter as tk
from tkinter import ttk
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np

C = {
    "bg":          "#0D0A0A",
    "surface":     "#1A1010",
    "surface2":    "#241515",
    "border":      "#3D2020",
    "accent":      "#C0392B",
    "warn":        "#E74C3C",
    "ok":          "#2ECC71",
    "mid":         "#E67E22",
    "text":        "#F0E6E6",
    "text_dim":    "#8A7070",
    "gold":        "#D4A017",
    "gold_dim":    "#8A6810",
}
FONT_FAMILY = "Segoe UI"
MPL_STYLE = {
    "figure.facecolor":  C["surface"],
    "axes.facecolor":    C["surface"],
    "axes.edgecolor":    C["border"],
    "axes.labelcolor":   C["text_dim"],
    "xtick.color":       C["text_dim"],
    "ytick.color":       C["text_dim"],
    "grid.color":        C["border"],
    "text.color":        C["text"],
    "lines.linewidth":   2.5,
}


class TrendTab:

    def __init__(self, notebook):
        self.frame = tk.Frame(notebook, bg=C["bg"])
        self._build()

    def _build(self):
        # ── toolbar ──────────────────────────────────────────
        toolbar = tk.Frame(self.frame, bg=C["surface"], height=60)
        toolbar.pack(fill="x")
        toolbar.pack_propagate(False)

        tk.Label(toolbar, text="📈  Trend Tracker",
                 font=(FONT_FAMILY, 13, "bold"),
                 bg=C["surface"], fg=C["text"]).pack(side="left", padx=24, pady=0)

        # Student ID entry
        right = tk.Frame(toolbar, bg=C["surface"])
        right.pack(side="right", padx=16)

        tk.Label(right, text="Student ID:",
                 font=(FONT_FAMILY, 9),
                 bg=C["surface"], fg=C["text_dim"]).pack(side="left", padx=(0, 6))

        self._sid_var = tk.StringVar(value="STU001")
        entry = tk.Entry(right, textvariable=self._sid_var,
                         font=(FONT_FAMILY, 10),
                         bg=C["surface2"], fg=C["text"],
                         insertbackground=C["text"],
                         relief="flat", width=14, bd=0)
        entry.pack(side="left", ipady=5)

        # Refresh button
        btn = tk.Frame(right, bg=C["accent"], cursor="hand2")
        btn.pack(side="left", padx=(8, 0))
        lbl = tk.Label(btn, text=" Refresh ",
                        font=(FONT_FAMILY, 9, "bold"),
                        bg=C["accent"], fg=C["text"],
                        padx=10, pady=6)
        lbl.pack()
        btn.bind("<Button-1>", lambda _: self._refresh())
        lbl.bind("<Button-1>", lambda _: self._refresh())
        btn.bind("<Enter>", lambda _: btn.configure(bg="#4E46D4") or lbl.configure(bg="#4E46D4"))
        btn.bind("<Leave>", lambda _: btn.configure(bg=C["accent"]) or lbl.configure(bg=C["accent"]))

        # ── chart area ───────────────────────────────────────
        self._chart_frame = tk.Frame(self.frame, bg=C["bg"])
        self._chart_frame.pack(fill="both", expand=True, padx=24, pady=16)

        self._draw_placeholder()

    def _draw_placeholder(self):
        for w in self._chart_frame.winfo_children():
            w.destroy()

        ph = tk.Label(self._chart_frame,
                      text="Enter a Student ID and click Refresh\nto see their burnout trend over time.",
                      font=(FONT_FAMILY, 12),
                      bg=C["bg"], fg=C["text_dim"],
                      justify="center")
        ph.place(relx=0.5, rely=0.5, anchor="center")

    def _refresh(self):
        sid = self._sid_var.get().strip()
        if not sid:
            return

        try:
            from db.mongo_handler import get_all_by_student
            df = get_all_by_student(sid)
            if df is None or df.empty:
                self._draw_placeholder()
                return
            records = df.to_dict(orient="records")
        except Exception as e:
            self._show_error(str(e))
            return

        if not records:
            self._draw_placeholder()
            return

        self._draw_chart(records, sid)

    def _draw_chart(self, records, sid):
        for w in self._chart_frame.winfo_children():
            w.destroy()

        scores = [r.get("burnout_score", 0) for r in records]
        dates  = [str(r.get("timestamp", i))[:10] for i, r in enumerate(records)]

        with plt.rc_context(MPL_STYLE):
            fig = Figure(figsize=(10, 5), dpi=96)
            ax = fig.add_subplot(111)

            xs = range(len(scores))

            # gradient fill under curve
            ax.fill_between(xs, scores,
                            alpha=0.15, color=C["accent"])

            # colour-coded line segments
            for i in range(len(scores)-1):
                mid = (scores[i] + scores[i+1]) / 2
                col = C["warn"] if mid > 0.65 else (C["mid"] if mid > 0.4 else C["ok"])
                ax.plot([xs[i], xs[i+1]], [scores[i], scores[i+1]],
                        color=col, linewidth=2.5)

            # dots
            for i, s in enumerate(scores):
                col = C["warn"] if s > 0.65 else (C["mid"] if s > 0.4 else C["ok"])
                ax.scatter([i], [s], color=col, zorder=5, s=60)

            ax.set_xticks(list(xs))
            ax.set_xticklabels(dates, rotation=30, ha="right", fontsize=8)
            ax.set_ylim(0, 1)
            ax.set_ylabel("Burnout Score", fontsize=9)
            ax.set_title(f"Burnout Trend  —  {sid}", fontsize=11, pad=12)
            ax.grid(axis="y", linestyle="--", alpha=0.4)
            ax.axhline(0.65, color=C["warn"],  linestyle="--", alpha=0.5, linewidth=1)
            ax.axhline(0.40, color=C["mid"],   linestyle="--", alpha=0.5, linewidth=1)

            legend = [
                mpatches.Patch(color=C["warn"], label="High risk"),
                mpatches.Patch(color=C["mid"],  label="Moderate"),
                mpatches.Patch(color=C["ok"],   label="Low risk"),
            ]
            ax.legend(handles=legend, loc="upper left",
                      facecolor=C["surface2"], edgecolor=C["border"],
                      labelcolor=C["text"], fontsize=8)

            fig.tight_layout()

        chart = FigureCanvasTkAgg(fig, master=self._chart_frame)
        chart.draw()
        chart.get_tk_widget().pack(fill="both", expand=True)

    def _show_error(self, msg):
        for w in self._chart_frame.winfo_children():
            w.destroy()
        tk.Label(self._chart_frame,
                 text=f"⚠️  Could not load data:\n{msg}",
                 font=(FONT_FAMILY, 10),
                 bg=C["bg"], fg=C["warn"],
                 justify="center").place(relx=0.5, rely=0.5, anchor="center")
