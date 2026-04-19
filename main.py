import tkinter as tk
from tkinter import ttk
from gui.student_form import StudentFormTab
from gui.results_tab  import ResultsTab
from gui.trend_tab import TrendTab
from gui.teacher_dashboard import TeacherDashboard

root = tk.Tk()
root.title("Student Burnout Early Warning System")
root.geometry("1200x800")
root.configure(bg='#2c2c2c')

# Configure ttk.Style for grey and white theme
style = ttk.Style()
style.theme_use('clam')

# Define color scheme
BG_DARK = '#2c2c2c'
BG_LIGHT = '#3a3a3a'
FG_WHITE = '#ffffff'
ACCENT = '#4CAF50'

# Configure styles
style.configure('TNotebook', background=BG_DARK, borderwidth=0)
style.configure('TNotebook.Tab', padding=[20, 10], font=('Arial', 11, 'bold'))
style.map('TNotebook.Tab', 
    background=[('selected', BG_LIGHT)],
    foreground=[('selected', FG_WHITE)])

style.configure('TButton', 
    font=('Arial', 10, 'bold'), 
    padding=8,
    background=ACCENT,
    foreground=FG_WHITE)
style.map('TButton',
    background=[('active', '#45a049')])

style.configure('TLabel', 
    font=('Arial', 10),
    background=BG_LIGHT,
    foreground=FG_WHITE)

style.configure('TEntry', 
    font=('Arial', 10),
    fieldbackground=BG_LIGHT,
    background=BG_LIGHT,
    foreground=FG_WHITE)

style.configure('Heading.TLabel', 
    font=('Arial', 16, 'bold'),
    background=BG_LIGHT,
    foreground=FG_WHITE)

style.configure('TCombobox',
    fieldbackground=BG_LIGHT,
    background=BG_LIGHT,
    foreground='#000000')
style.map('TCombobox',
    fieldbackground=[('readonly', '#ffffff')],
    background=[('readonly', '#ffffff')],
    foreground=[('readonly', '#000000')])

style.configure('TFrame', background=BG_LIGHT)
style.configure('TScrollbar', background=BG_LIGHT, troughcolor=BG_DARK)

nb = ttk.Notebook(root)
nb.pack(fill='both', expand=True, padx=0, pady=0)

# Create Results tab first (form needs a reference to it)
results_tab = ResultsTab(nb)
trend_tab = TrendTab(nb)
teacher_dashboard = TeacherDashboard(nb)

# Create Form tab — pass results_tab.update as the callback
def on_result(result, form_data, mood_result=None):
    results_tab.update(result, form_data, mood_result)
    nb.select(1)   # auto-switch to Results tab after submit

form_tab = StudentFormTab(nb, on_result=on_result)

# Re-order tabs: Form first, Results second, Trend third, Teacher Dashboard fourth
nb.forget(0); nb.forget(0); nb.forget(0); nb.forget(0)
nb.add(form_tab.frame,           text='Student Form')
nb.add(results_tab.frame,        text='Results')
nb.add(trend_tab.frame,          text='Trend Tracker')
nb.add(teacher_dashboard.frame,  text='Teacher Dashboard')

root.mainloop()
