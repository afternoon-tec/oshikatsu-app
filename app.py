from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)
DB = "kakeibo.db"

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

# --- トップページ（家計簿表示＋集計） ---
@app.route("/")
def index():
    conn = get_db()
    cur = conn.cursor()

    # 推しごとにデータを取得
    cur.execute("SELECT DISTINCT oshi_name FROM kakeibo ORDER BY oshi_name;")
    oshis = [row["oshi_name"] for row in cur.fetchall()]

    data_by_oshi = {}
    for oshi in oshis:
        cur.execute("SELECT * FROM kakeibo WHERE oshi_name=? ORDER BY date;", (oshi,))
        data_by_oshi[oshi] = cur.fetchall()

    # 全体の合計
    cur.execute("""
        SELECT SUM(expense) AS total_expense, SUM(income) AS total_income,
               SUM(income) - SUM(expense) AS balance
        FROM kakeibo
    """)
    total = cur.fetchone()

    # 月ごとの合計
    cur.execute("""
        SELECT strftime('%Y-%m', date) AS month,
               SUM(expense) AS total_expense,
               SUM(income) AS total_income,
               SUM(income) - SUM(expense) AS balance
        FROM kakeibo
        GROUP BY month ORDER BY month;
    """)
    monthly = cur.fetchall()
    conn.close()

    return render_template("index.html", data_by_oshi=data_by_oshi, total=total, monthly=monthly)


# --- 新規追加 ---
@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        oshi = request.form["oshi_name"]
        category = request.form["category"]
        expense = int(request.form["expense"] or 0)
        income = int(request.form["income"] or 0)
        memo = request.form["memo"]
        date = request.form["date"]

        conn = get_db()
        conn.execute("""
            INSERT INTO kakeibo (oshi_name, category, expense, income, memo, date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (oshi, category, expense, income, memo, date))
        conn.commit()
        conn.close()
        return redirect("/")
    return render_template("add.html")


# --- 編集・削除ページ（一覧表示） ---
@app.route("/manage")
def manage():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM kakeibo ORDER BY date DESC;")
    records = cur.fetchall()
    conn.close()
    return render_template("manage.html", records=records)


# --- 編集 ---
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    conn = get_db()
    if request.method == "POST":
        oshi = request.form["oshi_name"]
        category = request.form["category"]
        expense = int(request.form["expense"] or 0)
        income = int(request.form["income"] or 0)
        memo = request.form["memo"]
        date = request.form["date"]

        conn.execute("""
            UPDATE kakeibo SET oshi_name=?, category=?, expense=?, income=?, memo=?, date=?
            WHERE id=?
        """, (oshi, category, expense, income, memo, date, id))
        conn.commit()
        conn.close()
        return redirect("/manage")

    cur = conn.execute("SELECT * FROM kakeibo WHERE id=?", (id,))
    data = cur.fetchone()
    conn.close()
    return render_template("edit.html", data=data)


# --- 削除 ---
@app.route("/delete/<int:id>")
def delete(id):
    conn = get_db()
    conn.execute("DELETE FROM kakeibo WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/manage")


if __name__ == "__main__":
    app.run(debug=True)
# ---ホームに戻る---
@app.route("/home")
def home():
    return render_template("home.html")
