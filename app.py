from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
from datetime import date

app = Flask(__name__)
app.secret_key = "smart-library-management-system-secret-key-2026"
DB = "library.db"

DEFAULT_CATEGORIES = [
    "Programming",
    "Database Systems",
    "Web Development",
    "Artificial Intelligence & ML",
    "Computer Networks",
    "Data Structures & Algorithms",
    "Mathematics & Statistics",
    "Operating Systems",
    "Cybersecurity",
    "Cloud Computing",
    "Electronics & IoT",
    "Business & Management",
    "Literature & Humanities"
]

def db():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c

def init():
    c = db()
    c.execute("""CREATE TABLE IF NOT EXISTS books(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        author TEXT,
        category TEXT,
        price REAL,
        status TEXT DEFAULT 'Available',
        isbn TEXT DEFAULT '',
        rack TEXT DEFAULT ''
    )""")
    
    # Safely ensure isbn and rack columns exist if table was created previously
    existing_cols = [row[1] for row in c.execute("PRAGMA table_info(books)").fetchall()]
    if "isbn" not in existing_cols:
        c.execute("ALTER TABLE books ADD COLUMN isbn TEXT DEFAULT ''")
    if "rack" not in existing_cols:
        c.execute("ALTER TABLE books ADD COLUMN rack TEXT DEFAULT ''")

    c.execute("""CREATE TABLE IF NOT EXISTS issues(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        book_id INTEGER,
        student TEXT,
        phone TEXT,
        issue_date TEXT,
        due_date TEXT,
        return_date TEXT,
        fee REAL DEFAULT 0,
        status TEXT DEFAULT 'Issued'
    )""")

    if c.execute("SELECT COUNT(*) FROM books").fetchone()[0] == 0:
        c.executemany(
            "INSERT INTO books(title, author, category, price, isbn, rack) VALUES(?,?,?,?,?,?)",
            [
                ("Python Basics", "R. Sharma", "Programming", 450, "978-0134076423", "Rack A-1"),
                ("Database Systems", "A. Kumar", "Database Systems", 550, "978-0133970777", "Rack B-2"),
                ("Web Development", "S. Rao", "Web Development", 500, "978-1491950296", "Rack C-1"),
                ("Data Structures", "M. Singh", "Programming", 600, "978-0262033848", "Rack A-2")
            ]
        )
    c.commit()
    c.close()

@app.route("/")
def home():
    c = db()
    q = request.args.get("q", "").strip()
    available_only = request.args.get("available_only", "")

    query = "SELECT * FROM books WHERE 1=1"
    params = []
    if q:
        query += " AND (title LIKE ? OR author LIKE ? OR category LIKE ? OR isbn LIKE ?)"
        params.extend([f"%{q}%", f"%{q}%", f"%{q}%", f"%{q}%"])
    
    if available_only == "1":
        query += " AND status = 'Available'"

    query += " ORDER BY id DESC"
    books = c.execute(query, params).fetchall()

    avail_count = 0
    if q:
        avail_count = len([b for b in books if b["status"] == "Available"])

    issues = c.execute(
        "SELECT i.*, b.title, b.isbn FROM issues i JOIN books b ON i.book_id = b.id ORDER BY i.id DESC"
    ).fetchall()
    stats = [
        c.execute("SELECT COUNT(*) FROM books").fetchone()[0],
        c.execute("SELECT COUNT(*) FROM books WHERE status='Available'").fetchone()[0],
        c.execute("SELECT COUNT(*) FROM issues WHERE status='Issued'").fetchone()[0],
        c.execute("SELECT COALESCE(SUM(fee),0) FROM issues").fetchone()[0]
    ]
    c.close()
    return render_template(
        "home.html",
        books=books,
        issues=issues,
        stats=stats,
        categories=DEFAULT_CATEGORIES,
        q=q,
        available_only=available_only,
        avail_count=avail_count
    )

@app.route("/api/search-available")
def api_search_available():
    q = request.args.get("q", "").strip()
    filter_mode = request.args.get("filter", "all").strip()
    if not q:
        return jsonify([])
    c = db()
    query = "SELECT id, title, author, category, rack, price, status FROM books WHERE (title LIKE ? OR author LIKE ? OR category LIKE ? OR isbn LIKE ? OR rack LIKE ?)"
    params = [f"%{q}%", f"%{q}%", f"%{q}%", f"%{q}%", f"%{q}%"]
    if filter_mode == "available":
        query += " AND status='Available'"
    query += " ORDER BY CASE WHEN status='Available' THEN 0 ELSE 1 END, title ASC LIMIT 8"
    books = c.execute(query, params).fetchall()
    c.close()
    return jsonify([dict(b) for b in books])

@app.route("/admin")
def admin():
    c = db()
    q = request.args.get("q", "").strip()
    cat = request.args.get("cat", "").strip()
    status_filter = request.args.get("status", "").strip()

    query = "SELECT * FROM books WHERE 1=1"
    params = []

    if q:
        query += " AND (title LIKE ? OR author LIKE ? OR isbn LIKE ? OR rack LIKE ?)"
        params.extend([f"%{q}%", f"%{q}%", f"%{q}%", f"%{q}%"])
    if cat:
        query += " AND category = ?"
        params.append(cat)
    if status_filter:
        query += " AND status = ?"
        params.append(status_filter)

    query += " ORDER BY id DESC"
    books = c.execute(query, params).fetchall()

    # Dynamic list of all categories present in the database + defaults
    db_cats = [r[0] for r in c.execute("SELECT DISTINCT category FROM books WHERE category IS NOT NULL AND category != ''").fetchall()]
    all_categories = sorted(list(set(DEFAULT_CATEGORIES + db_cats)))

    stats = {
        "total": c.execute("SELECT COUNT(*) FROM books").fetchone()[0],
        "available": c.execute("SELECT COUNT(*) FROM books WHERE status='Available'").fetchone()[0],
        "issued": c.execute("SELECT COUNT(*) FROM books WHERE status='Issued'").fetchone()[0],
        "total_val": c.execute("SELECT COALESCE(SUM(price), 0) FROM books").fetchone()[0]
    }
    c.close()
    return render_template(
        "admin.html",
        books=books,
        stats=stats,
        categories=all_categories,
        q=q,
        current_cat=cat,
        current_status=status_filter
    )

@app.route("/admin/add", methods=["POST"])
@app.route("/add", methods=["POST"])
def add_book():
    f = request.form
    title = f.get("title", "").strip()
    author = f.get("author", "").strip()
    
    # Check if category is "Other" or custom
    selected_cat = f.get("category", "").strip()
    custom_cat = f.get("custom_category", "").strip()
    category = custom_cat if selected_cat == "Other" and custom_cat else (selected_cat or "General")

    try:
        price = float(f.get("price", 0))
    except (ValueError, TypeError):
        price = 0.0

    isbn = f.get("isbn", "").strip()
    rack = f.get("rack", "").strip()

    try:
        copies = max(1, int(f.get("copies", 1)))
    except (ValueError, TypeError):
        copies = 1

    if not title or not author:
        flash("Book title and author are required.", "error")
        return redirect(request.referrer or url_for("admin"))

    c = db()
    for _ in range(copies):
        c.execute(
            "INSERT INTO books(title, author, category, price, status, isbn, rack) VALUES(?,?,?,?,?,?,?)",
            (title, author, category, price, "Available", isbn, rack)
        )
    c.commit()
    c.close()

    flash(f"Successfully added {copies} cop{'ies' if copies > 1 else 'y'} of '{title}' to the catalog.", "success")
    return redirect(request.referrer or url_for("admin"))

@app.route("/admin/edit/<int:bid>", methods=["POST"])
def edit_book(bid):
    f = request.form
    title = f.get("title", "").strip()
    author = f.get("author", "").strip()
    
    selected_cat = f.get("category", "").strip()
    custom_cat = f.get("custom_category", "").strip()
    category = custom_cat if selected_cat == "Other" and custom_cat else (selected_cat or "General")

    try:
        price = float(f.get("price", 0))
    except (ValueError, TypeError):
        price = 0.0

    isbn = f.get("isbn", "").strip()
    rack = f.get("rack", "").strip()
    status = f.get("status", "Available").strip()

    if not title or not author:
        flash("Title and author are required.", "error")
        return redirect(url_for("admin"))

    c = db()
    c.execute(
        "UPDATE books SET title=?, author=?, category=?, price=?, isbn=?, rack=?, status=? WHERE id=?",
        (title, author, category, price, isbn, rack, status, bid)
    )
    c.commit()
    c.close()

    flash(f"Book '{title}' (ID #{bid}) updated successfully.", "success")
    return redirect(url_for("admin"))

@app.route("/admin/delete/<int:bid>", methods=["POST", "GET"])
def delete_book(bid):
    c = db()
    book = c.execute("SELECT * FROM books WHERE id=?", (bid,)).fetchone()
    if not book:
        c.close()
        flash("Book record not found.", "error")
        return redirect(url_for("admin"))

    if book["status"] == "Issued":
        c.close()
        flash(f"Cannot delete '{book['title']}' because it is currently issued to a student. Return the book first.", "error")
        return redirect(url_for("admin"))

    c.execute("DELETE FROM books WHERE id=?", (bid,))
    c.commit()
    c.close()

    flash(f"Book '{book['title']}' (ID #{bid}) was deleted from the catalog.", "success")
    return redirect(url_for("admin"))

@app.route("/issue", methods=["GET", "POST"])
def issue():
    c = db()
    if request.method == "POST":
        f = request.form
        try:
            bid = int(f["book_id"])
        except (ValueError, KeyError):
            c.close()
            flash("Invalid book selected.", "error")
            return redirect(url_for("issue"))

        book = c.execute("SELECT * FROM books WHERE id=? AND status='Available'", (bid,)).fetchone()
        if not book:
            c.close()
            flash("Selected book is currently unavailable.", "error")
            return redirect(url_for("issue"))

        cur = c.execute(
            "INSERT INTO issues(book_id, student, phone, issue_date, due_date) VALUES(?,?,?,?,?)",
            (bid, f.get("student", "").strip(), f.get("phone", "").strip(), f.get("issue_date"), f.get("due_date"))
        )
        c.execute("UPDATE books SET status='Issued' WHERE id=?", (bid,))
        c.commit()
        iid = cur.lastrowid
        c.close()
        flash(f"Book '{book['title']}' issued successfully to {f.get('student')}.", "success")
        return redirect(url_for("receipt", iid=iid))

    books = c.execute("SELECT * FROM books WHERE status='Available' ORDER BY title ASC").fetchall()
    c.close()
    return render_template("issue.html", books=books)

@app.route("/return/<int:iid>")
def ret(iid):
    c = db()
    i = c.execute("SELECT * FROM issues WHERE id=?", (iid,)).fetchone()
    if i and i["status"] == "Issued":
        try:
            due = date.fromisoformat(i["due_date"])
        except (ValueError, TypeError):
            due = date.today()

        today = date.today()
        days = max(0, (today - due).days)
        fee = days * 10
        c.execute(
            "UPDATE issues SET return_date=?, fee=?, status='Returned' WHERE id=?",
            (today.isoformat(), fee, iid)
        )
        c.execute("UPDATE books SET status='Available' WHERE id=?", (i["book_id"],))
        c.commit()
        flash(f"Book returned successfully. Late fine: ₹{fee:.2f}", "success")
    c.close()
    return redirect(url_for("receipt", iid=iid))

@app.route("/receipt/<int:iid>")
def receipt(iid):
    c = db()
    i = c.execute(
        "SELECT i.*, b.title, b.author, b.price, b.isbn, b.rack FROM issues i JOIN books b ON i.book_id=b.id WHERE i.id=?",
        (iid,)
    ).fetchone()
    c.close()
    if not i:
        flash("Receipt record not found.", "error")
        return redirect(url_for("home"))
    return render_template("receipt.html", i=i)

if __name__ == "__main__":
    init()
    app.run(debug=True)
