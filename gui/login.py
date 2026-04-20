
import tkinter as tk
from tkinter import ttk
import hashlib

C = {
    "bg":          "#0D0A0A",
    "surface":     "#1A1010",
    "surface2":    "#241515",
    "border":      "#3D2020",
    "accent":      "#C0392B",
    "accent_glow": "#8B1A1A",
    "text":        "#F0E6E6",
    "text_dim":    "#8A7070",
    "gold":        "#D4A017",
    "ok":          "#2ECC71",
    "warn":        "#E74C3C",
}
FONT = "Segoe UI"



def _hash(s):
    return hashlib.sha256(s.encode()).hexdigest()

FACULTY_CREDENTIALS = {
    "faculty":  _hash("faculty123"),
    "teacher":  _hash("teacher123"),
    "admin":    _hash("admin123"),
}


DEFAULT_STUDENT_PASSWORD = _hash("student123")


def _verify_student(student_id: str, password: str) -> bool:
    try:
        from db.mongo_handler import get_latest_by_student
        record = get_latest_by_student(student_id)
        if record is None:
            return _hash(password) == DEFAULT_STUDENT_PASSWORD
        return _hash(password) == DEFAULT_STUDENT_PASSWORD
    except Exception:
        return _hash(password) == DEFAULT_STUDENT_PASSWORD


def _verify_faculty(username: str, password: str) -> bool:
    return FACULTY_CREDENTIALS.get(username.lower()) == _hash(password)




def _entry_field(parent, label, show=None):
    frame = tk.Frame(parent, bg=C["surface"])
    frame.pack(fill="x", pady=(0, 16))

    tk.Label(frame, text=label,
             font=(FONT, 9),
             bg=C["surface"], fg=C["text_dim"],
             anchor="w").pack(fill="x", padx=2, pady=(0, 4))

    border = tk.Frame(frame, bg=C["border"], pady=1, padx=1)
    border.pack(fill="x")

    entry = tk.Entry(border,
                     font=(FONT, 12),
                     bg=C["surface2"], fg=C["text"],
                     insertbackground=C["gold"],
                     relief="flat", bd=0,
                     show=show)
    entry.pack(fill="x", ipady=10, padx=10)

    def on_focus_in(_):
        border.configure(bg=C["gold"])
    def on_focus_out(_):
        border.configure(bg=C["border"])

    entry.bind("<FocusIn>",  on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)
    return frame, entry




class LoginWindow:

    def __init__(self, root, on_student_login, on_faculty_login):
        self.root = root
        self.on_student_login = on_student_login
        self.on_faculty_login = on_faculty_login
        self._mode = "student"

        self.win = tk.Toplevel(root)
        self.win.title("Login — Student Burnout Early Warning System")
        self.win.geometry("480x580")
        self.win.resizable(False, False)
        self.win.configure(bg=C["bg"])
        self.win.grab_set()

        self.win.update_idletasks()
        x = (self.win.winfo_screenwidth()  - 480) // 2
        y = (self.win.winfo_screenheight() - 580) // 2
        self.win.geometry(f"480x580+{x}+{y}")

        self.root.withdraw()
        self.win.protocol("WM_DELETE_WINDOW", self._on_close)

        self._build()

    def _on_close(self):
        self.root.destroy()

    def _build(self):
        hdr = tk.Frame(self.win, bg=C["surface"], height=80)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        tk.Label(hdr, text="🔥  BURNOUT PREDICTOR",
                 font=(FONT, 14, "bold"),
                 bg=C["surface"], fg=C["text"]).pack(side="left", padx=28, pady=0)

        gold_bar = tk.Frame(self.win, bg=C["gold"], height=2)
        gold_bar.pack(fill="x")

        tab_frame = tk.Frame(self.win, bg=C["bg"])
        tab_frame.pack(fill="x", pady=(24, 0))

        self._student_tab = tk.Label(tab_frame, text="Student Login",
                                     font=(FONT, 10, "bold"),
                                     bg=C["bg"], fg=C["gold"],
                                     padx=20, pady=10, cursor="hand2")
        self._student_tab.pack(side="left", padx=(40, 0))

        sep = tk.Label(tab_frame, text="|",
                       font=(FONT, 10),
                       bg=C["bg"], fg=C["border"])
        sep.pack(side="left", padx=8)

        self._faculty_tab = tk.Label(tab_frame, text="Faculty Login",
                                     font=(FONT, 10),
                                     bg=C["bg"], fg=C["text_dim"],
                                     padx=20, pady=10, cursor="hand2")
        self._faculty_tab.pack(side="left")

        self._student_tab.bind("<Button-1>", lambda _: self._switch("student"))
        self._faculty_tab.bind("<Button-1>", lambda _: self._switch("faculty"))

        self._underline = tk.Frame(self.win, bg=C["gold"], height=2)
        self._underline.place(x=40, y=148, width=110)

        self._card = tk.Frame(self.win, bg=C["surface"],
                              highlightbackground=C["border"],
                              highlightthickness=1)
        self._card.place(x=40, y=170, width=400, height=340)

        self._build_student_form()

    def _clear_card(self):
        for w in self._card.winfo_children():
            w.destroy()

    def _switch(self, mode):
        self._mode = mode
        if mode == "student":
            self._student_tab.configure(fg=C["gold"], font=(FONT, 10, "bold"))
            self._faculty_tab.configure(fg=C["text_dim"], font=(FONT, 10))
            self._underline.place(x=40, y=148, width=110)
            self._build_student_form()
        else:
            self._faculty_tab.configure(fg=C["gold"], font=(FONT, 10, "bold"))
            self._student_tab.configure(fg=C["text_dim"], font=(FONT, 10))
            self._underline.place(x=178, y=148, width=105)
            self._build_faculty_form()

    def _build_student_form(self):
        self._clear_card()
        pad = tk.Frame(self._card, bg=C["surface"])
        pad.pack(fill="both", expand=True, padx=28, pady=24)

        tk.Label(pad, text="Student Sign In",
                 font=(FONT, 13, "bold"),
                 bg=C["surface"], fg=C["text"]).pack(anchor="w", pady=(0, 20))

        _, self._sid_entry = _entry_field(pad, "STUDENT ID")
        _, self._spw_entry = _entry_field(pad, "PASSWORD", show="•")

        self._spw_entry.bind("<Return>", lambda _: self._do_student_login())

        self._s_err = tk.Label(pad, text="",
                               font=(FONT, 9),
                               bg=C["surface"], fg=C["warn"])
        self._s_err.pack(anchor="w", pady=(0, 8))

        btn = tk.Frame(pad, bg=C["accent"], cursor="hand2")
        btn.pack(fill="x", pady=(4, 0))
        lbl = tk.Label(btn, text="Sign In  →",
                       font=(FONT, 11, "bold"),
                       bg=C["accent"], fg=C["text"],
                       pady=12)
        lbl.pack()

        btn.bind("<Button-1>", lambda _: self._do_student_login())
        lbl.bind("<Button-1>", lambda _: self._do_student_login())
        btn.bind("<Enter>", lambda _: btn.configure(bg=C["accent_glow"]) or lbl.configure(bg=C["accent_glow"]))
        btn.bind("<Leave>", lambda _: btn.configure(bg=C["accent"]) or lbl.configure(bg=C["accent"]))

        tk.Label(pad, text="Default password: student123",
                 font=(FONT, 8),
                 bg=C["surface"], fg=C["text_dim"]).pack(pady=(12, 0))

    def _do_student_login(self):
        sid = self._sid_entry.get().strip()
        pw  = self._spw_entry.get().strip()

        if not sid:
            self._s_err.configure(text="⚠  Please enter your Student ID")
            return
        if not pw:
            self._s_err.configure(text="⚠  Please enter your password")
            return

        if _verify_student(sid, pw):
            self.win.destroy()
            self.root.deiconify()
            self.on_student_login(sid)
        else:
            self._s_err.configure(text="⚠  Incorrect password. Try 'student123'")

    def _build_faculty_form(self):
        self._clear_card()
        pad = tk.Frame(self._card, bg=C["surface"])
        pad.pack(fill="both", expand=True, padx=28, pady=24)

        tk.Label(pad, text="Faculty Sign In",
                 font=(FONT, 13, "bold"),
                 bg=C["surface"], fg=C["text"]).pack(anchor="w", pady=(0, 20))

        _, self._fid_entry = _entry_field(pad, "USERNAME")
        _, self._fpw_entry = _entry_field(pad, "PASSWORD", show="•")

        self._fpw_entry.bind("<Return>", lambda _: self._do_faculty_login())

        self._f_err = tk.Label(pad, text="",
                               font=(FONT, 9),
                               bg=C["surface"], fg=C["warn"])
        self._f_err.pack(anchor="w", pady=(0, 8))

        btn = tk.Frame(pad, bg=C["gold"], cursor="hand2")
        btn.pack(fill="x", pady=(4, 0))
        lbl = tk.Label(btn, text="Sign In  →",
                       font=(FONT, 11, "bold"),
                       bg=C["gold"], fg=C["bg"],
                       pady=12)
        lbl.pack()

        btn.bind("<Button-1>", lambda _: self._do_faculty_login())
        lbl.bind("<Button-1>", lambda _: self._do_faculty_login())
        btn.bind("<Enter>", lambda _: btn.configure(bg=C["accent"]) or lbl.configure(bg=C["accent"], fg=C["text"]))
        btn.bind("<Leave>", lambda _: btn.configure(bg=C["gold"]) or lbl.configure(bg=C["gold"], fg=C["bg"]))

        tk.Label(pad, text="Usernames: faculty / teacher / admin\nDefault password: faculty123 / teacher123 / admin123",
                 font=(FONT, 8),
                 bg=C["surface"], fg=C["text_dim"],
                 justify="left").pack(pady=(12, 0), anchor="w")

    def _do_faculty_login(self):
        username = self._fid_entry.get().strip()
        pw       = self._fpw_entry.get().strip()

        if not username:
            self._f_err.configure(text="⚠  Please enter your username")
            return
        if not pw:
            self._f_err.configure(text="⚠  Please enter your password")
            return

        if _verify_faculty(username, pw):
            self.win.destroy()
            self.root.deiconify()
            self.on_faculty_login(username)
        else:
            self._f_err.configure(text="⚠  Invalid username or password")
