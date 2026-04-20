
import tkinter as tk
from tkinter import ttk
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

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
}


def _stat_card(parent, title, value, subtitle="", color=None):
    color = color or C["accent"]
    card = tk.Frame(parent, bg=C["surface"],
                    highlightbackground=C["border"],
                    highlightthickness=1)
    card.pack(side="left", fill="both", expand=True, padx=6)

    tk.Label(card, text=title,
             font=(FONT_FAMILY, 8, "bold"),
             bg=C["surface"], fg=C["text_dim"]).pack(padx=14, pady=(14, 4), anchor="w")
    tk.Label(card, text=str(value),
             font=(FONT_FAMILY, 26, "bold"),
             bg=C["surface"], fg=color).pack(padx=14, anchor="w")
    if subtitle:
        tk.Label(card, text=subtitle,
                 font=(FONT_FAMILY, 8),
                 bg=C["surface"], fg=C["text_dim"]).pack(padx=14, pady=(2, 12), anchor="w")


class TeacherDashboard:

    def __init__(self, notebook):
        self.frame = tk.Frame(notebook, bg=C["bg"])
        self._build()

    def _build(self):
        toolbar = tk.Frame(self.frame, bg=C["surface"], height=60)
        toolbar.pack(fill="x")
        toolbar.pack_propagate(False)

        tk.Label(toolbar, text="🧑‍🏫  Teacher Dashboard",
                 font=(FONT_FAMILY, 13, "bold"),
                 bg=C["surface"], fg=C["text"]).pack(side="left", padx=24, pady=0)

        right = tk.Frame(toolbar, bg=C["surface"])
        right.pack(side="right", padx=16)

        for text, cmd in [("Refresh", self._load), ("Export CSV", self._export)]:
            btn = tk.Frame(right, bg=C["accent"], cursor="hand2")
            btn.pack(side="left", padx=4)
            lbl = tk.Label(btn, text=f" {text} ",
                           font=(FONT_FAMILY, 9, "bold"),
                           bg=C["accent"], fg=C["text"],
                           padx=10, pady=6)
            lbl.pack()
            _cmd = cmd
            btn.bind("<Button-1>", lambda _, c=_cmd: c())
            lbl.bind("<Button-1>", lambda _, c=_cmd: c())

        canvas = tk.Canvas(self.frame, bg=C["bg"],
                           highlightthickness=0, bd=0)
        vsb = tk.Scrollbar(self.frame, orient="vertical",
                           command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self._inner = tk.Frame(canvas, bg=C["bg"])
        win = canvas.create_window((0, 0), window=self._inner, anchor="nw")
        canvas.bind("<Configure>",
                    lambda e: canvas.itemconfig(win, width=e.width))
        self._inner.bind("<Configure>",
                         lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))

        self._load()

    def _load(self):
        for w in self._inner.winfo_children():
            w.destroy()

        try:
            from db.mongo_handler import get_recent_n
            df = get_recent_n(200)
            records = df.to_dict(orient="records") if not df.empty else []
        except Exception as e:
            records = []

        self._render(records)

    def _render(self, records):
        total = len(records)
        if total == 0:
            tk.Label(self._inner,
                     text="No student records found in the database.",
                     font=(FONT_FAMILY, 12),
                     bg=C["bg"], fg=C["text_dim"]).pack(pady=60)
            return

        scores = [float(r.get("burnout_score", 0)) for r in records]
        high   = sum(1 for s in scores if s > 0.65)
        mid    = sum(1 for s in scores if 0.4 < s <= 0.65)
        low    = sum(1 for s in scores if s <= 0.4)
        avg    = sum(scores) / total if total else 0

        stats_row = tk.Frame(self._inner, bg=C["bg"])
        stats_row.pack(fill="x", padx=18, pady=(18, 8))
        tk.Frame(stats_row, bg=C["bg"]).pack(side="left")

        _stat_card(stats_row, "TOTAL STUDENTS",  total, "submitted", C["accent"])
        _stat_card(stats_row, "HIGH RISK",        high,  "need attention", C["warn"])
        _stat_card(stats_row, "MODERATE",         mid,   "watch closely",  C["mid"])
        _stat_card(stats_row, "LOW RISK",          low,  "doing well",     C["ok"])
        _stat_card(stats_row, "AVG SCORE", f"{avg:.2f}", "burnout score",  C["accent"])

        charts_row = tk.Frame(self._inner, bg=C["bg"])
        charts_row.pack(fill="x", padx=18, pady=8)

        self._pie_chart(charts_row, high, mid, low)
        self._histogram(charts_row, scores)

        self._risk_table(records)

    def _pie_chart(self, parent, high, mid, low):
        card = tk.Frame(parent, bg=C["surface"],
                        highlightbackground=C["border"],
                        highlightthickness=1)
        card.pack(side="left", fill="both", expand=True, padx=(0, 6))

        with plt.rc_context(MPL_STYLE):
            fig = Figure(figsize=(4, 3.4), dpi=96)
            ax = fig.add_subplot(111)
            vals = [high, mid, low]
            labels = ["High", "Moderate", "Low"]
            colors = [C["warn"], C["mid"], C["ok"]]
            non_zero = [(v, l, c) for v, l, c in zip(vals, labels, colors) if v > 0]
            if non_zero:
                v, l, c = zip(*non_zero)
                ax.pie(v, labels=l, colors=c,
                       autopct="%1.0f%%",
                       pctdistance=0.75,
                       wedgeprops=dict(width=0.55, edgecolor=C["surface"]),
                       textprops=dict(color=C["text"], fontsize=9))
            ax.set_title("Risk Distribution", fontsize=10, pad=8)
            fig.tight_layout()

        FigureCanvasTkAgg(fig, master=card).get_tk_widget().pack(
            fill="both", expand=True, padx=4, pady=4)

    def _histogram(self, parent, scores):
        card = tk.Frame(parent, bg=C["surface"],
                        highlightbackground=C["border"],
                        highlightthickness=1)
        card.pack(side="left", fill="both", expand=True, padx=(6, 0))

        with plt.rc_context(MPL_STYLE):
            fig = Figure(figsize=(5, 3.4), dpi=96)
            ax = fig.add_subplot(111)
            ax.hist(scores, bins=10, range=(0, 1),
                    color=C["accent"], edgecolor=C["surface"],
                    alpha=0.85)
            ax.axvline(0.65, color=C["warn"], linestyle="--", linewidth=1.2, alpha=0.7)
            ax.axvline(0.40, color=C["mid"],  linestyle="--", linewidth=1.2, alpha=0.7)
            ax.set_xlabel("Burnout Score", fontsize=9)
            ax.set_ylabel("Students",       fontsize=9)
            ax.set_title("Score Distribution", fontsize=10)
            ax.grid(axis="y", linestyle="--", alpha=0.3)
            fig.tight_layout()

        FigureCanvasTkAgg(fig, master=card).get_tk_widget().pack(
            fill="both", expand=True, padx=4, pady=4)

    def _risk_table(self, records):
        card = tk.Frame(self._inner, bg=C["surface"],
                        highlightbackground=C["border"],
                        highlightthickness=1)
        card.pack(fill="x", padx=18, pady=(8, 8))

        tk.Label(card, text="⚠️  AT-RISK STUDENTS",
                 font=(FONT_FAMILY, 8, "bold"),
                 bg=C["surface"], fg=C["warn"]).pack(padx=16, pady=(12, 6), anchor="w")

        cols = ("Student ID", "Score", "Risk Level", "Timestamp")
        tree = ttk.Treeview(card, columns=cols, show="headings", height=6)

        style = ttk.Style()
        style.configure("Dark.Treeview",
                         background=C["surface2"],
                         foreground=C["text"],
                         fieldbackground=C["surface2"],
                         rowheight=28)
        style.configure("Dark.Treeview.Heading",
                         background=C["surface"],
                         foreground=C["text_dim"],
                         font=(FONT_FAMILY, 9, "bold"))
        style.map("Dark.Treeview",
                  background=[("selected", C["accent"])])
        tree.configure(style="Dark.Treeview")

        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, anchor="center",
                        width=160 if col == "Timestamp" else 120)

        at_risk = sorted(
            [r for r in records if float(r.get("burnout_score", 0)) > 0.4],
            key=lambda r: float(r.get("burnout_score", 0)),
            reverse=True
        )

        if at_risk:
            for r in at_risk:
                s = float(r.get("burnout_score", 0))
                level = "🔴 High" if s > 0.65 else "🟡 Moderate"
                tree.insert("", "end", values=(
                    r.get("student_id", "—"),
                    f"{s:.2f}",
                    level,
                    str(r.get("timestamp", "—"))[:19],
                ))
        else:
            tree.insert("", "end", values=("—", "—", "No at-risk students", "—"))

        tree.pack(fill="x", padx=12, pady=(0, 12))

        card2 = tk.Frame(self._inner, bg=C["surface"],
                         highlightbackground=C["border"],
                         highlightthickness=1)
        card2.pack(fill="x", padx=18, pady=(0, 24))

        tk.Label(card2, text="✅  DOING WELL",
                 font=(FONT_FAMILY, 8, "bold"),
                 bg=C["surface"], fg=C["ok"]).pack(padx=16, pady=(12, 6), anchor="w")

        tree2 = ttk.Treeview(card2, columns=cols, show="headings", height=6)
        tree2.configure(style="Dark.Treeview")

        for col in cols:
            tree2.heading(col, text=col)
            tree2.column(col, anchor="center",
                         width=160 if col == "Timestamp" else 120)

        doing_well = sorted(
            [r for r in records if float(r.get("burnout_score", 0)) <= 0.4],
            key=lambda r: float(r.get("burnout_score", 0))
        )

        if doing_well:
            for r in doing_well:
                s = float(r.get("burnout_score", 0))
                tree2.insert("", "end", values=(
                    r.get("student_id", "—"),
                    f"{s:.2f}",
                    "🟢 Low Risk",
                    str(r.get("timestamp", "—"))[:19],
                ))
        else:
            tree2.insert("", "end", values=("—", "—", "No low-risk students yet", "—"))

        tree2.pack(fill="x", padx=12, pady=(0, 12))

    def _export(self):
        try:
            from db.mongo_handler import get_recent_n
            import csv, datetime
            df = get_recent_n(500)
            records = df.to_dict(orient="records") if not df.empty else []
            fname = f"burnout_export_{datetime.date.today()}.csv"
            with open(fname, "w", newline="") as f:
                if records:
                    writer = csv.DictWriter(f, fieldnames=records[0].keys())
                    writer.writeheader()
                    writer.writerows(records)
            import tkinter.messagebox
            tk.messagebox.showinfo("Export", f"Saved to {fname}")
        except Exception as e:
            import tkinter.messagebox
            tk.messagebox.showerror("Export Failed", str(e))
