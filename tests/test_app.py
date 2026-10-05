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
