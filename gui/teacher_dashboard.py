import tkinter as tk
from tkinter import ttk, messagebox
from db import mongo_handler
from datetime import datetime

class TeacherDashboard:
    def __init__(self, notebook):
        self.notebook = notebook
        self.frame = ttk.Frame(notebook)
        notebook.add(self.frame, text='Teacher Dashboard')

        # Create a sub-notebook for Results, Tracker, Analytics
        self.sub_notebook = ttk.Notebook(self.frame)
        self.sub_notebook.pack(fill='both', expand=True, padx=0, pady=0)

        self._create_results_tab()
        self._create_tracker_tab()
        self._create_analytics_tab()

    def _create_results_tab(self):
        """Display all students' latest burnout results."""
        tab = ttk.Frame(self.sub_notebook)
        self.sub_notebook.add(tab, text='Results')

        # Title
        title_frame = tk.Frame(tab, bg='#3a3a3a')
        title_frame.pack(fill='x', padx=0, pady=0)
        ttk.Label(title_frame, text="All Students Burnout Overview",
            style='Heading.TLabel').pack(pady=10)

        # Scrollable content
        canvas = tk.Canvas(tab, bg='#2c2c2c', highlightthickness=0)
        scrollbar = ttk.Scrollbar(tab, orient='vertical', command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#2c2c2c')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Content area for results
        content_frame = tk.Frame(scrollable_frame, bg='#2c2c2c')
        content_frame.pack(fill='both', expand=True, padx=20, pady=10)

        # Refresh button
        btn_frame = tk.Frame(content_frame, bg='#2c2c2c')
        btn_frame.pack(fill='x', pady=(0, 10))
        ttk.Button(btn_frame, text="Refresh Results",
            command=lambda: self._refresh_results(content_frame)).pack(side='left')

        # Results display area
        self.results_display = tk.Frame(content_frame, bg='#2c2c2c')
        self.results_display.pack(fill='both', expand=True)

        # Note: Loading is deferred to avoid MongoDB connection at startup
        ttk.Label(self.results_display, text="Click 'Refresh Results' to load student data",
            foreground='#b0b0b0').pack(pady=20)

    def _refresh_results(self, parent):
        """Fetch and display all students' latest results."""
        # Clear previous results
        for widget in self.results_display.winfo_children():
            widget.destroy()

        try:
            df = mongo_handler.get_all_latest()

            if df.empty:
                ttk.Label(self.results_display,
                    text="No student data available",
                    foreground='#b0b0b0').pack(pady=20)
                return

            # Column headers
            header_frame = tk.Frame(self.results_display, bg='#3a3a3a')
            header_frame.pack(fill='x', padx=10, pady=(0, 5))

            headers = ['Student ID', 'Burnout Score', 'Risk Level', 'Confidence', 'Last Updated']
            for i, header in enumerate(headers):
                ttk.Label(header_frame, text=header,
                    font=('Arial', 9, 'bold'),
                    width=18).grid(row=0, column=i, padx=5, pady=5)

            # Rows for each student
            for idx, row in df.iterrows():
                row_frame = tk.Frame(self.results_display, bg='#3a3a3a')
                row_frame.pack(fill='x', padx=10, pady=2)

                student_id = str(row.get('student_id', 'N/A'))
                score = row.get('burnout_score', 0)
                risk = str(row.get('risk_label', 'N/A'))
                confidence = row.get('confidence', 0)
                timestamp = row.get('timestamp', datetime.now())

                # Color based on risk level
                risk_colors = {
                    'High': '#E74C3C',
                    'Medium': '#F39C12',
                    'Low': '#27AE60'
                }
                risk_color = risk_colors.get(risk, '#b0b0b0')

                ttk.Label(row_frame, text=student_id, width=18).grid(
                    row=0, column=0, padx=5, pady=5)
                ttk.Label(row_frame, text=f"{score:.3f}", width=18).grid(
                    row=0, column=1, padx=5, pady=5)

                risk_label = tk.Label(row_frame, text=risk,
                    bg='#3a3a3a', fg=risk_color, font=('Arial', 10, 'bold'),
                    width=16, anchor='center')
                risk_label.grid(row=0, column=2, padx=5, pady=5)

                ttk.Label(row_frame, text=f"{confidence:.1f}%", width=18).grid(
                    row=0, column=3, padx=5, pady=5)

                # Format timestamp
                if isinstance(timestamp, datetime):
                    time_str = timestamp.strftime('%Y-%m-%d %H:%M')
                else:
                    time_str = str(timestamp)
                ttk.Label(row_frame, text=time_str, width=18).grid(
                    row=0, column=4, padx=5, pady=5)

        except (ConnectionError, Exception) as e:
            ttk.Label(self.results_display,
                text=f"MongoDB Error: {str(e)}\n\nPlease ensure MongoDB is running locally at localhost:27017",
                foreground='#ff6b6b', wraplength=300, justify='left').pack(pady=20)

    def _create_tracker_tab(self):
        """Track trends for a selected student."""
        tab = ttk.Frame(self.sub_notebook)
        self.sub_notebook.add(tab, text='Tracker')

        # Title
        title_frame = tk.Frame(tab, bg='#3a3a3a')
        title_frame.pack(fill='x', padx=0, pady=0)
        ttk.Label(title_frame, text="Student Burnout Trends",
            style='Heading.TLabel').pack(pady=10)

        # Scrollable content
        canvas = tk.Canvas(tab, bg='#2c2c2c', highlightthickness=0)
        scrollbar = ttk.Scrollbar(tab, orient='vertical', command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#2c2c2c')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Content area
        content_frame = tk.Frame(scrollable_frame, bg='#2c2c2c')
        content_frame.pack(fill='both', expand=True, padx=20, pady=10)

        # Student selector
        selector_frame = tk.Frame(content_frame, bg='#2c2c2c')
        selector_frame.pack(fill='x', pady=(0, 10))

        ttk.Label(selector_frame, text="Select Student:").pack(side='left', padx=5)

        self.student_var = tk.StringVar()
        self.student_combo = ttk.Combobox(selector_frame, textvariable=self.student_var,
            state='readonly', width=20)
        self.student_combo.pack(side='left', padx=5)

        ttk.Button(selector_frame, text="Load Trends",
            command=lambda: self._refresh_tracker()).pack(side='left', padx=5)
        
        ttk.Button(selector_frame, text="Refresh Students",
            command=lambda: self._load_student_list()).pack(side='left', padx=5)

        # Tracker display area
        self.tracker_display = tk.Frame(content_frame, bg='#2c2c2c')
        self.tracker_display.pack(fill='both', expand=True)

        # Note: Student list loading is deferred to avoid MongoDB connection at startup
        ttk.Label(self.tracker_display, text="Click 'Refresh Students' to load student list",
            foreground='#b0b0b0').pack(pady=20)

    def _load_student_list(self):
        """Load list of students from MongoDB."""
        try:
            students = mongo_handler.get_all_students()
            self.student_combo['values'] = students
            if students:
                self.student_combo.set(students[0])
        except ConnectionError:
            self.student_combo['values'] = []

    def _refresh_tracker(self):
        """Display trends for selected student."""
        # Clear previous data
        for widget in self.tracker_display.winfo_children():
            widget.destroy()

        student_id = self.student_var.get()
        if not student_id:
            ttk.Label(self.tracker_display,
                text="Please select a student",
                foreground='#b0b0b0').pack(pady=20)
            return

        try:
            df = mongo_handler.get_all_by_student(student_id)

            if df.empty:
                ttk.Label(self.tracker_display,
                    text=f"No data available for student {student_id}",
                    foreground='#b0b0b0').pack(pady=20)
                return

            # Display trend data
            info_text = f"Submissions for {student_id}:\n\n"

            for idx, row in df.iterrows():
                score = row.get('burnout_score', 'N/A')
                risk = row.get('risk_label', 'N/A')
                confidence = row.get('confidence', 'N/A')
                timestamp = row.get('timestamp', 'N/A')

                if isinstance(timestamp, datetime):
                    time_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    time_str = str(timestamp)

                info_text += f"• {time_str}\n"
                info_text += f"  Score: {score:.3f} | Risk: {risk} | Confidence: {confidence:.1f}%\n\n"

            display_label = tk.Text(self.tracker_display, height=15, width=50,
                font=('Arial', 10), bg='#3a3a3a', fg='#ffffff',
                insertbackground='white', wrap='word')
            display_label.pack(fill='both', expand=True, padx=10, pady=10)
            display_label.insert('1.0', info_text)
            display_label.config(state='disabled')

        except (ConnectionError, Exception) as e:
            ttk.Label(self.tracker_display,
                text=f"MongoDB Error: {str(e)}\n\nPlease ensure MongoDB is running at localhost:27017",
                foreground='#ff6b6b', wraplength=300, justify='left').pack(pady=20)

    def _create_analytics_tab(self):
        """Display analytics and summary statistics."""
        tab = ttk.Frame(self.sub_notebook)
        self.sub_notebook.add(tab, text='Analytics')

        # Title
        title_frame = tk.Frame(tab, bg='#3a3a3a')
        title_frame.pack(fill='x', padx=0, pady=0)
        ttk.Label(title_frame, text="Class Analytics & Summary",
            style='Heading.TLabel').pack(pady=10)

        # Scrollable content
        canvas = tk.Canvas(tab, bg='#2c2c2c', highlightthickness=0)
        scrollbar = ttk.Scrollbar(tab, orient='vertical', command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#2c2c2c')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Content area
        content_frame = tk.Frame(scrollable_frame, bg='#2c2c2c')
        content_frame.pack(fill='both', expand=True, padx=40, pady=20)

        # Refresh button
        btn_frame = tk.Frame(content_frame, bg='#2c2c2c')
        btn_frame.pack(fill='x', pady=(0, 20))
        ttk.Button(btn_frame, text="Refresh Analytics",
            command=lambda: self._refresh_analytics(content_frame)).pack(side='left')

        # Analytics display area
        self.analytics_display = tk.Frame(content_frame, bg='#2c2c2c')
        self.analytics_display.pack(fill='both', expand=True)

        # Note: Loading is deferred to avoid MongoDB connection at startup
        ttk.Label(self.analytics_display, text="Click 'Refresh Analytics' to load class statistics",
            foreground='#b0b0b0').pack(pady=20)

    def _refresh_analytics(self, parent):
        """Fetch and display class analytics."""
        # Clear previous analytics
        for widget in self.analytics_display.winfo_children():
            widget.destroy()

        try:
            df = mongo_handler.get_faculty_summary()

            if df.empty:
                ttk.Label(self.analytics_display,
                    text="No student data available",
                    foreground='#b0b0b0').pack(pady=20)
                return

            # Calculate statistics
            all_latest = mongo_handler.get_all_latest()

            if not all_latest.empty:
                avg_burnout = all_latest['burnout_score'].mean()
                high_risk = len(all_latest[all_latest['risk_label'] == 'High'])
                medium_risk = len(all_latest[all_latest['risk_label'] == 'Medium'])
                low_risk = len(all_latest[all_latest['risk_label'] == 'Low'])
                total_students = len(all_latest)

                # Display summary cards
                stat_frame = tk.Frame(self.analytics_display, bg='#2c2c2c')
                stat_frame.pack(fill='x', pady=10)

                # Card: Total Students
                card1 = tk.Frame(stat_frame, bg='#3a3a3a', relief='flat', bd=1)
                card1.pack(side='left', padx=10, pady=5, fill='both', expand=True)
                ttk.Label(card1, text="Total Students",
                    font=('Arial', 10, 'bold')).pack(pady=5)
                ttk.Label(card1, text=str(total_students),
                    font=('Arial', 16, 'bold'), foreground='#4CAF50').pack(pady=5)

                # Card: Average Burnout
                card2 = tk.Frame(stat_frame, bg='#3a3a3a', relief='flat', bd=1)
                card2.pack(side='left', padx=10, pady=5, fill='both', expand=True)
                ttk.Label(card2, text="Avg Burnout Score",
                    font=('Arial', 10, 'bold')).pack(pady=5)
                ttk.Label(card2, text=f"{avg_burnout:.3f}",
                    font=('Arial', 16, 'bold'), foreground='#F39C12').pack(pady=5)

                # Risk distribution
                dist_frame = tk.Frame(self.analytics_display, bg='#2c2c2c')
                dist_frame.pack(fill='x', pady=10)

                ttk.Label(dist_frame, text="Risk Distribution:",
                    font=('Arial', 11, 'bold')).pack(anchor='w', padx=10)

                risk_text = f"🔴 High Risk: {high_risk} students ({high_risk/total_students*100:.1f}%)\n"
                risk_text += f"🟡 Medium Risk: {medium_risk} students ({medium_risk/total_students*100:.1f}%)\n"
                risk_text += f"🟢 Low Risk: {low_risk} students ({low_risk/total_students*100:.1f}%)"

                risk_label = tk.Label(dist_frame, text=risk_text,
                    bg='#3a3a3a', fg='#ffffff', font=('Arial', 10),
                    justify='left', padx=20, pady=10)
                risk_label.pack(anchor='w', padx=10)

                # Top at-risk students
                top_frame = tk.Frame(self.analytics_display, bg='#2c2c2c')
                top_frame.pack(fill='both', expand=True, pady=10)

                ttk.Label(top_frame, text="Top At-Risk Students:",
                    font=('Arial', 11, 'bold')).pack(anchor='w', padx=10)

                top_students = all_latest.nlargest(5, 'burnout_score')
                if not top_students.empty:
                    for idx, row in top_students.iterrows():
                        student_id = row['student_id']
                        score = row['burnout_score']
                        risk = row['risk_label']

                        risk_color = {
                            'High': '#E74C3C',
                            'Medium': '#F39C12',
                            'Low': '#27AE60'
                        }.get(risk, '#b0b0b0')

                        info_text = f"{student_id}: {score:.3f} ({risk})"
                        lbl = tk.Label(top_frame, text=info_text,
                            bg='#3a3a3a', fg=risk_color, font=('Arial', 9),
                            padx=20, pady=5)
                        lbl.pack(anchor='w', padx=10, pady=2)

        except (ConnectionError, Exception) as e:
            ttk.Label(self.analytics_display,
                text=f"MongoDB Error: {str(e)}\n\nPlease ensure MongoDB is running at localhost:27017",
                foreground='#ff6b6b', wraplength=300, justify='left').pack(pady=20)
