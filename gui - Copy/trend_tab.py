import tkinter as tk
from tkinter import ttk
import pandas as pd

class TrendTab:
    def __init__(self, notebook):
        self.frame = tk.Frame(notebook, bg='white')
        notebook.add(self.frame, text='Trend Tracker')
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
        title_frame.pack(pady=(20,15), expand=True)
        
        ttk.Label(title_frame, text="Trend Tracker",
            font=('Arial', 16, 'bold')).pack()

        # ── Content frame for center alignment ───────────
        content_frame = tk.Frame(f, bg='#2c2c2c')
        content_frame.pack(padx=40, pady=10, fill='both', expand=True)
        
        ctrl = tk.Frame(content_frame, bg='#2c2c2c')
        ctrl.pack(side='top', fill='x', padx=10, pady=12)

        ttk.Label(ctrl, text="Student ID:").pack(side='left')
        self.sid_var = tk.StringVar()
        ttk.Entry(ctrl, textvariable=self.sid_var,
            width=15).pack(side='left', padx=8)
        ttk.Button(ctrl, text="Refresh",
            command=self._refresh).pack(side='left', padx=5)

        # Text display for trend data
        self.info_lbl = ttk.Label(content_frame, 
            text="Enter a Student ID and click Refresh to view burnout trends.\n\n"
                 "Note: Requires MongoDB to be running on localhost:27017", 
            wraplength=600, justify='left', 
            font=('Arial', 10),
            foreground='#b0b0b0')
        self.info_lbl.pack(pady=15, padx=10, fill='both', expand=True)

    def _refresh(self):
        sid = self.sid_var.get().strip()
        if not sid:
            self.info_lbl.config(text="Please enter a Student ID", foreground='#ff6b6b')
            return

        self.info_lbl.config(text="Loading...", foreground='#b0b0b0')
        self.frame.update()

        try:
            from db.mongo_handler import get_all_by_student
            df = get_all_by_student(sid)
            
            if df.empty:
                self.info_lbl.config(
                    text=f'No data available for student {sid}',
                    foreground='#b0b0b0')
                return

            df['timestamp'] = pd.to_datetime(df['timestamp'])
            weekly = (df.set_index('timestamp')['burnout_score']
                        .resample('W').mean())

            info_text = f"Weekly Burnout Trend for {sid}:\n\n"
            for date, score in weekly.items():
                info_text += f"{date.strftime('%Y-%m-%d')}: {score:.2f}\n"
            
            self.info_lbl.config(text=info_text, foreground='#ffffff')
            
        except ConnectionError as e:
            self.info_lbl.config(
                text=f"⚠️  MongoDB Connection Error\n\n"
                     f"Could not connect to MongoDB.\n\n"
                     f"To enable trend tracking:\n"
                     f"1. Install MongoDB locally or use Atlas\n"
                     f"2. Ensure MongoDB is running on localhost:27017\n"
                     f"3. Try again\n\n"
                     f"For now, the Burnout Predictor works without MongoDB.",
                foreground='#ff6b6b')
        except Exception as e:
            self.info_lbl.config(
                text=f"❌  Error Loading Data\n\n{str(e)}",
                foreground='#ff6b6b')
