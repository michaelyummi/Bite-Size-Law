#files
import os
#text handling
import re
#search logic
from difflib import get_close_matches
#web app logic and web serving
from flask import Flask, jsonify, render_template, request
#connects database to python backend logic
import sqlite3

#start server with following command:
#cd /home/user/bitesizelaw && . .venv/bin/activate && python "Bite Size/bitesizelaw.py"

#paste into browser on host device for website
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
BILL_DATA = {}
REGULATION_DATA = BILL_DATA

#Legal Cases
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

#Congressional Bills
BILL_FIELDS = [
    "name",
    "legislative_body",
    "leading_agency",
    "key_dates",
    "summary_of_facts",
    "issue",
]
REGULATION_FIELDS = BILL_FIELDS

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

#Functions for search mechanism

def normalize_case_name(case_name):
    return re.sub(r"[^a-z0-9\s]", "", (case_name or "").lower()).strip()


def normalize_bill_name(bill_name):
    return re.sub(r"[^a-z0-9\s]", "", (bill_name or "").lower()).strip()


def normalize_regulation_name(regulation_name):
    return normalize_bill_name(regulation_name)

#Function for case look up

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

#Database function logic

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
        buffer = ""
        for line in sql.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("--"):
                continue
            buffer += line + "\n"
            if sqlite3.complete_statement(buffer):
                statement = buffer.strip()
                buffer = ""
                upper = statement.upper()
                if upper.startswith("PRAGMA") or upper.startswith("BEGIN") or upper.startswith("COMMIT") or upper.startswith("ROLLBACK"):
                    continue
                conn.execute(statement)
        if buffer.strip():
            statement = buffer.strip()
            upper = statement.upper()
            if not (upper.startswith("PRAGMA") or upper.startswith("BEGIN") or upper.startswith("COMMIT") or upper.startswith("ROLLBACK")):
                conn.execute(statement)
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

    ensure_bill_tables(db_path)


def ensure_bill_tables(db_path=None):
    conn = get_db_connection(db_path)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS bills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                legislative_body TEXT,
                leading_agency TEXT,
                key_dates TEXT,
                summary_of_facts TEXT,
                issue TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS saved_bills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                folder_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                legislative_body TEXT,
                leading_agency TEXT,
                key_dates TEXT,
                summary_of_facts TEXT,
                issue TEXT,
                saved_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(folder_id) REFERENCES saved_case_folders(id) ON DELETE CASCADE
            )
            """
        )

        for table_name in ("bills", "saved_bills"):
            columns = [row[1] for row in conn.execute(f"PRAGMA table_info({table_name})").fetchall()]
            target_columns = {
                "bills": ["id", "name", "legislative_body", "leading_agency", "key_dates", "summary_of_facts", "issue"],
                "saved_bills": ["id", "folder_id", "name", "legislative_body", "leading_agency", "key_dates", "summary_of_facts", "issue", "saved_at"],
            }[table_name]

            if "legislative_body" not in columns:
                conn.execute(f"ALTER TABLE {table_name} ADD COLUMN legislative_body TEXT")
            if "leading_agency" not in columns:
                conn.execute(f"ALTER TABLE {table_name} ADD COLUMN leading_agency TEXT")

            current_columns = [row[1] for row in conn.execute(f"PRAGMA table_info({table_name})").fetchall()]
            if current_columns != target_columns:
                temp_name = f"{table_name}__reordered"
                conn.execute(f"ALTER TABLE {table_name} RENAME TO {temp_name}")
                if table_name == "bills":
                    conn.execute(
                        """
                        CREATE TABLE bills (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL UNIQUE,
                            legislative_body TEXT,
                            leading_agency TEXT,
                            key_dates TEXT,
                            summary_of_facts TEXT,
                            issue TEXT
                        )
                        """
                    )
                    conn.execute(
                        f"""
                        INSERT INTO bills (id, name, legislative_body, leading_agency, key_dates, summary_of_facts, issue)
                        SELECT id, name, legislative_body, leading_agency, key_dates, summary_of_facts, issue
                        FROM {temp_name}
                        """
                    )
                else:
                    conn.execute(
                        """
                        CREATE TABLE saved_bills (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            folder_id INTEGER NOT NULL,
                            name TEXT NOT NULL,
                            legislative_body TEXT,
                            leading_agency TEXT,
                            key_dates TEXT,
                            summary_of_facts TEXT,
                            issue TEXT,
                            saved_at TEXT DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY(folder_id) REFERENCES saved_case_folders(id) ON DELETE CASCADE
                        )
                        """
                    )
                    conn.execute(
                        f"""
                        INSERT INTO saved_bills (id, folder_id, name, legislative_body, leading_agency, key_dates, summary_of_facts, issue, saved_at)
                        SELECT id, folder_id, name, legislative_body, leading_agency, key_dates, summary_of_facts, issue, saved_at
                        FROM {temp_name}
                        """
                    )
                conn.execute(f"DROP TABLE {temp_name}")

        legacy_bill_tables = [
            ("regulations", "bills"),
            ("saved_regulations", "saved_bills"),
        ]
        for legacy_name, new_name in legacy_bill_tables:
            legacy_exists = conn.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name = ?",
                (legacy_name,),
            ).fetchone()
            if not legacy_exists:
                continue
            new_exists = conn.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name = ?",
                (new_name,),
            ).fetchone()
            if new_exists:
                continue
            conn.execute(
                f"CREATE TABLE {new_name} AS SELECT * FROM {legacy_name}"
            )
            conn.execute(
                f"CREATE UNIQUE INDEX IF NOT EXISTS idx_{new_name}_name ON {new_name}(name)"
            )

        conn.commit()
    finally:
        conn.close()


def ensure_regulation_tables(db_path=None):
    ensure_bill_tables(db_path)


def _backup_saved_tables(db_path):
    if not os.path.exists(db_path):
        return {}

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        backup = {}
        for table_name in ("saved_case_folders", "saved_cases", "saved_bills"):
            table_exists = conn.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name = ?",
                (table_name,),
            ).fetchone()
            if not table_exists:
                continue
            rows = conn.execute(f"SELECT * FROM {table_name}").fetchall()
            backup[table_name] = [dict(row) for row in rows]
        return backup
    finally:
        conn.close()

#Backup database function/logic

def _restore_saved_tables(db_path, backup):
    if not backup:
        return

    conn = sqlite3.connect(db_path)
    try:
        for table_name in ("saved_case_folders", "saved_cases", "saved_bills"):
            rows = backup.get(table_name)
            if not rows:
                continue
            columns = [row[1] for row in conn.execute(f"PRAGMA table_info({table_name})").fetchall()]
            if not columns:
                continue
            conn.execute(f"DELETE FROM {table_name}")
            for row in rows:
                allowed_columns = [column for column in columns if column in row]
                insert_columns = ", ".join(allowed_columns)
                placeholders = ", ".join("?" for _ in allowed_columns)
                values = [row[column] for column in allowed_columns]
                conn.execute(
                    f"INSERT INTO {table_name} ({insert_columns}) VALUES ({placeholders})",
                    values,
                )
        conn.commit()
    finally:
        conn.close()

#backup logic

def _rebuild_database_from_seed(db_path, sql_path):
    saved_backup = _backup_saved_tables(db_path)
    if os.path.exists(db_path):
        os.remove(db_path)
    _ensure_db_from_sql(db_path, sql_path)
    ensure_saved_case_tables(db_path)
    _restore_saved_tables(db_path, saved_backup)


def ensure_database_matches_seed(db_path=None):
    if db_path is None:
        db_path = os.path.join(BASE_DIR, "database", "cases.db")
    sql_path = os.path.join(BASE_DIR, "database", "cases.sql")
    if not os.path.exists(sql_path):
        return

    if not os.path.exists(db_path):
        _ensure_db_from_sql(db_path, sql_path)
        return

    if os.path.getmtime(sql_path) > os.path.getmtime(db_path):
        _rebuild_database_from_seed(db_path, sql_path)
        return

    conn = sqlite3.connect(db_path)
    try:
        table_exists = conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name = 'cases'"
        ).fetchone()
        if table_exists is None:
            conn.close()
            _rebuild_database_from_seed(db_path, sql_path)
            return

        rows = conn.execute("SELECT name FROM cases").fetchall()
        existing_names = {row[0] for row in rows}
        missing_cases = REQUIRED_CASE_NAMES - existing_names
        if missing_cases:
            conn.close()
            _rebuild_database_from_seed(db_path, sql_path)
            return
    finally:
        conn.close()


def refresh_sql_data_if_needed(db_path=None):
    ensure_database_matches_seed(db_path)
    ensure_saved_case_tables(db_path)


def refresh_case_data_if_needed(db_path=None):
    global CASE_DATA
    refresh_sql_data_if_needed(db_path)
    CASE_DATA = load_cases_from_db(db_path)


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

#template for not found database

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

#Bill layout

def normalize_bill_payload(payload, bill_name=None, source="known_bill"):
    bill_name = (bill_name or payload.get("name") or "Unknown bill").strip() or "Unknown bill"
    base = {
        "name": bill_name,
        "legislative_body": "",
        "leading_agency": "",
        "key_dates": "",
        "summary_of_facts": "",
        "issue": "",
    }

    if isinstance(payload, dict):
        for field in BILL_FIELDS:
            value = payload.get(field)
            if value is None:
                aliases = []
                if field == "summary_of_facts":
                    aliases = ["summary", "facts", "summary_facts"]
                elif field == "key_dates":
                    aliases = ["dates", "key_dates"]
                for alias in aliases:
                    if alias in payload and payload.get(alias) is not None:
                        value = payload.get(alias)
                        break
            if value is not None and str(value).strip():
                base[field] = str(value).strip()

    base["name"] = base["name"].strip() or bill_name
    if source:
        base["source"] = source
    return base


def normalize_regulation_payload(payload, regulation_name=None, source="known_regulation"):
    return normalize_bill_payload(payload, bill_name=regulation_name, source=source)


def find_bill(query):
    cleaned_query = normalize_bill_name(query)
    if not cleaned_query:
        return None

    bill_lookup = {normalize_bill_name(key): key for key in BILL_DATA}

    if cleaned_query in bill_lookup:
        return BILL_DATA[bill_lookup[cleaned_query]]

    close_matches = get_close_matches(cleaned_query, list(bill_lookup.keys()), n=1, cutoff=0.5)
    if close_matches:
        return BILL_DATA[bill_lookup[close_matches[0]]]

    return None


def find_regulation(query):
    return find_bill(query)


def load_bills_from_db(db_path=None):
    if db_path is None:
        db_path = os.path.join(BASE_DIR, "database", "cases.db")

    ensure_bill_tables(db_path)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    bills = {}
    try:
        rows = conn.execute(
            """
            SELECT name, legislative_body, leading_agency, key_dates, summary_of_facts, issue
            FROM bills
            ORDER BY name COLLATE NOCASE
            """
        ).fetchall()
        for row in rows:
            key = normalize_bill_name(row["name"])
            bills[key] = {
                "name": row["name"],
                "legislative_body": row["legislative_body"] or "Not specified",
                "leading_agency": row["leading_agency"] or "Not specified",
                "key_dates": row["key_dates"] or "Not specified",
                "summary_of_facts": row["summary_of_facts"] or "",
                "issue": row["issue"] or "",
            }
    finally:
        conn.close()
    return bills


def load_regulations_from_db(db_path=None):
    return load_bills_from_db(db_path)


def generate_case_summary(case_name):
    known_case = find_case(case_name)
    if known_case:
        return normalize_case_payload(dict(known_case), case_name=case_name, source="known_case")
    return None


def generate_bill_summary(bill_name):
    known_bill = find_bill(bill_name)
    if known_bill:
        return normalize_bill_payload(dict(known_bill), bill_name=bill_name, source="known_bill")
    return None


def generate_regulation_summary(regulation_name):
    return generate_bill_summary(regulation_name)


# Load CASE_DATA from the SQLite database (creates the DB from database/cases.sql if needed)
CASE_DATA = load_cases_from_db()
BILL_DATA = load_bills_from_db()
REGULATION_DATA = BILL_DATA
ensure_saved_case_tables()


@app.route("/api/cases", methods=["GET"])
def api_cases():
    refresh_sql_data_if_needed()
    refresh_case_data_if_needed()
    case_names = [entry["name"] for entry in CASE_DATA.values()]
    return jsonify({"cases": sorted(case_names)})


@app.route("/api/cases/all", methods=["GET"])
def api_cases_all():
    refresh_sql_data_if_needed()
    refresh_case_data_if_needed()
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


@app.route("/api/bills", methods=["GET", "POST"])
def api_bills():
    refresh_sql_data_if_needed()
    if request.method == "GET":
        query = (request.args.get("q") or "").strip()
        conn = get_db_connection()
        try:
            if query:
                rows = conn.execute(
                    "SELECT name FROM bills WHERE LOWER(name) LIKE LOWER(?) ORDER BY name COLLATE NOCASE LIMIT 20",
                    (f"%{query}%",),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT name FROM bills ORDER BY name COLLATE NOCASE LIMIT 50"
                ).fetchall()
            return jsonify({"bills": [row["name"] for row in rows]})
        finally:
            conn.close()

    data = request.get_json(silent=True) or {}
    if not isinstance(data, dict):
        return jsonify({"error": "Bill data must be sent as JSON."}), 400

    try:
        bill_record = insert_bill_into_db(data)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except sqlite3.Error as exc:
        return jsonify({"error": f"Database error: {exc}"}), 500

    return jsonify(bill_record), 201


@app.route("/api/regulations", methods=["GET", "POST"])
def api_regulations():
    return api_bills()


@app.route("/api/bills/all", methods=["GET"])
def api_bills_all():
    refresh_sql_data_if_needed()
    conn = get_db_connection()
    try:
        rows = conn.execute(
            """
            SELECT id, name, legislative_body, leading_agency, key_dates, summary_of_facts, issue
            FROM bills
            ORDER BY name COLLATE NOCASE
            """
        ).fetchall()
        return jsonify({"bills": [dict(row) for row in rows]})
    finally:
        conn.close()


@app.route("/api/regulations/all", methods=["GET"])
def api_regulations_all():
    return api_bills_all()


@app.route("/api/bills/<int:bill_id>", methods=["GET", "PUT", "DELETE"])
def api_bill_detail(bill_id):
    global BILL_DATA
    refresh_sql_data_if_needed()
    conn = get_db_connection()
    try:
        bill_row = conn.execute(
            """
            SELECT id, name, legislative_body, leading_agency, key_dates, summary_of_facts, issue
            FROM bills WHERE id = ?
            """,
            (bill_id,),
        ).fetchone()
    finally:
        conn.close()

    if bill_row is None:
        return jsonify({"error": "Bill not found."}), 404

    if request.method == "GET":
        return jsonify(dict(bill_row))

    if request.method == "DELETE":
        conn = get_db_connection()
        try:
            cursor = conn.execute("DELETE FROM bills WHERE id = ?", (bill_id,))
            conn.commit()
            if cursor.rowcount == 0:
                return jsonify({"error": "Bill not found."}), 404
        finally:
            conn.close()

        BILL_DATA = load_bills_from_db()
        REGULATION_DATA = BILL_DATA
        return jsonify({"deleted": True, "bill_id": bill_id})

    data = request.get_json(silent=True) or {}
    if not isinstance(data, dict):
        return jsonify({"error": "Bill data must be sent as JSON."}), 400

    payload = normalize_bill_payload(data, bill_name=data.get("name"), source="database")
    if not payload["name"].strip():
        return jsonify({"error": "Bill name is required."}), 400

    conn = get_db_connection()
    try:
        duplicate = conn.execute(
            "SELECT id FROM bills WHERE LOWER(name) = LOWER(?) AND id != ?",
            (payload["name"], bill_id),
        ).fetchone()
        if duplicate:
            return jsonify({"error": "A bill with that name already exists."}), 400

        conn.execute(
            """
            UPDATE bills
            SET name = ?, legislative_body = ?, leading_agency = ?, key_dates = ?, summary_of_facts = ?, issue = ?
            WHERE id = ?
            """,
            (
                payload["name"],
                payload["legislative_body"],
                payload["leading_agency"],
                payload["key_dates"],
                payload["summary_of_facts"],
                payload["issue"],
                bill_id,
            ),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "A bill with that name already exists."}), 400
    finally:
        conn.close()

    BILL_DATA = load_bills_from_db()
    REGULATION_DATA = BILL_DATA
    return jsonify({
        "id": bill_id,
        "name": payload["name"],
        "legislative_body": payload["legislative_body"],
        "leading_agency": payload["leading_agency"],
        "key_dates": payload["key_dates"],
        "summary_of_facts": payload["summary_of_facts"],
        "issue": payload["issue"],
    })


@app.route("/api/regulations/<int:regulation_id>", methods=["GET", "PUT", "DELETE"])
def api_regulation_detail(regulation_id):
    return api_bill_detail(regulation_id)


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


@app.route("/api/bill", methods=["POST"])
def api_bill():
    data = request.get_json(silent=True) or {}
    bill_name = (data.get("bill_name") or data.get("regulation_name") or data.get("name") or "").strip()

    if not bill_name:
        return jsonify({"error": "Please enter a congressional bill name."}), 400

    summary = generate_bill_summary(bill_name)
    if summary is None:
        return jsonify({
            "error": f"Bill not found: '{bill_name}'. Add it to the bills database using the same fields as the other entries."
        }), 404

    return jsonify(summary)


@app.route("/api/regulation", methods=["POST"])
def api_regulation():
    return api_bill()


@app.route("/api/saved-folders", methods=["GET", "POST"])
def api_saved_folders():
    refresh_sql_data_if_needed()

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
            existing = conn.execute(
                "SELECT id, name FROM saved_case_folders WHERE id = ?",
                (folder_id,),
            ).fetchone()
            if existing is None:
                return jsonify({"error": "Folder not found."}), 404

            duplicate = conn.execute(
                "SELECT id FROM saved_case_folders WHERE LOWER(name) = LOWER(?) AND id != ?",
                (folder_name, folder_id),
            ).fetchone()
            if duplicate:
                return jsonify({"error": "A folder with that name already exists."}), 409

            if existing["name"] == folder_name:
                return jsonify({"updated": True, "folder_id": folder_id, "name": folder_name, "unchanged": True})

            try:
                cursor = conn.execute(
                    "UPDATE saved_case_folders SET name = ? WHERE id = ?",
                    (folder_name, folder_id),
                )
                conn.commit()
            except sqlite3.IntegrityError:
                return jsonify({"error": "A folder with that name already exists."}), 409

            if cursor.rowcount == 0:
                return jsonify({"error": "Folder not found."}), 404
            return jsonify({"updated": True, "folder_id": folder_id, "name": folder_name, "unchanged": False})
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
    refresh_sql_data_if_needed()
    conn = get_db_connection()
    try:
        case_rows = conn.execute(
            """
            SELECT
                sf.id AS folder_id,
                sf.name AS folder_name,
                sc.id AS item_id,
                'case' AS item_type,
                sc.name,
                sc.year,
                sc.court,
                sc.facts,
                sc.plaintiff_argument,
                sc.defendant_argument,
                sc.ruling,
                sc.opinion,
                sc.significance,
                NULL AS legislative_body,
                NULL AS leading_agency,
                NULL AS key_dates,
                NULL AS summary_of_facts,
                NULL AS issue,
                sc.saved_at
            FROM saved_case_folders sf
            LEFT JOIN saved_cases sc ON sc.folder_id = sf.id
            ORDER BY sf.name COLLATE NOCASE, sc.saved_at DESC
            """
        ).fetchall()

        bill_rows = conn.execute(
            """
            SELECT
                sf.id AS folder_id,
                sf.name AS folder_name,
                sb.id AS item_id,
                'bill' AS item_type,
                sb.name,
                NULL AS year,
                NULL AS court,
                NULL AS facts,
                NULL AS plaintiff_argument,
                NULL AS defendant_argument,
                NULL AS ruling,
                NULL AS opinion,
                NULL AS significance,
                sb.legislative_body,
                sb.leading_agency,
                sb.key_dates,
                sb.summary_of_facts,
                sb.issue,
                sb.saved_at
            FROM saved_case_folders sf
            LEFT JOIN saved_bills sb ON sb.folder_id = sf.id
            ORDER BY sf.name COLLATE NOCASE, sb.saved_at DESC
            """
        ).fetchall()

        combined_rows = case_rows + bill_rows
        folders = {}
        for row in combined_rows:
            folder_id = row["folder_id"]
            if folder_id not in folders:
                folders[folder_id] = {
                    "id": folder_id,
                    "name": row["folder_name"],
                    "cases": [],
                }
            if row["item_id"] is None:
                continue
            folders[folder_id]["cases"].append({
                "id": row["item_id"],
                "item_type": row["item_type"],
                "name": row["name"],
                "year": row["year"],
                "court": row["court"],
                "facts": row["facts"],
                "plaintiff_argument": row["plaintiff_argument"],
                "defendant_argument": row["defendant_argument"],
                "ruling": row["ruling"],
                "opinion": row["opinion"],
                "significance": row["significance"],
                "legislative_body": row["legislative_body"],
                "leading_agency": row["leading_agency"],
                "key_dates": row["key_dates"],
                "summary_of_facts": row["summary_of_facts"],
                "issue": row["issue"],
                "saved_at": row["saved_at"],
            })

        for folder in folders.values():
            folder["cases"].sort(key=lambda item: item.get("saved_at") or "", reverse=True)

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


@app.route("/api/saved-bills/save", methods=["POST"])
def api_save_bill_to_folder():
    refresh_sql_data_if_needed()

    data = request.get_json(silent=True) or {}
    folder_id = data.get("folder_id")
    bill_data = data.get("bill") or data.get("regulation") or {}
    bill_name = (bill_data.get("name") or data.get("name") or "").strip()

    if not folder_id:
        return jsonify({"error": "Please select a folder."}), 400
    if not bill_name:
        return jsonify({"error": "Bill information is missing."}), 400

    conn = get_db_connection()
    try:
        folder = conn.execute(
            "SELECT id, name FROM saved_case_folders WHERE id = ?",
            (folder_id,),
        ).fetchone()
        if folder is None:
            return jsonify({"error": "Folder not found."}), 404

        payload = normalize_bill_payload(bill_data, bill_name=bill_name, source="saved")
        conn.execute(
            """
            INSERT INTO saved_bills (
                folder_id,
                name,
                legislative_body,
                leading_agency,
                key_dates,
                summary_of_facts,
                issue
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                folder["id"],
                payload["name"],
                payload["legislative_body"],
                payload["leading_agency"],
                payload["key_dates"],
                payload["summary_of_facts"],
                payload["issue"],
            ),
        )
        conn.commit()
        saved_bill = conn.execute(
            "SELECT id, name, legislative_body, leading_agency, key_dates, summary_of_facts, issue, saved_at FROM saved_bills WHERE folder_id = ? AND name = ? ORDER BY id DESC LIMIT 1",
            (folder["id"], payload["name"]),
        ).fetchone()
    finally:
        conn.close()

    return jsonify({
        "folder_id": folder_id,
        "folder_name": folder["name"],
        "bill": {
            "id": saved_bill["id"],
            "name": saved_bill["name"],
            "legislative_body": saved_bill["legislative_body"],
            "leading_agency": saved_bill["leading_agency"],
            "key_dates": saved_bill["key_dates"],
            "summary_of_facts": saved_bill["summary_of_facts"],
            "issue": saved_bill["issue"],
            "saved_at": saved_bill["saved_at"],
        }
    })

#Input from user logged in server terminal

@app.route("/api/saved-regulations/save", methods=["POST"])
def api_save_regulation_to_folder():
    return api_save_bill_to_folder()

#Input from user logged in server terminal

@app.route("/api/saved-bills/<int:bill_id>", methods=["DELETE"])
def api_delete_saved_bill(bill_id):
    refresh_sql_data_if_needed()
    conn = get_db_connection()
    try:
        cursor = conn.execute("DELETE FROM saved_bills WHERE id = ?", (bill_id,))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "Saved bill not found."}), 404
        return jsonify({"deleted": True, "bill_id": bill_id})
    finally:
        conn.close()

#Input from user logged in server terminal

@app.route("/api/saved-regulations/<int:regulation_id>", methods=["DELETE"])
def api_delete_saved_regulation(regulation_id):
    return api_delete_saved_bill(regulation_id)

#Input from user logged in server terminal

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

#Input from user logged in server terminal

@app.route("/api/bills/add", methods=["POST"])
def api_add_bill():
    data = request.get_json(silent=True) or {}
    if not isinstance(data, dict):
        return jsonify({"error": "Bill data must be sent as JSON."}), 400

    try:
        bill_record = insert_bill_into_db(data)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except sqlite3.Error as exc:
        return jsonify({"error": f"Database error: {exc}"}), 500

    return jsonify(bill_record), 201

#Input from user logged in server terminal

@app.route("/api/regulations/add", methods=["POST"])
def api_add_regulation():
    return api_add_bill()

#function for bill insertion

def insert_bill_into_db(payload):
    global BILL_DATA
    db_path = os.path.join(BASE_DIR, "database", "cases.db")
    ensure_bill_tables(db_path)

    bill_record = normalize_bill_payload(payload, bill_name=payload.get("name"), source="manual")
    if not bill_record["name"].strip():
        raise ValueError("Bill name is required.")

    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT 1 FROM bills WHERE LOWER(name) = LOWER(?)",
            (bill_record["name"],),
        )
        if cur.fetchone():
            raise ValueError(f"Bill already exists: {bill_record['name']}")

        cur.execute(
            """
            INSERT INTO bills (
                name, legislative_body, leading_agency, key_dates, summary_of_facts, issue
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                bill_record["name"],
                bill_record["legislative_body"],
                bill_record["leading_agency"],
                bill_record["key_dates"],
                bill_record["summary_of_facts"],
                bill_record["issue"],
            ),
        )
        conn.commit()
    finally:
        conn.close()

    BILL_DATA = load_bills_from_db()
    REGULATION_DATA = BILL_DATA
    return bill_record

#bills added to database

def insert_regulation_into_db(payload):
    return insert_bill_into_db(payload)

#Ends off the code and runs the website via flask

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)


