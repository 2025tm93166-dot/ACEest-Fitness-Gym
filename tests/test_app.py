import sqlite3

import app as app_module


class DummyVar:
    def __init__(self, value):
        self.value = value

    def get(self):
        return self.value


class FakeText:
    def __init__(self):
        self.value = ""

    def configure(self, *args, **kwargs):
        pass

    def title(self, *args, **kwargs):
        pass

    def geometry(self, *args, **kwargs):
        pass

    def delete(self, *args, **kwargs):
        self.value = ""

    def insert(self, *args, **kwargs):
        if len(args) >= 2:
            self.value += str(args[1])
        else:
            self.value += str(kwargs.get("text", ""))


class DummyRoot:
    def winfo_children(self):
        return []

    def title(self, *args, **kwargs):
        pass

    def geometry(self, *args, **kwargs):
        pass

    def configure(self, *args, **kwargs):
        pass


class FakeWidget:
    def __init__(self, *args, **kwargs):
        self.children = []
        self.values = []
        self.commands = {}
        self.value = kwargs.get("value", "")

    def pack(self, *args, **kwargs):
        pass

    def bind(self, *args, **kwargs):
        pass

    def configure(self, *args, **kwargs):
        pass

    def title(self, *args, **kwargs):
        pass

    def geometry(self, *args, **kwargs):
        pass

    def destroy(self):
        pass

    def winfo_children(self):
        return self.children

    def heading(self, *args, **kwargs):
        pass

    def column(self, *args, **kwargs):
        pass

    def insert(self, *args, **kwargs):
        self.values.append(kwargs.get("values"))

    def get_children(self):
        return list(range(len(self.values)))

    def delete(self, item):
        self.values.pop(item)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def get(self):
        return self.value


class FakeButton(FakeWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.command = kwargs.get("command")


class FakeNotebook(FakeWidget):
    def add(self, child, **kwargs):
        self.children.append(child)


class FakeText(FakeWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.value = ""

    def delete(self, *args, **kwargs):
        self.value = ""

    def insert(self, *args, **kwargs):
        self.value += str(args[1])


def _new_app(db_path, *, current_client=None):
    conn = sqlite3.connect(db_path)
    app = app_module.ACEestApp.__new__(app_module.ACEestApp)
    app.root = DummyRoot()
    app.conn = conn
    app.cur = conn.cursor()
    app.current_user = None
    app.current_client = current_client
    app.current_role = "Admin"
    app.program_templates = {
        "Fat Loss": ["Full Body HIIT", "Circuit Training", "Cardio + Weights"],
        "Muscle Gain": ["Push/Pull/Legs", "Upper/Lower Split", "Full Body Strength"],
        "Beginner": ["Full Body 3x/week", "Light Strength + Mobility"],
    }
    return app


def test_init_db_creates_schema_and_default_admin(monkeypatch, tmp_path):
    db_path = tmp_path / "aceest_test.db"
    monkeypatch.setattr(app_module, "DB_NAME", str(db_path))

    app_module.init_db()

    with sqlite3.connect(db_path) as conn:
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        ).fetchall()
        table_names = {row[0] for row in tables}
        assert {"users", "clients", "progress", "workouts", "exercises", "metrics"}.issubset(table_names)

        admin = conn.execute(
            "SELECT username, password, role FROM users WHERE username='admin'"
        ).fetchone()
        assert admin == ("admin", "admin", "Admin")


def test_login_success_sets_user_and_role(monkeypatch, tmp_path):
    db_path = tmp_path / "aceest_login.db"
    monkeypatch.setattr(app_module, "DB_NAME", str(db_path))
    app_module.init_db()

    app = _new_app(str(db_path), current_client=None)
    app.username_var = DummyVar("admin")
    app.password_var = DummyVar("admin")
    app.dashboard = lambda: None

    app.login()

    assert app.current_user == "admin"
    assert app.current_role == "Admin"


def test_login_failure_shows_error(monkeypatch, tmp_path):
    db_path = tmp_path / "aceest_login_fail.db"
    monkeypatch.setattr(app_module, "DB_NAME", str(db_path))
    app_module.init_db()

    app = _new_app(str(db_path))
    app.username_var = DummyVar("wrong-user")
    app.password_var = DummyVar("wrong-pass")
    app.dashboard = lambda: None

    called = {}

    def _show_error(title, message):
        called["title"] = title
        called["message"] = message

    monkeypatch.setattr(app_module.messagebox, "showerror", _show_error)

    app.login()

    assert called == {"title": "Login Failed", "message": "Invalid credentials"}


def test_generate_program_updates_selected_client(monkeypatch, tmp_path):
    db_path = tmp_path / "aceest_gen.db"
    monkeypatch.setattr(app_module, "DB_NAME", str(db_path))
    app_module.init_db()

    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO clients (name, membership_status) VALUES (?, ?)",
            ("Alice", "Active"),
        )
        conn.commit()

    app = _new_app(str(db_path), current_client="Alice")
    app.refresh_summary = lambda: None

    monkeypatch.setattr(app_module.random, "choice", lambda seq: seq[0])
    monkeypatch.setattr(app_module.messagebox, "showinfo", lambda *args, **kwargs: None)

    app.generate_program()

    with sqlite3.connect(db_path) as conn:
        program = conn.execute(
            "SELECT program FROM clients WHERE name=?",
            ("Alice",),
        ).fetchone()[0]

    assert program == "Full Body HIIT"


def test_refresh_summary_writes_expected_text(monkeypatch, tmp_path):
    db_path = tmp_path / "aceest_summary.db"
    monkeypatch.setattr(app_module, "DB_NAME", str(db_path))
    app_module.init_db()

    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO clients (name, program, calories, membership_status) VALUES (?, ?, ?, ?)",
            ("Alice", "Push/Pull/Legs", 2200, "Active"),
        )
        conn.commit()

    app = _new_app(str(db_path), current_client="Alice")
    app.summary_text = FakeText()

    app.refresh_summary()

    assert "Name: Alice" in app.summary_text.value
    assert "Program: Push/Pull/Legs" in app.summary_text.value
    assert "Calories: 2200" in app.summary_text.value
    assert "Membership: Active" in app.summary_text.value


def test_check_membership_sends_membership_message(monkeypatch, tmp_path):
    db_path = tmp_path / "aceest_membership.db"
    monkeypatch.setattr(app_module, "DB_NAME", str(db_path))
    app_module.init_db()

    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO clients (name, membership_status, membership_end) VALUES (?, ?, ?)",
            ("Alice", "Active", "2026-12-31"),
        )
        conn.commit()

    app = _new_app(str(db_path), current_client="Alice")
    called = {}

    def _show_info(title, message):
        called["title"] = title
        called["message"] = message

    monkeypatch.setattr(app_module.messagebox, "showinfo", _show_info)

    app.check_membership()

    assert called["title"] == "Membership"
    assert "Membership: Active" in called["message"]
    assert "Renewal Date: 2026-12-31" in called["message"]


def _patch_widgets(monkeypatch):
    for name in ("Frame", "Label", "Entry", "Text", "Toplevel"):
        monkeypatch.setattr(app_module.tk, name, FakeWidget)
    monkeypatch.setattr(app_module.tk, "StringVar", lambda **kwargs: DummyVar(kwargs.get("value", "")))
    monkeypatch.setattr(app_module.tk, "IntVar", lambda **kwargs: DummyVar(kwargs.get("value", 0)))
    monkeypatch.setattr(app_module.ttk, "Button", FakeButton)
    monkeypatch.setattr(app_module.ttk, "Combobox", FakeWidget)
    monkeypatch.setattr(app_module.ttk, "Notebook", FakeNotebook)
    monkeypatch.setattr(app_module.ttk, "Treeview", FakeWidget)


def test_app_initialization_sets_up_database_and_login(monkeypatch, tmp_path):
    db_path = tmp_path / "aceest_init.db"
    monkeypatch.setattr(app_module, "DB_NAME", str(db_path))
    app_module.init_db()
    _patch_widgets(monkeypatch)
    monkeypatch.setattr(app_module.ACEestApp, "login_screen", lambda self: None)

    app = app_module.ACEestApp(DummyRoot())

    assert app.conn.execute("SELECT username FROM users").fetchone() == ("admin",)
    assert app.current_user is None
    assert app.current_client is None
    assert app.program_templates["Beginner"]
    app.conn.close()


def test_login_screen_builds_login_form(monkeypatch, tmp_path):
    app = _new_app(str(tmp_path / "login_screen.db"))
    _patch_widgets(monkeypatch)

    app.login_screen()

    assert isinstance(app.username_var, DummyVar)
    assert isinstance(app.password_var, DummyVar)


def test_dashboard_builds_tabs_and_workout_table(monkeypatch, tmp_path):
    db_path = tmp_path / "dashboard.db"
    monkeypatch.setattr(app_module, "DB_NAME", str(db_path))
    app_module.init_db()
    app = _new_app(str(db_path))
    app.root = FakeWidget()
    _patch_widgets(monkeypatch)

    app.dashboard()

    assert isinstance(app.client_list, FakeWidget)
    assert isinstance(app.summary_text, FakeWidget)
    assert isinstance(app.tree_workouts, FakeWidget)
    assert app.client_list.values == []


def test_client_selection_and_add_save_paths(monkeypatch, tmp_path):
    db_path = tmp_path / "clients.db"
    monkeypatch.setattr(app_module, "DB_NAME", str(db_path))
    app_module.init_db()
    app = _new_app(str(db_path))
    app.client_list = FakeWidget()
    app.client_list.value = ""
    app.refresh_summary = lambda: None
    app.refresh_workouts = lambda: None
    app.plot_charts = lambda: None
    monkeypatch.setattr(app_module.tk.simpledialog, "askstring", lambda *args: None)
    app.add_save_client()

    monkeypatch.setattr(app_module.tk.simpledialog, "askstring", lambda *args: "Alice")
    monkeypatch.setattr(app_module.messagebox, "showinfo", lambda *args: None)
    app.refresh_client_list = lambda: setattr(app.client_list, "values", ["Alice"])
    app.add_save_client()
    assert app.cur.execute("SELECT name FROM clients").fetchone() == ("Alice",)

    app.load_client()
    assert app.current_client is None
    app.client_list.value = "Alice"
    app.load_client()
    assert app.current_client == "Alice"
    app.conn.close()


def test_pdf_generation_requires_client_and_writes_client_fields(monkeypatch, tmp_path):
    db_path = tmp_path / "pdf.db"
    monkeypatch.setattr(app_module, "DB_NAME", str(db_path))
    app_module.init_db()
    app = _new_app(str(db_path))
    app_module.init_db()
    app.cur.execute(
        "INSERT INTO clients (name, age, height, weight, program, calories, "
        "target_weight, target_adherence, membership_status, membership_end) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        ("Alice", 30, 165, 60, "Strength", 2000, 58, 90, "Active", "2027-01-01"),
    )
    app.conn.commit()
    warnings = []
    monkeypatch.setattr(app_module.messagebox, "showwarning", lambda *args: warnings.append(args))
    app.generate_pdf()
    assert warnings and warnings[0][0] == "No Client"

    output = {}

    class DummyPDF:
        def __init__(self):
            self.cells = []

        def add_page(self):
            pass

        def set_font(self, *args):
            pass

        def cell(self, *args, **kwargs):
            self.cells.append(args[2])

        def output(self, path):
            output["path"] = path
            output["cells"] = self.cells

    monkeypatch.setattr(app_module, "FPDF", DummyPDF)
    monkeypatch.setattr(app_module.messagebox, "showinfo", lambda *args: None)
    app.current_client = "Alice"
    app.generate_pdf()
    assert output["path"] == "Alice_report.pdf"
    assert "Age: 30" in output["cells"]
    assert "Membership: Active" in output["cells"]
    app.conn.close()


def test_summary_membership_and_program_without_client(monkeypatch, tmp_path):
    app = _new_app(str(tmp_path / "empty_client.db"))
    app.summary_text = FakeText()
    messages = []
    monkeypatch.setattr(app_module.messagebox, "showwarning", lambda *args: messages.append(args))
    app.refresh_summary()
    app.check_membership()
    app.generate_program()
    assert app.summary_text.value == ""
    assert messages == [("No Client", "Select a client first")]
    app.conn.close()


def test_plot_charts_handles_empty_and_populated_progress(monkeypatch, tmp_path):
    db_path = tmp_path / "charts.db"
    monkeypatch.setattr(app_module, "DB_NAME", str(db_path))
    app_module.init_db()
    app = _new_app(str(db_path), current_client="Alice")
    app.chart_frame = FakeWidget()
    app.plot_charts()
    assert app.chart_frame.children == []

    app.cur.executemany(
        "INSERT INTO progress VALUES (?, ?, ?, ?)",
        [(1, "Alice", "Week 1", 70), (2, "Alice", "Week 2", 85)],
    )
    app.conn.commit()
    calls = {}

    class DummyAxis:
        def plot(self, weeks, adherence, **kwargs):
            calls["data"] = (weeks, adherence, kwargs)

        def set_title(self, title):
            calls["title"] = title

        def set_ylabel(self, label):
            calls["ylabel"] = label

        def set_ylim(self, *limits):
            calls["limits"] = limits

        def grid(self, enabled):
            calls["grid"] = enabled

    class DummyCanvas:
        def __init__(self, figure, master):
            pass

        def draw(self):
            calls["drawn"] = True

        def get_tk_widget(self):
            return FakeWidget()

    monkeypatch.setattr(app_module.plt, "subplots", lambda **kwargs: (object(), DummyAxis()))
    monkeypatch.setattr(app_module, "FigureCanvasTkAgg", DummyCanvas)
    app.plot_charts()
    assert calls["data"] == (["Week 1", "Week 2"], [70, 85], {"marker": "o"})
    assert calls["title"] == "Weekly Adherence"
    assert calls["limits"] == (0, 100)
    assert calls["drawn"]
    app.conn.close()


def test_workout_refresh_and_add_save(monkeypatch, tmp_path):
    db_path = tmp_path / "workouts.db"
    app = _new_app(str(db_path))
    app.tree_workouts = FakeWidget()
    app.refresh_workouts()
    assert app.tree_workouts.values == []
    app.add_workout()
    assert app.tree_workouts.values == []

    app.current_client = "Alice"
    app.cur.execute(
        "CREATE TABLE workouts (client_name TEXT, date TEXT, workout_type TEXT, "
        "duration_min INTEGER, notes TEXT)"
    )
    app.cur.execute(
        "INSERT INTO workouts (client_name, date, workout_type, duration_min, notes) "
        "VALUES (?, ?, ?, ?, ?)",
        ("Alice", "2026-01-01", "Cardio", 30, "Easy run"),
    )
    app.conn.commit()
    app.refresh_workouts()
    assert app.tree_workouts.values == [("2026-01-01", "Cardio", 30, "Easy run")]

    _patch_widgets(monkeypatch)
    buttons = []

    def button_factory(*args, **kwargs):
        button = FakeButton(*args, **kwargs)
        buttons.append(button)
        return button

    monkeypatch.setattr(app_module.ttk, "Button", button_factory)
    monkeypatch.setattr(
        app_module.tk,
        "StringVar",
        lambda **kwargs: DummyVar(kwargs.get("value", "Cardio")),
    )
    monkeypatch.setattr(app_module.tk, "IntVar", lambda **kwargs: DummyVar(45))
    app.refresh_workouts = lambda: None
    app.add_workout()
    buttons[-1].command()
    workout = app.cur.execute(
        "SELECT date, workout_type, duration_min, notes FROM workouts "
        "WHERE client_name='Alice' ORDER BY rowid DESC"
    ).fetchone()
    assert workout[0]  # Defaults to today's date.
    assert workout[1:] == ("Cardio", 45, "Cardio")
    app.conn.close()


def test_clear_root_destroys_existing_widgets():
    app = app_module.ACEestApp.__new__(app_module.ACEestApp)

    class Child:
        def __init__(self):
            self.destroyed = False

        def destroy(self):
            self.destroyed = True

    children = [Child(), Child()]
    app.root = FakeWidget()
    app.root.children = children

    app.clear_root()

    assert all(child.destroyed for child in children)
