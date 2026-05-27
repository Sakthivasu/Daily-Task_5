from flask import Flask, request, jsonify, session, send_from_directory
from flask_bcrypt import Bcrypt
from flask_cors import CORS
import mysql.connector
from datetime import datetime

app = Flask(__name__, static_folder="static")

app.secret_key = "EXPENSE_TRACKER"

bcrypt = Bcrypt(app)

CORS(app, supports_credentials=True)


# ================= DATABASE CONNECTION =================

def get_db():

    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="12345",
        database="expense_tracker"
    )

    return db, db.cursor(dictionary=True)


# ================= HTML PAGES =================

@app.route("/")
def login_page():
    return send_from_directory("static", "login.html")


@app.route("/register.html")
def register_page():
    return send_from_directory("static", "register.html")


@app.route("/dashboard.html")
def dashboard_page():
    return send_from_directory("static", "dashboard.html")


@app.route("/expenses.html")
def expenses_page():
    return send_from_directory("static", "expenses.html")


# ================= REGISTER =================

@app.route("/register", methods=["POST"])
def register():

    data = request.get_json()

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    db, cursor = get_db()

    cursor.execute(
        "SELECT * FROM users WHERE username=%s OR email=%s",
        (username, email)
    )

    user = cursor.fetchone()

    if user:
        cursor.close()
        db.close()

        return jsonify({
            "message": "User already exists"
        }), 400

    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

    cursor.execute(
        "INSERT INTO users(username,email,password) VALUES(%s,%s,%s)",
        (username, email, hashed_password)
    )

    db.commit()

    cursor.close()
    db.close()

    return jsonify({
        "message": "Registration successful"
    }), 201


# ================= LOGIN =================

@app.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    db, cursor = get_db()

    cursor.execute(
        "SELECT * FROM users WHERE username=%s",
        (username,)
    )

    user = cursor.fetchone()

    cursor.close()
    db.close()

    if user and bcrypt.check_password_hash(user["password"], password):

        session["user_id"] = user["id"]
        session["username"] = user["username"]

        return jsonify({
            "message": "Login successful",
            "username": user["username"]
        }), 200

    return jsonify({
        "message": "Invalid username or password"
    }), 401


# ================= LOGOUT =================

@app.route("/logout")
def logout():

    session.clear()

    return jsonify({
        "message": "Logged out successfully"
    }), 200


# ================= GET EXPENSES =================

@app.route("/expenses", methods=["GET"])
def get_expenses():

    if "user_id" not in session:

        return jsonify({
            "message": "Unauthorized"
        }), 401

    db, cursor = get_db()

    cursor.execute(
        "SELECT * FROM expenses WHERE user_id=%s ORDER BY date DESC",
        (session["user_id"],)
    )

    expenses = cursor.fetchall()

    cursor.close()
    db.close()

    return jsonify(expenses), 200


# ================= ADD EXPENSE =================

@app.route("/expenses", methods=["POST"])
def add_expense():

    if "user_id" not in session:

        return jsonify({
            "message": "Unauthorized"
        }), 401

    data = request.get_json()

    title = data.get("title")
    amount = data.get("amount")
    category = data.get("category")
    date = data.get("date")
    note = data.get("note")

    # VALIDATION

    if not title or not amount or not category or not date:

        return jsonify({
            "message": "All fields are required"
        }), 400

    try:

        amount = float(amount)

        if amount <= 0:
            return jsonify({
                "message": "Amount must be positive"
            }), 400

    except:
        return jsonify({
            "message": "Invalid amount"
        }), 400

    try:

        datetime.strptime(date, "%Y-%m-%d")

    except:
        return jsonify({
            "message": "Invalid date format"
        }), 400

    db, cursor = get_db()

    cursor.execute(
        """
        INSERT INTO expenses
        (user_id, title, amount, category, date, note)
        VALUES(%s,%s,%s,%s,%s,%s)
        """,
        (
            session["user_id"],
            title,
            amount,
            category,
            date,
            note
        )
    )

    db.commit()

    cursor.close()
    db.close()

    return jsonify({
        "message": "Expense added successfully"
    }), 201


# ================= DELETE EXPENSE =================

@app.route("/expenses/<int:id>", methods=["DELETE"])
def delete_expense(id):

    if "user_id" not in session:

        return jsonify({
            "message": "Unauthorized"
        }), 401

    db, cursor = get_db()

    cursor.execute(
        "DELETE FROM expenses WHERE id=%s AND user_id=%s",
        (id, session["user_id"])
    )

    db.commit()

    if cursor.rowcount == 0:

        cursor.close()
        db.close()

        return jsonify({
            "message": "Expense not found"
        }), 404

    cursor.close()
    db.close()

    return jsonify({
        "message": "Expense deleted successfully"
    }), 200


# ================= EXPENSE SUMMARY =================

@app.route("/expenses/summary")
def expense_summary():

    if "user_id" not in session:

        return jsonify({
            "message": "Unauthorized"
        }), 401

    db, cursor = get_db()

    uid = session["user_id"]

    # TOTAL AMOUNT

    cursor.execute(
        "SELECT SUM(amount) AS total FROM expenses WHERE user_id=%s",
        (uid,)
    )

    total = cursor.fetchone()["total"] or 0

    # HIGHEST EXPENSE

    cursor.execute(
        "SELECT MAX(amount) AS highest FROM expenses WHERE user_id=%s",
        (uid,)
    )

    highest = cursor.fetchone()["highest"] or 0

    # TOTAL COUNT

    cursor.execute(
        "SELECT COUNT(*) AS count FROM expenses WHERE user_id=%s",
        (uid,)
    )

    count = cursor.fetchone()["count"]

    # CATEGORY DATA

    cursor.execute(
        """
        SELECT category, SUM(amount) AS total
        FROM expenses
        WHERE user_id=%s
        GROUP BY category
        """,
        (uid,)
    )

    categories = cursor.fetchall()

    cursor.close()
    db.close()

    return jsonify({

        "username": session["username"],

        "total_amount": float(total),

        "highest_expense": float(highest),

        "total_expenses": count,

        "categories": categories

    }), 200


# ================= FILTER EXPENSES =================

@app.route("/expenses/filter")
def filter_expenses():

    if "user_id" not in session:

        return jsonify({
            "message": "Unauthorized"
        }), 401

    category = request.args.get("category")
    from_date = request.args.get("from")
    to_date = request.args.get("to")

    query = "SELECT * FROM expenses WHERE user_id=%s"

    values = [session["user_id"]]

    if category:

        query += " AND category=%s"

        values.append(category)

    if from_date and to_date:

        query += " AND date BETWEEN %s AND %s"

        values.extend([from_date, to_date])

    query += " ORDER BY date DESC"

    db, cursor = get_db()

    cursor.execute(query, tuple(values))

    expenses = cursor.fetchall()

    cursor.close()
    db.close()

    return jsonify(expenses), 200


# ================= RUN SERVER =================

if __name__ == "__main__":

    app.run(debug=True)