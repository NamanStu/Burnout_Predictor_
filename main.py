import sys
import io

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding and sys.stderr.encoding.lower() != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import tkinter as tk
from tkinter import ttk

from gui.student_form import StudentFormTab
from gui.results_tab import ResultsTab
from gui.trend_tab import TrendTab
from gui.teacher_dashboard import TeacherDashboard
from gui.login import LoginWindow

C = {
    "bg":      "#0D0A0A",
    "surface": "#1A1010",
    "border":  "#3D2020",
    "accent":  "#C0392B",
    "text":    "#F0E6E6",
    "text_dim":"#8A7070",
}
FONT = "Segoe UI"
# ─────────────────────────────────────────────

root = tk.Tk()
root.title("Student Burnout Early Warning System")
root.geometry("1280x820")
root.minsize(960, 660)
root.configure(bg=C["bg"])

style = ttk.Style()
style.theme_use("clam")

style.configure("Burnout.TNotebook",
                background=C["surface"],
                tabmargins=[0, 0, 0, 0],
                borderwidth=0)

style.configure("Burnout.TNotebook.Tab",
                font=(FONT, 10, "bold"),
                padding=[20, 12],
                background=C["surface"],
                foreground=C["text_dim"],
                borderwidth=0,
                focuscolor=C["surface"])

style.map("Burnout.TNotebook.Tab",
          background=[("selected", C["bg"])],
          foreground=[("selected", C["accent"])],
          expand=[("selected", [0, 0, 0, 2])])

nb = ttk.Notebook(root, style="Burnout.TNotebook")
nb.pack(fill="both", expand=True)

results_tab       = ResultsTab(nb)
trend_tab         = TrendTab(nb)
teacher_dashboard = TeacherDashboard(nb)

def on_result(result, form_data, mood_result=None):
    results_tab.update(result, form_data, mood_result)
    nb.select(1)   # auto-switch to Results

form_tab = StudentFormTab(nb, on_result=on_result)

nb.add(form_tab.frame,          text="  Student Form  ")
nb.add(results_tab.frame,       text="  Results       ")
nb.add(trend_tab.frame,         text="  Trend Tracker ")
nb.add(teacher_dashboard.frame, text="  Teacher Dashboard  ")

def on_student_login(student_id: str):
    """Student sees Form, Results, Trend — not Teacher Dashboard."""
    form_tab._id_var.set(student_id)
    try:
        nb.hide(3)   # hide Teacher Dashboard
    except Exception:
        pass
    nb.select(0)
    root.title(f"Student Burnout — {student_id}")

def on_faculty_login(username: str):
    """Faculty sees only Teacher Dashboard."""
    try:
        nb.hide(0)   # hide Student Form
        nb.hide(1)   # hide Results
        nb.hide(2)   # hide Trend Tracker
    except Exception:
        pass
    nb.select(3)
    root.title(f"Teacher Dashboard — {username}")

LoginWindow(root, on_student_login, on_faculty_login)

root.mainloop()
