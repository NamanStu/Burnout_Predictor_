import tkinter as tk
from tkinter import ttk
import numpy as np

class ResultsTab:
    def __init__(self, notebook):
        self.frame = tk.Frame(notebook, bg='white')
        notebook.add(self.frame, text='Results')
        self._build()

    def _build(self):
        # Create main frame and canvas for scrolling
        main_frame = tk.Frame(self.frame, bg='#2c2c2c')
        main_frame.pack(fill='both', expand=True)
        
        # Create canvas and scrollbar
        canvas = tk.Canvas(main_frame, bg='#2c2c2c', highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient='vertical', command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#2c2c2c')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        f = scrollable_frame

        # ── Title ───────────────────────────────────────
        title_frame = tk.Frame(f, bg='#2c2c2c')
        title_frame.pack(pady=(20,20), expand=True)
        
        ttk.Label(title_frame, text="Prediction Results",
            style='Heading.TLabel').pack()

        # ── Content frame for center alignment ───────────
        content_frame = tk.Frame(f, bg='#2c2c2c')
        content_frame.pack(padx=40, pady=10, fill='both', expand=True)

        # ── Score + risk label ────────────────────────────
        self.score_lbl = ttk.Label(content_frame,
            text="Burnout Score: —",
            font=('Arial', 16, 'bold'))
        self.score_lbl.pack(pady=10)

        self.risk_lbl = ttk.Label(content_frame,
            text="Risk Level: —",
            font=('Arial', 14))
        self.risk_lbl.pack(pady=8)

        self.conf_lbl = ttk.Label(content_frame,
            text="Confidence: —",
            font=('Arial', 11), foreground='#b0b0b0')
        self.conf_lbl.pack(pady=5)

        # ── Color-coded risk bar (Canvas + NumPy) ─────────
        ttk.Label(content_frame, text="Risk Meter:",
            font=('Arial', 11, 'bold')).pack(pady=(15,8))
        self.bar_canvas = tk.Canvas(content_frame, width=400,
            height=40, bg='#3a3a3a',
            highlightthickness=1, highlightbackground='#555555')
        self.bar_canvas.pack(pady=10)

        # ── VADER scores ──────────────────────────────────
        self.vader_lbl = ttk.Label(content_frame,
            text="Mood Analysis: —",
            font=('Arial', 10), foreground='#b0b0b0')
        self.vader_lbl.pack(pady=12)

        # ── SHAP explanation text ──────────────────────────
        ttk.Label(content_frame, text="Model Explanation",
            font=('Arial', 12, 'bold')).pack(pady=(15,8))
        self.shap_lbl = ttk.Label(content_frame, text="—", font=('Arial', 10), 
                                  wraplength=600, justify='left')
        self.shap_lbl.pack(pady=10, padx=20, fill='both', expand=True)

    def update(self, result: dict, form_data: dict = None, mood: dict = None):
        """Call this from student_form on_result callback."""
        score      = result['score']
        risk       = result['risk_label']
        confidence = result['confidence']

        # Update text labels
        self.score_lbl.config(
            text=f"Burnout Score: {score:.3f}")
        self.risk_lbl.config(
            text=f"Risk Level: {risk}",
            foreground={'High':'#E74C3C',
                        'Medium':'#F39C12',
                        'Low':'#27AE60'}.get(risk, 'black'))
        self.conf_lbl.config(
            text=f"Confidence: {confidence}%")

        # Color-coded risk bar — NumPy clips the width
        bar_w = int(np.clip(score * 400, 0, 400))
        color = ('#E74C3C' if score > 0.6 else
                 '#F39C12' if score > 0.3 else '#27AE60')
        self.bar_canvas.delete('all')
        self.bar_canvas.create_rectangle(
            0, 0, bar_w, 30, fill=color, outline='')
        self.bar_canvas.create_text(
            bar_w + 5, 15, text=f"{score:.0%}",
            anchor='w', font=('Arial', 9))

        # Mood analysis
        if mood:
            self.vader_lbl.config(
                text=(f"Mood: {mood['label']}  |  "
                      f"VADER stress: {mood['vader_stress']}/10  |  "
                      f"Keyword score: {mood['keyword_score']}/10"))

        # SHAP explanation as text
        explanation = "Model prediction based on student responses."
        if form_data:
            if form_data.get('stress_level', 5) > 7:
                explanation += "\n• High stress level detected."
            if form_data.get('anxiety_level', 5) > 7:
                explanation += "\n• High anxiety level detected."
            if form_data.get('sleep_hours', 6) < 5:
                explanation += "\n• Insufficient sleep identified."
            if form_data.get('study_hours', 6) > 10:
                explanation += "\n• Extended study hours noted."
        self.shap_lbl.config(text=explanation)
