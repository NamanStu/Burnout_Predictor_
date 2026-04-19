import tkinter as tk
from tkinter import ttk, messagebox
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

_sia = SentimentIntensityAnalyzer()   # create once, reuse

STRESS_WORDS = [
    'exam','deadline','tired','anxious','failed','pressure',
    'overwhelmed','panic','burnout','cry','depressed','stress',
    'exhausted','hopeless','lonely','worried','fear','stuck',
    'numb','helpless','worthless','hate','quit','give up',
    'struggle','hard','difficult','nervous','cannot','can not'
]

def analyze_mood(text: str) -> dict:
    scores   = _sia.polarity_scores(text)
    compound = scores['compound']               # -1 to +1
    # Invert: negative sentiment = high stress
    vader_stress = round((1 - compound) / 2 * 10, 1)

    lower  = text.lower()
    hits   = sum(1 for w in STRESS_WORDS if w in lower)
    kw_score = round(min(hits / len(STRESS_WORDS) * 30, 10), 1)

    label = ("High Stress" if vader_stress > 6.5 else
             "Moderate"   if vader_stress > 3.5 else
             "Low Stress")
    return {
        'vader_stress':   vader_stress,
        'keyword_score':  kw_score,
        'compound':       compound,
        'label':          label,
    }


class StudentFormTab:
    def __init__(self, notebook, on_result):
        """
        on_result: callback function that receives the
                   predict() result dict when form is submitted.
                   This is how the form talks to the Results tab.
        """
        self.on_result = on_result
        self.frame = tk.Frame(notebook, bg='white')
        notebook.add(self.frame, text='Student Form')
        self._build()

    def _build(self):
        # Create canvas and scrollbar for scrolling form
        canvas = tk.Canvas(self.frame, bg='#2c2c2c', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.frame, orient='vertical', command=canvas.yview)
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
        title_frame.grid(row=0, column=0, columnspan=3, pady=(20,20), sticky='ew')
        
        ttk.Label(title_frame, text="Student Burnout Assessment",
            style='Heading.TLabel').pack()

        # ── Center content in a sub-frame ────────────────
        content_frame = tk.Frame(f, bg='#2c2c2c')
        content_frame.grid(row=1, column=0, columnspan=3, padx=40, pady=10, sticky='ew')
        
        # Configure columns for center alignment
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=0)
        content_frame.columnconfigure(2, weight=1)
        
        # ── All variables ────────────────────────────────
        self.student_id      = tk.StringVar(value='STU001')
        self.age             = tk.IntVar(value=21)
        self.gender          = tk.StringVar(value='Male')
        self.course          = tk.StringVar(value='BTech')
        self.semester        = tk.IntVar(value=4)
        self.study_hours     = tk.IntVar(value=6)
        self.sleep_hours     = tk.IntVar(value=6)
        self.assign_pressure = tk.IntVar(value=5)
        self.exam_pressure   = tk.IntVar(value=5)
        self.attend_stress   = tk.IntVar(value=5)
        self.screen_time     = tk.IntVar(value=5)
        self.stress_level    = tk.IntVar(value=5)
        self.anxiety_level   = tk.IntVar(value=5)
        self.exercise_freq   = tk.StringVar(value='1-2 times/week')
        self.social_freq     = tk.StringVar(value='Sometimes')
        self.emotional_exh   = tk.StringVar(value='No')
        self.lost_motiv      = tk.StringVar(value='Sometimes')
        self.support_level   = tk.IntVar(value=5)
        self.mentally_drain  = tk.StringVar(value='Sometimes')
        self.difficulty_conc = tk.StringVar(value='Sometimes')

        # ── Helper to add a labelled row ─────────────────
        def add_entry(row, label, var, width=20):
            ttk.Label(content_frame, text=label).grid(
                row=row, column=0, padx=(20,5),
                pady=6, sticky='e')
            e = ttk.Entry(content_frame, textvariable=var, width=width)
            e.grid(row=row, column=1, padx=5, pady=6, sticky='w')

        def add_slider(row, label, var, lo, hi):
            ttk.Label(content_frame, text=label).grid(
                row=row, column=0, padx=(20,5),
                pady=6, sticky='e')
            slider = tk.Scale(content_frame, from_=lo, to=hi,
                variable=var, orient='horizontal',
                length=200, resolution=1, bg='#3a3a3a',
                fg='#ffffff', highlightthickness=0, troughcolor='#555555')
            slider.grid(row=row, column=1, padx=5, pady=6, sticky='ew')
            # Show current value next to slider (as integer only)
            val_lbl = ttk.Label(content_frame, text=f"{int(var.get())}", width=5)
            val_lbl.grid(row=row, column=2, padx=5, sticky='w')
            # Update label when slider changes
            def on_slider_change(*args):
                val_lbl.config(text=f"{int(var.get())}")
            var.trace_add("write", on_slider_change)

        def add_dropdown(row, label, var, options):
            ttk.Label(content_frame, text=label).grid(
                row=row, column=0, padx=(20,5),
                pady=6, sticky='e')
            ttk.Combobox(content_frame, textvariable=var,
                values=options, width=18,
                state='readonly').grid(
                row=row, column=1, padx=5, pady=6, sticky='w')

        # ── Widgets ──────────────────────────────────────
        add_entry(1,   "Student ID",                    self.student_id,      width=15)
        add_slider(2,   "Age (18-30)",                  self.age,             18, 30)
        add_dropdown(3, "Gender",                       self.gender,
            ['Male', 'Female', 'Prefer not to say'])
        add_dropdown(4, "Course",                       self.course,
            ['BTech', 'BCA', 'BCom', 'BSc'])
        add_slider(5,   "Semester (1-8)",              self.semester,        1, 8)
        add_slider(6,   "Study Hours/Day (0-14)",      self.study_hours,     0, 14)
        add_slider(7,   "Sleep Hours/Day (0-12)",      self.sleep_hours,     0, 12)
        add_slider(8,   "Assignment Pressure (1-10)",  self.assign_pressure, 1, 10)
        add_slider(9,   "Exam Pressure (1-10)",        self.exam_pressure,   1, 10)
        add_slider(10,  "Attendance Stress (1-10)",    self.attend_stress,   1, 10)
        add_slider(11,  "Screen Time Hours (0-12)",    self.screen_time,     0, 12)
        add_slider(12,  "Stress Level (1-10)",         self.stress_level,    1, 10)
        add_slider(13,  "Anxiety Level (1-10)",        self.anxiety_level,   1, 10)
        add_dropdown(14,"Exercise Frequency",           self.exercise_freq,
            ['Never', '1-2 times/week', '3-5 times/week', 'Daily'])
        add_dropdown(15,"Socializing Frequency",        self.social_freq,
            ['Rarely', 'Sometimes', 'Often'])
        add_dropdown(16,"Emotionally Exhausted",        self.emotional_exh,
            ['No', 'Sometimes', 'Yes'])
        add_dropdown(17,"Lost Motivation",              self.lost_motiv,
            ['No', 'Sometimes', 'Yes'])
        add_slider(18,  "Support Level (1-10)",        self.support_level,   1, 10)
        add_dropdown(19,"Mentally Drained Frequency",   self.mentally_drain,
            ['Never', 'Sometimes', 'Often'])
        add_dropdown(20,"Difficulty Concentrating",     self.difficulty_conc,
            ['No', 'Sometimes', 'Yes'])

        # ── Mood journal ─────────────────────────────────
        ttk.Label(content_frame, text="Any Additional Notes").grid(
            row=21, column=0, padx=(20,5),
            pady=6, sticky='ne')
        self.notes_text = tk.Text(content_frame, height=3, width=40,
            font=('Arial', 10), bg='#3a3a3a', fg='#ffffff', insertbackground='white')
        self.notes_text.grid(row=21, column=1, columnspan=2,
            padx=5, pady=6, sticky='ew')

        # ── Submit button ─────────────────────────────────
        button_frame = tk.Frame(content_frame, bg='#2c2c2c')
        button_frame.grid(row=22, column=0, columnspan=3, pady=20)
        
        self.submit_btn = ttk.Button(button_frame, text="Submit →",
            command=self._on_submit)
        self.submit_btn.pack()

    def _on_submit(self):
        # ── Validation ────────────────────────────────────
        # Read notes (Text widget reads differently)
        notes = self.notes_text.get("1.0", "end").strip()
        
        # Validate student ID
        student_id = self.student_id.get().strip()
        if not student_id:
            try:
                messagebox.showerror("Validation Error", "Please enter a Student ID")
            except Exception as msg_err:
                print(f"Messagebox error: {msg_err}")
            return

        # ── Collect form data from all fields ──────────────
        form_data = {
            'student_id':             student_id,
            'age':                    self.age.get(),
            'gender':                 self.gender.get(),
            'course':                 self.course.get(),
            'semester':               self.semester.get(),
            'study_hours':            self.study_hours.get(),
            'sleep_hours':            self.sleep_hours.get(),
            'assign_pressure':        self.assign_pressure.get(),
            'exam_pressure':          self.exam_pressure.get(),
            'attend_stress':          self.attend_stress.get(),
            'screen_time':            self.screen_time.get(),
            'stress_level':           self.stress_level.get(),
            'anxiety_level':          self.anxiety_level.get(),
            'exercise_freq':          self.exercise_freq.get(),
            'social_freq':            self.social_freq.get(),
            'emotional_exh':          self.emotional_exh.get(),
            'lost_motiv':             self.lost_motiv.get(),
            'support_level':          self.support_level.get(),
            'mentally_drain':         self.mentally_drain.get(),
            'difficulty_conc':        self.difficulty_conc.get(),
            'notes': notes,
        }

        # ── Disable button while processing ───────────────
        self.submit_btn.config(state='disabled',
                               text='Processing...')
        self.frame.update()   # force GUI refresh

        try:
            from models.predictor import predict
            result = predict(form_data)
            mood_result = analyze_mood(notes) if notes else {'label': 'Neutral', 'vader_stress': 5.0, 'keyword_score': 0}
            
            # Save submission to MongoDB
            try:
                from db import mongo_handler
                submission_data = form_data.copy()
                submission_data.update({
                    'burnout_score': result['score'],
                    'risk_label': result['risk_label'],
                    'confidence': result['confidence']
                })
                submission_id = mongo_handler.insert_submission(submission_data)
                print(f"✓ Submission saved to MongoDB: {submission_id}")
            except Exception as db_err:
                print(f"⚠ Warning: Could not save to MongoDB: {db_err}")
            
            # Pass result + original form data to Results tab
            try:
                self.on_result(result, form_data, mood_result)
            except Exception as callback_err:
                print(f"Callback error: {callback_err}")
            
            # Show result message
            try:
                messagebox.showinfo("Done",
                    f"Risk Level: {result['risk_label']}\n"
                    f"Score: {result['score']}\n"
                    f"Confidence: {result['confidence']}%")
            except Exception as msg_err:
                print(f"Messagebox error: {msg_err}")
                
        except Exception as e:
            try:
                messagebox.showerror("Prediction Error", str(e))
            except:
                print(f"Error: {e}")
        finally:
            self.submit_btn.config(state='normal',
                                   text='Submit →')
