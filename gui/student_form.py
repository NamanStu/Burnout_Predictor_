import tkinter as tk
from tkinter import ttk, font as tkfont
import re

C = {
    "bg":          "#0D0A0A",   # near-black canvas
    "surface":     "#1A1010",   # card background
    "surface2":    "#241515",   # slightly lighter card
    "border":      "#3D2020",   # subtle border
    "accent":      "#C0392B",   # purple accent
    "accent_glow": "#8B1A1A",   # darker for hover
    "warn":        "#E74C3C",   # danger / high burnout
    "ok":          "#2ECC71",   # success / low burnout
    "mid":         "#E67E22",   # warning / medium burnout
    "text":        "#000000",   # primary text
    "text_dim":    "#8A7070",
    "gold":        "#D4A017",
    "gold_dim":    "#8A6810",   # muted text
    "slider_bg":   "#3D2020",
    "slider_fill": "#C0392B",
}

FONT_FAMILY = "Segoe UI"


def make_label(parent, text, size=10, bold=False, color=None, **kw):
    weight = "bold" if bold else "normal"
    color = color or C["text"]
    return tk.Label(parent, text=text,
                    font=(FONT_FAMILY, size, weight),
                    bg=parent["bg"], fg=color, **kw)


def section_header(parent, text):
    """Draws a coloured pill-label section divider."""
    frame = tk.Frame(parent, bg=C["bg"])
    frame.pack(fill="x", padx=24, pady=(18, 6))

    pill = tk.Frame(frame, bg=C["surface2"], bd=0, highlightthickness=0)
    pill.pack(fill="x")

    # colour bar on the left
    bar = tk.Frame(pill, width=4, bg=C["accent"])
    bar.pack(side="left", fill="y")

    lbl = tk.Label(pill, text=text.upper(),
                   font=(FONT_FAMILY, 8, "bold"),
                   bg=C["surface2"], fg=C["accent"],
                   padx=12, pady=6)
    lbl.pack(side="left")
    return frame


class GlowButton(tk.Frame):
    """A hover-colour button using Frame+Label (avoids Canvas TclError on MS Store Python)."""

    def __init__(self, parent, text, command=None,
                 width=220, height=44,
                 color=C["accent"], hover=C["accent_glow"],
                 text_color=C["text"], radius=10, **kw):
        kw.pop("width", None)
        kw.pop("height", None)
        super().__init__(parent, bg=color, cursor="hand2", **kw)
        self._cmd = command
        self._col = color
        self._hov = hover

        self._lbl = tk.Label(self, text=text,
                             font=(FONT_FAMILY, 11, "bold"),
                             bg=color, fg=text_color,
                             padx=20, pady=10)
        self._lbl.pack(expand=True, fill="both")

        for w in (self, self._lbl):
            w.bind("<Enter>",    self._on_enter)
            w.bind("<Leave>",    self._on_leave)
            w.bind("<Button-1>", self._on_click)

    def _on_enter(self, _):
        self.configure(bg=self._hov)
        self._lbl.configure(bg=self._hov)

    def _on_leave(self, _):
        self.configure(bg=self._col)
        self._lbl.configure(bg=self._col)

    def _on_click(self, _):
        if self._cmd:
            self._cmd()


class ModernSlider(tk.Frame):
    """Label + custom scale + live value badge."""

    def __init__(self, parent, label, from_, to, default=None,
                 integer=True, unit="", **kw):
        super().__init__(parent, bg=C["bg"], **kw)
        self._var = tk.DoubleVar(value=default if default is not None else (from_+to)//2)
        self._int = integer
        self._unit = unit

        # ---- row ----
        row = tk.Frame(self, bg=C["bg"])
        row.pack(fill="x", padx=24, pady=(6, 2))

        # label
        tk.Label(row, text=label,
                 font=(FONT_FAMILY, 10),
                 bg=C["bg"], fg=C["text_dim"],
                 anchor="w", width=26).pack(side="left")

        # value badge
        self._badge = tk.Label(row, text=self._fmt(),
                               font=(FONT_FAMILY, 10, "bold"),
                               bg=C["surface2"], fg=C["accent"],
                               width=5, anchor="center",
                               relief="flat", padx=4, pady=2)
        self._badge.pack(side="right")

        # scale
        tk.Scale(self, from_=from_, to=to,
                 orient="horizontal",
                 variable=self._var,
                 showvalue=False,
                 resolution=1 if integer else 0.1,
                 bg=C["bg"],
                 troughcolor=C["slider_bg"],
                 activebackground=C["accent"],
                 highlightthickness=0,
                 sliderrelief="flat",
                 bd=0,
                 command=self._on_change).pack(fill="x", padx=24, pady=(0, 4))

    def _fmt(self):
        v = self._var.get()
        if self._int:
            return f"{int(v)}{self._unit}"
        return f"{v:.1f}{self._unit}"

    def _on_change(self, _=None):
        self._badge.config(text=self._fmt())

    def get(self):
        v = self._var.get()
        return int(v) if self._int else round(v, 1)


class ModernDropdown(tk.Frame):
    """Label + styled combobox row."""

    def __init__(self, parent, label, options, default=0, **kw):
        super().__init__(parent, bg=C["bg"], **kw)
        self._var = tk.StringVar(value=options[default])

        row = tk.Frame(self, bg=C["bg"])
        row.pack(fill="x", padx=24, pady=(6, 6))

        tk.Label(row, text=label,
                 font=(FONT_FAMILY, 10),
                 bg=C["bg"], fg=C["text_dim"],
                 anchor="w", width=26).pack(side="left")

        style = ttk.Style()
        style.configure("Modern.TCombobox",
                         fieldbackground=C["surface2"],
                         background=C["surface2"],
                         foreground=C["text"],
                         arrowcolor=C["accent"],
                         borderwidth=0,
                         relief="flat",
                         padding=6)

        cb = ttk.Combobox(row, textvariable=self._var,
                          values=options, state="readonly",
                          style="Modern.TCombobox",
                          width=22)
        cb.pack(side="right")

    def get(self):
        return self._var.get()


class StudentFormTab:
    """
    Redesigned Student Form Tab.
    Compatible with the original on_result(result, form_data, mood_result) callback.
    """

    def __init__(self, notebook, on_result=None):
        self.on_result = on_result

        # ── root frame ──────────────────────────────────
        self.frame = tk.Frame(notebook, bg=C["bg"])
        self.frame.pack(fill="both", expand=True)

        self._build_header()
        self._build_body()

    def _build_header(self):
        hdr = tk.Frame(self.frame, bg=C["surface"], height=72)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        left = tk.Frame(hdr, bg=C["surface"])
        left.pack(side="left", padx=28, pady=0, fill="y")

        # The white text you wanted
        tk.Label(left, text="🔥  Student Burnout Assessment",
                 font=(FONT_FAMILY, 15, "bold"),
                 bg=C["surface"], fg="#FFFFFF").pack(side="left", pady=22)

        right = tk.Frame(hdr, bg=C["surface"])
        right.pack(side="right", padx=28, pady=0, fill="y")

        # Student ID Label in white
        tk.Label(right, text="Student ID",
                 font=(FONT_FAMILY, 9),
                 bg=C["surface"], fg="#FFFFFF").pack(side="left", pady=22, padx=(0, 8))

        self._id_var = tk.StringVar(value="STU001")
        id_entry = tk.Entry(right,
                            textvariable=self._id_var,
                            font=(FONT_FAMILY, 11, "bold"),
                            bg=C["surface2"], fg="#FFFFFF",
                            insertbackground="#FFFFFF",
                            relief="flat",
                            width=14,
                            bd=0)
        id_entry.pack(side="left", pady=22, ipady=6, padx=4)

    def _build_body(self):
        outer = tk.Frame(self.frame, bg=C["bg"])
        outer.pack(fill="both", expand=True)

        canvas = tk.Canvas(outer, bg=C["bg"],
                           highlightthickness=0, bd=0)
        vsb = tk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)

        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        inner = tk.Frame(canvas, bg=C["bg"])
        win_id = canvas.create_window((0, 0), window=inner, anchor="nw")

        def _resize(event):
            canvas.itemconfig(win_id, width=event.width)

        canvas.bind("<Configure>", _resize)
        inner.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))

        left_col  = tk.Frame(inner, bg=C["bg"])
        right_col = tk.Frame(inner, bg=C["bg"])
        left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 4))
        right_col.grid(row=0, column=1, sticky="nsew", padx=(4, 0))
        inner.columnconfigure(0, weight=1)
        inner.columnconfigure(1, weight=1)

        self._build_left(left_col)
        self._build_right(right_col)

        bar = tk.Frame(self.frame, bg=C["surface"], height=70)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)

        btn = GlowButton(bar, "⚡  Predict Burnout Risk",
                         command=self._submit,
                         width=260, height=44)
        btn.pack(side="left", padx=28, pady=13)

        self._status = tk.Label(bar, text="Fill in the form and click Predict",
                                font=(FONT_FAMILY, 9),
                                bg=C["surface"], fg=C["text_dim"])
        self._status.pack(side="left", padx=12)

    def _build_left(self, parent):
        section_header(parent, "👤  Personal Information")
        card = tk.Frame(parent, bg=C["surface"],
                        highlightbackground=C["border"],
                        highlightthickness=1)
        card.pack(fill="x", padx=24, pady=(0, 8))

        self._age       = ModernSlider(card, "Age",           18, 30, 21)
        self._age.pack(fill="x")

        self._gender    = ModernDropdown(card, "Gender",
                                         ["Male", "Female", "Non-binary", "Prefer not to say"])
        self._gender.pack(fill="x")

        self._course    = ModernDropdown(card, "Course",
                                         ["BTech", "MTech", "BCA", "MCA",
                                          "BSc", "MSc", "MBA", "Other"])
        self._course.pack(fill="x")

        self._semester  = ModernSlider(card, "Semester (1–8)", 1, 8, 4)
        self._semester.pack(fill="x")

        tk.Frame(card, height=8, bg=C["surface"]).pack()

        section_header(parent, "📚  Academic Load")
        card2 = tk.Frame(parent, bg=C["surface"],
                         highlightbackground=C["border"],
                         highlightthickness=1)
        card2.pack(fill="x", padx=24, pady=(0, 8))

        self._study     = ModernSlider(card2, "Study Hours / Day",  0, 14, 6, unit="h")
        self._study.pack(fill="x")

        self._assign_p  = ModernSlider(card2, "Assignment Pressure", 1, 10, 5)
        self._assign_p.pack(fill="x")

        self._exam_p    = ModernSlider(card2, "Exam Pressure",      1, 10, 5)
        self._exam_p.pack(fill="x")

        self._attend_s  = ModernSlider(card2, "Attendance Stress",  1, 10, 5)
        self._attend_s.pack(fill="x")

        tk.Frame(card2, height=8, bg=C["surface"]).pack()

        section_header(parent, "💬  Mood Journal  (optional)")
        card3 = tk.Frame(parent, bg=C["surface"],
                         highlightbackground=C["border"],
                         highlightthickness=1)
        card3.pack(fill="x", padx=24, pady=(0, 16))

        self._mood = tk.Text(card3, height=5,
                             font=(FONT_FAMILY, 10),
                             bg=C["surface2"], fg="#FFFFFF",
                             insertbackground=C["text"],
                             relief="flat", bd=0,
                             wrap="word",
                             padx=12, pady=10)
        self._mood.pack(fill="x", padx=12, pady=10)
        self._mood.insert("1.0",
                          "Describe how you've been feeling lately…")
        self._mood.bind("<FocusIn>",  self._clear_placeholder)
        self._mood.bind("<FocusOut>", self._restore_placeholder)
        self._PLACEHOLDER = "Describe how you've been feeling lately…"

    def _build_right(self, parent):
        section_header(parent, "😴  Sleep & Health")
        card = tk.Frame(parent, bg=C["surface"],
                        highlightbackground=C["border"],
                        highlightthickness=1)
        card.pack(fill="x", padx=24, pady=(0, 8))

        self._sleep     = ModernSlider(card, "Sleep Hours / Day", 0, 12, 6, unit="h")
        self._sleep.pack(fill="x")

        self._stress    = ModernSlider(card, "Stress Level",     1, 10, 5)
        self._stress.pack(fill="x")

        self._anxiety   = ModernSlider(card, "Anxiety Level",    1, 10, 5)
        self._anxiety.pack(fill="x")

        tk.Frame(card, height=8, bg=C["surface"]).pack()

        section_header(parent, "🏃  Lifestyle")
        card2 = tk.Frame(parent, bg=C["surface"],
                         highlightbackground=C["border"],
                         highlightthickness=1)
        card2.pack(fill="x", padx=24, pady=(0, 8))

        self._screen    = ModernSlider(card2, "Screen Time / Day", 0, 12, 5, unit="h")
        self._screen.pack(fill="x")

        self._exercise  = ModernDropdown(card2, "Exercise Frequency",
                                          ["Never", "1–2 times/week",
                                           "3–4 times/week", "Daily"])
        self._exercise.pack(fill="x")

        self._social    = ModernDropdown(card2, "Socializing Frequency",
                                          ["Rarely", "Sometimes",
                                           "Often", "Very Often"])
        self._social.pack(fill="x")

        self._diet      = ModernDropdown(card2, "Diet Quality",
                                          ["Poor", "Average", "Good", "Excellent"])
        self._diet.pack(fill="x")

        tk.Frame(card2, height=8, bg=C["surface"]).pack()

        section_header(parent, "📊  Quick Risk Indicators")
        self._risk_card = tk.Frame(parent, bg=C["surface"],
                                   highlightbackground=C["border"],
                                   highlightthickness=1)
        self._risk_card.pack(fill="x", padx=24, pady=(0, 8))
        self._build_risk_preview()

        for w in (self._stress, self._anxiety,
                  self._sleep, self._study,
                  self._assign_p, self._exam_p):
            w._var.trace_add("write", lambda *_: self._refresh_preview())

    def _build_risk_preview(self):
        self._risk_bars = {}
        metrics = [
            ("Stress",     self._get_stress_preview),
            ("Sleep Deficit", self._get_sleep_preview),
            ("Workload",   self._get_workload_preview),
        ]
        for name, _ in metrics:
            row = tk.Frame(self._risk_card, bg=C["surface"])
            row.pack(fill="x", padx=16, pady=6)

            tk.Label(row, text=name, width=14, anchor="w",
                     font=(FONT_FAMILY, 9),
                     bg=C["surface"], fg=C["text_dim"]).pack(side="left")

            bar_bg = tk.Frame(row, bg=C["slider_bg"], height=8, width=200)
            bar_bg.pack(side="left", padx=(4, 8))
            bar_bg.pack_propagate(False)

            bar_fill = tk.Frame(bar_bg, bg=C["ok"], height=8, width=40)
            bar_fill.place(x=0, y=0, relheight=1)

            pct_lbl = tk.Label(row, text="—",
                               font=(FONT_FAMILY, 9, "bold"),
                               bg=C["surface"], fg=C["text"])
            pct_lbl.pack(side="left")

            self._risk_bars[name] = (bar_bg, bar_fill, pct_lbl)

        tk.Frame(self._risk_card, height=8, bg=C["surface"]).pack()
        self._refresh_preview()

    def _get_stress_preview(self):
        return (self._stress.get() + self._anxiety.get()) / 20.0

    def _get_sleep_preview(self):
        s = self._sleep.get()
        deficit = max(0, 8 - s) / 8.0
        return min(deficit, 1.0)

    def _get_workload_preview(self):
        return (self._study.get() / 14.0 * 0.4
                + self._assign_p.get() / 10.0 * 0.3
                + self._exam_p.get() / 10.0 * 0.3)

    def _refresh_preview(self):
        fns = {
            "Stress":       self._get_stress_preview,
            "Sleep Deficit":self._get_sleep_preview,
            "Workload":     self._get_workload_preview,
        }
        for name, fn in fns.items():
            pct = fn()
            bg, fill, lbl = self._risk_bars[name]
            w = int(pct * 200)
            fill.place(x=0, y=0, relheight=1, width=max(4, w))
            if pct < 0.4:
                col = C["ok"]
            elif pct < 0.7:
                col = C["mid"]
            else:
                col = C["warn"]
            fill.configure(bg=col)
            lbl.configure(text=f"{int(pct*100)}%", fg=col)

    def _clear_placeholder(self, _):
        if self._mood.get("1.0", "end-1c") == self._PLACEHOLDER:
            self._mood.delete("1.0", "end")
            self._mood.configure(fg="#FFFFFF")

    def _restore_placeholder(self, _):
        if not self._mood.get("1.0", "end-1c").strip():
            self._mood.insert("1.0", self._PLACEHOLDER)
            self._mood.configure(fg=C["text_dim"])

    def _submit(self):
        mood_text = self._mood.get("1.0", "end-1c").strip()
        if mood_text == self._PLACEHOLDER:
            mood_text = ""

        form_data = {
            "student_id":          self._id_var.get().strip() or "STU001",
            "age":                 self._age.get(),
            "gender":              self._gender.get(),
            "course":              self._course.get(),
            "semester":            self._semester.get(),
            "study_hours_per_day": self._study.get(),
            "sleep_hours_per_day": self._sleep.get(),
            "assignment_pressure": self._assign_p.get(),
            "exam_pressure":       self._exam_p.get(),
            "attendance_stress":   self._attend_s.get(),
            "screen_time_hours":   self._screen.get(),
            "stress_level":        self._stress.get(),
            "anxiety_level":       self._anxiety.get(),
            "exercise_frequency":  self._exercise.get(),
            "socializing_frequency": self._social.get(),
            "diet_quality":        self._diet.get(),
            "mood_text":           mood_text,
        }

        self._status.configure(text="⏳  Running prediction…", fg=C["mid"])
        self.frame.update()

        # ── Call predictor ────────────────────────────────
        try:
            from models.predictor import predict
            result = predict(form_data)
        except Exception as e:
            result = {"error": str(e)}

        mood_result = None
        if mood_text:
            try:
                from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
                sia = SentimentIntensityAnalyzer()
                mood_result = sia.polarity_scores(mood_text)
            except Exception:
                pass

        self._status.configure(text="✅  Prediction complete", fg=C["ok"])

        if self.on_result:
            self.on_result(result, form_data, mood_result)