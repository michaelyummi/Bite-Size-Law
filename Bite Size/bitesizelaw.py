import os
import re
from difflib import get_close_matches

from flask import Flask, jsonify, render_template, request
import sqlite3

#start server with following command:
#cd /home/user/bitesizelaw && . .venv/bin/activate && python "Bite Size/bitesizelaw.py"

#paste into browser for website
#http://127.0.0.1:5000

#use this command to kill previous server
#fuser -k 5000/tcp

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
)

CASE_DATA = {}

CASE_FIELDS = [
    "name",
    "year",
    "court",
    "facts",
    "plaintiff_argument",
    "defendant_argument",
    "ruling",
    "opinion",
    "significance",
]

REQUIRED_CASE_NAMES = {
    "Brown v. Board of Education",
    "Dred Scott v. Sandford",
    "Gideon v. Wainwright",
    "Marbury v. Madison",
    "McCulloch v. Maryland",
    "Miranda v. Arizona",
    "Obergefell v. Hodges",
    "Plessy v. Ferguson",
    "United States v. Lopez",
}

def normalize_case_name(case_name):
    return re.sub(r"[^a-z0-9\s]", "", (case_name or "").lower()).strip()


def find_case(query):
    cleaned_query = normalize_case_name(query)
    if not cleaned_query:
        return None

    case_lookup = {normalize_case_name(key): key for key in CASE_DATA}

    if cleaned_query in case_lookup:
        return CASE_DATA[case_lookup[cleaned_query]]

    close_matches = get_close_matches(cleaned_query, list(case_lookup.keys()), n=1, cutoff=0.5)
    if close_matches:
        return CASE_DATA[case_lookup[close_matches[0]]]

    return None


def _ensure_db_from_sql(db_path, sql_path):
    """If the SQLite DB doesn't exist, create it by running the SQL script at `sql_path`.

    This lets the user edit `database/cases.sql` (adds/inserts) and have the DB created
    automatically the first time the app runs.
    """
    if os.path.exists(db_path):
        return
    if not os.path.exists(sql_path):
        return
    with open(sql_path, "r", encoding="utf-8") as f:
        sql = f.read()
    if not sql.strip():
        return
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(sql)
        conn.commit()
    finally:
        conn.close()


def get_db_connection(db_path=None):
    if db_path is None:
        db_path = os.path.join(BASE_DIR, "database", "cases.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_saved_case_tables(db_path=None):
    conn = get_db_connection(db_path)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS saved_case_folders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS saved_cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                folder_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                year TEXT,
                court TEXT,
                facts TEXT,
                plaintiff_argument TEXT,
                defendant_argument TEXT,
                ruling TEXT,
                opinion TEXT,
                significance TEXT,
                saved_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(folder_id) REFERENCES saved_case_folders(id) ON DELETE CASCADE
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def ensure_database_matches_seed(db_path=None):
    if db_path is None:
        db_path = os.path.join(BASE_DIR, "database", "cases.db")
    sql_path = os.path.join(BASE_DIR, "database", "cases.sql")
    if not os.path.exists(sql_path):
        return
    if not os.path.exists(db_path):
        _ensure_db_from_sql(db_path, sql_path)
        return

    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute("SELECT name FROM cases").fetchall()
        existing_names = {row[0] for row in rows}
        missing_cases = REQUIRED_CASE_NAMES - existing_names
        if missing_cases:
            conn.close()
            os.remove(db_path)
            _ensure_db_from_sql(db_path, sql_path)
            return
    finally:
        conn.close()


def load_cases_from_db(db_path=None):
    """Load cases from a SQLite database and return a dict matching the original CASE_DATA shape."""
    if db_path is None:
        db_path = os.path.join(BASE_DIR, "database", "cases.db")

    sql_path = os.path.join(BASE_DIR, "database", "cases.sql")
    ensure_database_matches_seed(db_path)
    _ensure_db_from_sql(db_path, sql_path)

    cases = {}
    if not os.path.exists(db_path):
        return cases

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT name, year, court, facts, plaintiff_argument, defendant_argument, ruling, opinion, significance FROM cases"
        )
        rows = cur.fetchall()
        for r in rows:
            key = normalize_case_name(r["name"])
            cases[key] = {
                "name": r["name"],
                "year": r["year"] or "Not specified",
                "court": r["court"] or "Not specified",
                "facts": r["facts"] or "",
                "plaintiff_argument": r["plaintiff_argument"] or "",
                "defendant_argument": r["defendant_argument"] or "",
                "ruling": r["ruling"] or "",
                "opinion": r["opinion"] or "",
                "significance": r["significance"] or "",
            }
    finally:
        conn.close()

    return cases


def normalize_case_payload(payload, case_name=None, source="known_case"):
    case_name = (case_name or payload.get("name") or "Unknown case").strip() or "Unknown case"
    base = {
        "name": case_name,
        "year": "Not specified",
        "court": "Not specified",
        "facts": "",
        "plaintiff_argument": "",
        "defendant_argument": "",
        "ruling": "",
        "opinion": "",
        "significance": "",
    }

    if isinstance(payload, dict):
        for field in CASE_FIELDS:
            value = payload.get(field)
            if value is not None and str(value).strip():
                base[field] = str(value).strip()

    base["name"] = base["name"].strip() or case_name
    if source:
        base["source"] = source
    return base


def sql_quote(value):
    if value is None:
        return "NULL"
    return "'" + str(value).replace("'", "''") + "'"


def append_case_to_sql_file(case_record):
    sql_path = os.path.join(BASE_DIR, "database", "cases.sql")
    if not os.path.exists(sql_path):
        with open(sql_path, "w", encoding="utf-8") as f:
            f.write("PRAGMA foreign_keys = OFF;\nBEGIN TRANSACTION;\n\n")

    insert_sql = f"""
INSERT INTO cases (
    name,
    year,
    court,
    facts,
    plaintiff_argument,
    defendant_argument,
    ruling,
    opinion,
    significance
) VALUES (
    {sql_quote(case_record['name'])},
    {sql_quote(case_record['year'])},
    {sql_quote(case_record['court'])},
    {sql_quote(case_record['facts'])},
    {sql_quote(case_record['plaintiff_argument'])},
    {sql_quote(case_record['defendant_argument'])},
    {sql_quote(case_record['ruling'])},
    {sql_quote(case_record['opinion'])},
    {sql_quote(case_record['significance'])}
);
"""

    with open(sql_path, "r+", encoding="utf-8") as f:
        contents = f.read()
        if "COMMIT;" in contents:
            updated = contents.rsplit("COMMIT;", 1)[0].rstrip() + "\n\n" + insert_sql.strip() + "\n\nCOMMIT;\n"
        else:
            updated = (contents.rstrip() + "\n\n" + insert_sql.strip() + "\n").strip() + "\n"
        f.seek(0)
        f.truncate()
        f.write(updated)


def insert_case_into_db(payload):
    global CASE_DATA
    db_path = os.path.join(BASE_DIR, "database", "cases.db")
    sql_path = os.path.join(BASE_DIR, "database", "cases.sql")
    _ensure_db_from_sql(db_path, sql_path)

    case_record = normalize_case_payload(payload, case_name=payload.get("name"), source="manual")
    if not case_record["name"].strip():
        raise ValueError("Case name is required.")

    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT 1 FROM cases WHERE LOWER(name) = LOWER(?)",
            (case_record["name"],),
        )
        if cur.fetchone():
            raise ValueError(f"Case already exists: {case_record['name']}")

        cur.execute(
            """
            INSERT INTO cases (
                name, year, court, facts, plaintiff_argument,
                defendant_argument, ruling, opinion, significance
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                case_record["name"],
                case_record["year"],
                case_record["court"],
                case_record["facts"],
                case_record["plaintiff_argument"],
                case_record["defendant_argument"],
                case_record["ruling"],
                case_record["opinion"],
                case_record["significance"],
            ),
        )
        conn.commit()
    finally:
        conn.close()

    append_case_to_sql_file(case_record)
    CASE_DATA = load_cases_from_db()
    return case_record


def generate_case_summary(case_name):
    known_case = find_case(case_name)
    if known_case:
        return normalize_case_payload(dict(known_case), case_name=case_name, source="known_case")
    return None


# Load CASE_DATA from the SQLite database (creates the DB from database/cases.sql if needed)
CASE_DATA = load_cases_from_db()
ensure_saved_case_tables()


@app.route("/api/cases", methods=["GET"])
def api_cases():
    case_names = [entry["name"] for entry in CASE_DATA.values()]
    return jsonify({"cases": sorted(case_names)})


@app.route("/api/cases/all", methods=["GET"])
def api_cases_all():
    conn = get_db_connection()
    try:
        rows = conn.execute(
            """
            SELECT id, name, year, court, facts, plaintiff_argument, defendant_argument, ruling, opinion, significance
            FROM cases
            ORDER BY name COLLATE NOCASE
            """
        ).fetchall()
        return jsonify({"cases": [dict(row) for row in rows]})
    finally:
        conn.close()


@app.route("/api/cases/<int:case_id>", methods=["GET", "PUT", "DELETE"])
def api_case_detail(case_id):
    global CASE_DATA
    conn = get_db_connection()
    try:
        case_row = conn.execute(
            """
            SELECT id, name, year, court, facts, plaintiff_argument, defendant_argument, ruling, opinion, significance
            FROM cases WHERE id = ?
            """,
            (case_id,),
        ).fetchone()
    finally:
        conn.close()

    if case_row is None:
        return jsonify({"error": "Case not found."}), 404

    if request.method == "GET":
        return jsonify(dict(case_row))

    if request.method == "DELETE":
        conn = get_db_connection()
        try:
            cursor = conn.execute("DELETE FROM cases WHERE id = ?", (case_id,))
            conn.commit()
            if cursor.rowcount == 0:
                return jsonify({"error": "Case not found."}), 404
        finally:
            conn.close()

        CASE_DATA = load_cases_from_db()
        return jsonify({"deleted": True, "case_id": case_id})

    data = request.get_json(silent=True) or {}
    if not isinstance(data, dict):
        return jsonify({"error": "Case data must be sent as JSON."}), 400

    payload = normalize_case_payload(data, case_name=data.get("name"), source="database")
    if not payload["name"].strip():
        return jsonify({"error": "Case name is required."}), 400

    conn = get_db_connection()
    try:
        duplicate = conn.execute(
            "SELECT id FROM cases WHERE LOWER(name) = LOWER(?) AND id != ?",
            (payload["name"], case_id),
        ).fetchone()
        if duplicate:
            return jsonify({"error": "A case with that name already exists."}), 400

        conn.execute(
            """
            UPDATE cases
            SET name = ?, year = ?, court = ?, facts = ?, plaintiff_argument = ?, defendant_argument = ?, ruling = ?, opinion = ?, significance = ?
            WHERE id = ?
            """,
            (
                payload["name"],
                payload["year"],
                payload["court"],
                payload["facts"],
                payload["plaintiff_argument"],
                payload["defendant_argument"],
                payload["ruling"],
                payload["opinion"],
                payload["significance"],
                case_id,
            ),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "A case with that name already exists."}), 400
    finally:
        conn.close()

    CASE_DATA = load_cases_from_db()

    return jsonify({
        "id": case_id,
        "name": payload["name"],
        "year": payload["year"],
        "court": payload["court"],
        "facts": payload["facts"],
        "plaintiff_argument": payload["plaintiff_argument"],
        "defendant_argument": payload["defendant_argument"],
        "ruling": payload["ruling"],
        "opinion": payload["opinion"],
        "significance": payload["significance"],
    })


@app.errorhandler(500)
def handle_500(error):
    return jsonify({
        "error": "The case data could not be generated."
    }), 500


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/case", methods=["POST"])
def api_case():
    data = request.get_json(silent=True) or {}
    case_name = data.get("case_name", "").strip()

    if not case_name:
        return jsonify({"error": "Please enter a case name."}), 400

    summary = generate_case_summary(case_name)
    if summary is None:
        return jsonify({
            "error": f"Case not found: '{case_name}'. Add it to CASE_DATA using the same fields as the sample cases."
        }), 404

    return jsonify(summary)


@app.route("/api/saved-folders", methods=["GET", "POST"])
def api_saved_folders():
    ensure_saved_case_tables()

    if request.method == "GET":
        conn = get_db_connection()
        try:
            rows = conn.execute(
                "SELECT id, name FROM saved_case_folders ORDER BY name COLLATE NOCASE"
            ).fetchall()
            folders = [{"id": row["id"], "name": row["name"]} for row in rows]
            return jsonify({"folders": folders})
        finally:
            conn.close()

    data = request.get_json(silent=True) or {}
    folder_name = str(data.get("name", "")).strip()
    if not folder_name:
        return jsonify({"error": "Folder name is required."}), 400

    folder_name = re.sub(r"\s+", " ", folder_name)

    conn = get_db_connection()
    try:
        conn.execute(
            "INSERT OR IGNORE INTO saved_case_folders (name) VALUES (?)",
            (folder_name,),
        )
        conn.commit()
        row = conn.execute(
            "SELECT id, name FROM saved_case_folders WHERE name = ?",
            (folder_name,),
        ).fetchone()
    finally:
        conn.close()

    if row is None:
        return jsonify({"error": "Unable to create folder."}), 400

    return jsonify({"id": row["id"], "name": row["name"]}), 201


@app.route("/api/saved-folders/<int:folder_id>", methods=["PUT", "DELETE"])
def api_saved_folder_detail(folder_id):
    ensure_saved_case_tables()

    if request.method == "PUT":
        data = request.get_json(silent=True) or {}
        folder_name = str(data.get("name", "")).strip()
        if not folder_name:
            return jsonify({"error": "Folder name is required."}), 400

        folder_name = re.sub(r"\s+", " ", folder_name)
        conn = get_db_connection()
        try:
            try:
                cursor = conn.execute(
                    "UPDATE saved_case_folders SET name = ? WHERE id = ?",
                    (folder_name, folder_id),
                )
                conn.commit()
            except sqlite3.IntegrityError:
                return jsonify({"error": "A folder with that name already exists."}), 400

            if cursor.rowcount == 0:
                return jsonify({"error": "Folder not found."}), 404
            return jsonify({"updated": True, "folder_id": folder_id, "name": folder_name})
        finally:
            conn.close()

    conn = get_db_connection()
    try:
        cursor = conn.execute("DELETE FROM saved_case_folders WHERE id = ?", (folder_id,))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "Folder not found."}), 404
        return jsonify({"deleted": True, "folder_id": folder_id})
    finally:
        conn.close()


@app.route("/api/saved-cases", methods=["GET"])
def api_saved_cases():
    ensure_saved_case_tables()
    conn = get_db_connection()
    try:
        rows = conn.execute(
            """
            SELECT
                sf.id AS folder_id,
                sf.name AS folder_name,
                sc.id AS case_id,
                sc.name,
                sc.year,
                sc.court,
                sc.facts,
                sc.plaintiff_argument,
                sc.defendant_argument,
                sc.ruling,
                sc.opinion,
                sc.significance,
                sc.saved_at
            FROM saved_case_folders sf
            LEFT JOIN saved_cases sc ON sc.folder_id = sf.id
            ORDER BY sf.name COLLATE NOCASE, sc.saved_at DESC
            """
        ).fetchall()

        folders = {}
        for row in rows:
            folder_id = row["folder_id"]
            if folder_id not in folders:
                folders[folder_id] = {
                    "id": folder_id,
                    "name": row["folder_name"],
                    "cases": [],
                }
            if row["case_id"] is not None:
                folders[folder_id]["cases"].append({
                    "id": row["case_id"],
                    "name": row["name"],
                    "year": row["year"],
                    "court": row["court"],
                    "facts": row["facts"],
                    "plaintiff_argument": row["plaintiff_argument"],
                    "defendant_argument": row["defendant_argument"],
                    "ruling": row["ruling"],
                    "opinion": row["opinion"],
                    "significance": row["significance"],
                    "saved_at": row["saved_at"],
                })

        return jsonify({"folders": list(folders.values())})
    finally:
        conn.close()


@app.route("/api/saved-cases/save", methods=["POST"])
def api_save_case_to_folder():
    ensure_saved_case_tables()

    data = request.get_json(silent=True) or {}
    folder_id = data.get("folder_id")
    case_data = data.get("case") or {}
    case_name = (case_data.get("name") or data.get("name") or "").strip()

    if not folder_id:
        return jsonify({"error": "Please select a folder."}), 400
    if not case_name:
        return jsonify({"error": "Case information is missing."}), 400

    conn = get_db_connection()
    try:
        folder = conn.execute(
            "SELECT id, name FROM saved_case_folders WHERE id = ?",
            (folder_id,),
        ).fetchone()
        if folder is None:
            return jsonify({"error": "Folder not found."}), 404

        payload = normalize_case_payload(case_data, case_name=case_name, source="saved")
        conn.execute(
            """
            INSERT INTO saved_cases (
                folder_id,
                name,
                year,
                court,
                facts,
                plaintiff_argument,
                defendant_argument,
                ruling,
                opinion,
                significance
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                folder["id"],
                payload["name"],
                payload["year"],
                payload["court"],
                payload["facts"],
                payload["plaintiff_argument"],
                payload["defendant_argument"],
                payload["ruling"],
                payload["opinion"],
                payload["significance"],
            ),
        )
        conn.commit()
        saved_case = conn.execute(
            "SELECT id, name, year, court, facts, plaintiff_argument, defendant_argument, ruling, opinion, significance, saved_at FROM saved_cases WHERE folder_id = ? AND name = ? ORDER BY id DESC LIMIT 1",
            (folder["id"], payload["name"]),
        ).fetchone()
    finally:
        conn.close()

    return jsonify({
        "folder_id": folder_id,
        "folder_name": folder["name"],
        "case": {
            "id": saved_case["id"],
            "name": saved_case["name"],
            "year": saved_case["year"],
            "court": saved_case["court"],
            "facts": saved_case["facts"],
            "plaintiff_argument": saved_case["plaintiff_argument"],
            "defendant_argument": saved_case["defendant_argument"],
            "ruling": saved_case["ruling"],
            "opinion": saved_case["opinion"],
            "significance": saved_case["significance"],
            "saved_at": saved_case["saved_at"],
        }
    })


@app.route("/api/saved-cases/<int:case_id>", methods=["DELETE"])
def api_delete_saved_case(case_id):
    ensure_saved_case_tables()
    conn = get_db_connection()
    try:
        cursor = conn.execute("DELETE FROM saved_cases WHERE id = ?", (case_id,))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "Saved case not found."}), 404
        return jsonify({"deleted": True, "case_id": case_id})
    finally:
        conn.close()


@app.route("/api/cases/add", methods=["POST"])
def api_add_case():
    data = request.get_json(silent=True) or {}
    if not isinstance(data, dict):
        return jsonify({"error": "Case data must be sent as JSON."}), 400

    try:
        case_record = insert_case_into_db(data)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except sqlite3.Error as exc:
        return jsonify({"error": f"Database error: {exc}"}), 500

    return jsonify(case_record), 201


if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "0").lower() in {"1", "true", "yes", "on"}
    app.run(debug=debug_mode, host="0.0.0.0", port=5000, use_reloader=debug_mode)


