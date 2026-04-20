import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os

C = {
    "bg":          "#0D0A0A",
    "surface":     "#1A1010",
    "surface2":    "#241515",
    "border":      "#3D2020",
    "accent":      "#C0392B",
    "accent_glow": "#4E46D4",
    "warn":        "#E74C3C",
    "ok":          "#2ECC71",
    "mid":         "#E67E22",
    "text":        "#F0E6E6",
    "text_dim":    "#8A7070",
    "gold":        "#D4A017",
    "gold_dim":    "#8A6810",
}
FONT_FAMILY = "Segoe UI"


def _risk_color(label: str) -> str:
    l = label.lower()
    if "high" in l or "severe" in l:
        return C["warn"]
    if "medium" in l or "moderate" in l:
        return C["mid"]
    return C["ok"]


class ResultsTab:

    def __init__(self, notebook):
        self.frame = tk.Frame(notebook, bg=C["bg"])
        self._placeholder()

    def _placeholder(self):
        for w in self.frame.winfo_children():
            w.destroy()

        ph = tk.Frame(self.frame, bg=C["bg"])
        ph.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(ph, text="📋",
                 font=(FONT_FAMILY, 48),
                 bg=C["bg"], fg=C["border"]).pack()
        tk.Label(ph, text="Submit the form to see your burnout analysis",
                 font=(FONT_FAMILY, 13),
                 bg=C["bg"], fg=C["text_dim"]).pack(pady=8)

    def update(self, result: dict, form_data: dict, mood_result=None):
        for w in self.frame.winfo_children():
            w.destroy()

        if "error" in result:
            self._show_error(result["error"])
            return

        canvas = tk.Canvas(self.frame, bg=C["bg"],
                           highlightthickness=0, bd=0)
        vsb = tk.Scrollbar(self.frame, orient="vertical",
                           command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        inner = tk.Frame(canvas, bg=C["bg"])
        win = canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.bind("<Configure>",
                    lambda e: canvas.itemconfig(win, width=e.width))
        inner.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))

        self._build_results(inner, result, form_data, mood_result)

    def _build_results(self, parent, result, form_data, mood_result):
        sid    = form_data.get("student_id", "—")
        label  = result.get("risk_label", result.get("prediction", "Unknown"))
        score  = result.get("burnout_score", result.get("confidence", None))
        models = result.get("model_scores", {})

        color  = _risk_color(str(label))

        banner = tk.Frame(parent, bg=C["surface"], height=100)
        banner.pack(fill="x")
        banner.pack_propagate(False)

        tk.Label(banner,
                 text=f"Results for  {sid}",
                 font=(FONT_FAMILY, 11),
                 bg=C["surface"], fg=C["text_dim"]).pack(pady=(14, 0))

        tk.Label(banner,
                 text=str(label).upper(),
                 font=(FONT_FAMILY, 20, "bold"),
                 bg=C["surface"], fg=color).pack()

        if score is not None:
            self._score_ring(parent, float(score), color)

        if models:
            self._model_bars(parent, models)

        self._summary_grid(parent, form_data)

        if mood_result:
            self._mood_section(parent, mood_result)

        shap_path = "visuals/shap_live.png"
        if os.path.exists(shap_path):
            self._shap_section(parent, shap_path)

        tk.Frame(parent, height=32, bg=C["bg"]).pack()

    def _score_ring(self, parent, score, color):
        card = tk.Frame(parent, bg=C["surface"],
                        highlightbackground=C["border"],
                        highlightthickness=1)
        card.pack(fill="x", padx=24, pady=(16, 8))

        tk.Label(card, text="BURNOUT SCORE",
                 font=(FONT_FAMILY, 8, "bold"),
                 bg=C["surface"], fg=C["text_dim"]).pack(pady=(12, 4))

        pct = min(max(int(score * 100), 0), 100)

        c = tk.Canvas(card, width=160, height=160,
                      bg=C["surface"], highlightthickness=0)
        c.pack(pady=8)

        c.create_arc(20, 20, 140, 140, start=225, extent=-270,
                     style="arc", outline=C["border"], width=14)
        extent = -int(270 * score)
        c.create_arc(20, 20, 140, 140, start=225, extent=extent,
                     style="arc", outline=color, width=14)
        c.create_text(80, 80, text=f"{pct}%",
                      font=(FONT_FAMILY, 22, "bold"), fill=color)
        c.create_text(80, 110, text="risk score",
                      font=(FONT_FAMILY, 9), fill=C["text_dim"])

        tk.Frame(card, height=12, bg=C["surface"]).pack()

    def _model_bars(self, parent, models):
        card = tk.Frame(parent, bg=C["surface"],
                        highlightbackground=C["border"],
                        highlightthickness=1)
        card.pack(fill="x", padx=24, pady=8)

        tk.Label(card, text="MODEL CONFIDENCE",
                 font=(FONT_FAMILY, 8, "bold"),
                 bg=C["surface"], fg=C["text_dim"]).pack(padx=16, pady=(12, 6), anchor="w")

        for name, val in models.items():
            row = tk.Frame(card, bg=C["surface"])
            row.pack(fill="x", padx=16, pady=4)

            tk.Label(row, text=name, width=18, anchor="w",
                     font=(FONT_FAMILY, 9),
                     bg=C["surface"], fg=C["text"]).pack(side="left")

            bar_bg = tk.Frame(row, bg=C["border"],
                              height=10)
            bar_bg.pack(side="left", fill="x", expand=True, padx=(4, 8))
            bar_bg.pack_propagate(False)

            pct = float(val)
            col = _risk_color("high" if pct > 0.65 else ("medium" if pct > 0.4 else "low"))
            bar_fill = tk.Frame(bar_bg, bg=col, height=10)
            bar_fill.place(relx=0, rely=0, relheight=1, relwidth=pct)

            tk.Label(row, text=f"{int(pct*100)}%",
                     font=(FONT_FAMILY, 9, "bold"),
                     bg=C["surface"], fg=col, width=5).pack(side="left")

        tk.Frame(card, height=12, bg=C["surface"]).pack()

    def _summary_grid(self, parent, form_data):
        card = tk.Frame(parent, bg=C["surface"],
                        highlightbackground=C["border"],
                        highlightthickness=1)
        card.pack(fill="x", padx=24, pady=8)

        tk.Label(card, text="SUBMITTED DATA",
                 font=(FONT_FAMILY, 8, "bold"),
                 bg=C["surface"], fg=C["text_dim"]).pack(padx=16, pady=(12, 6), anchor="w")

        grid = tk.Frame(card, bg=C["surface"])
        grid.pack(fill="x", padx=16, pady=(0, 12))

        skip = {"student_id", "mood_text"}
        items = [(k.replace("_", " ").title(), str(v))
                 for k, v in form_data.items() if k not in skip]

        for i, (k, v) in enumerate(items):
            r, c2 = divmod(i, 2)
            cell = tk.Frame(grid, bg=C["surface2"],
                            highlightbackground=C["border"],
                            highlightthickness=1)
            cell.grid(row=r, column=c2, padx=4, pady=3, sticky="nsew")
            grid.columnconfigure(c2, weight=1)

            tk.Label(cell, text=k,
                     font=(FONT_FAMILY, 8),
                     bg=C["surface2"], fg=C["text_dim"],
                     anchor="w", padx=10, pady=2).pack(fill="x")
            tk.Label(cell, text=v,
                     font=(FONT_FAMILY, 10, "bold"),
                     bg=C["surface2"], fg=C["text"],
                     anchor="w", padx=10, pady=4).pack(fill="x")

    def _mood_section(self, parent, mood: dict):
        card = tk.Frame(parent, bg=C["surface"],
                        highlightbackground=C["border"],
                        highlightthickness=1)
        card.pack(fill="x", padx=24, pady=8)

        tk.Label(card, text="MOOD SENTIMENT",
                 font=(FONT_FAMILY, 8, "bold"),
                 bg=C["surface"], fg=C["text_dim"]).pack(padx=16, pady=(12, 6), anchor="w")

        row = tk.Frame(card, bg=C["surface"])
        row.pack(fill="x", padx=16, pady=(0, 12))

        compound = mood.get("compound", 0)
        if compound >= 0.05:
            label, col = "Positive 😊", C["ok"]
        elif compound <= -0.05:
            label, col = "Negative 😟", C["warn"]
        else:
            label, col = "Neutral 😐", C["mid"]

        tk.Label(row, text=label,
                 font=(FONT_FAMILY, 14, "bold"),
                 bg=C["surface"], fg=col).pack(side="left")
        tk.Label(row, text=f"  compound: {compound:.3f}",
                 font=(FONT_FAMILY, 9),
                 bg=C["surface"], fg=C["text_dim"]).pack(side="left", pady=6)

    def _shap_section(self, parent, path):
        card = tk.Frame(parent, bg=C["surface"],
                        highlightbackground=C["border"],
                        highlightthickness=1)
        card.pack(fill="x", padx=24, pady=8)

        tk.Label(card, text="SHAP FEATURE IMPORTANCE",
                 font=(FONT_FAMILY, 8, "bold"),
                 bg=C["surface"], fg=C["text_dim"]).pack(padx=16, pady=(12, 6), anchor="w")

        try:
            img = Image.open(path)
            img.thumbnail((700, 400))
            photo = ImageTk.PhotoImage(img)
            lbl = tk.Label(card, image=photo, bg=C["surface"])
            lbl.image = photo
            lbl.pack(padx=16, pady=(0, 12))
        except Exception as e:
            tk.Label(card, text=f"Could not load SHAP image: {e}",
                     font=(FONT_FAMILY, 9),
                     bg=C["surface"], fg=C["warn"]).pack(padx=16, pady=12)

    def _show_error(self, msg):
        ph = tk.Frame(self.frame, bg=C["bg"])
        ph.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(ph, text="⚠️",
                 font=(FONT_FAMILY, 40),
                 bg=C["bg"], fg=C["warn"]).pack()
        tk.Label(ph, text=f"Prediction error:\n{msg}",
                 font=(FONT_FAMILY, 11),
                 bg=C["bg"], fg=C["text_dim"],
                 justify="center").pack(pady=8)
