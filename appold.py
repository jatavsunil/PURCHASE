from flask import Flask, render_template, request, redirect, url_for, session, jsonify, Response, send_file
import mysql.connector
import pandas as pd
from io import StringIO, BytesIO

app = Flask(__name__)
app.secret_key = "your_secret_key"

# ----------------- DB CONNECTION -----------------
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "Pass@123",
    "database": "material_property"
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

# ----------------- LOGIN -----------------
@app.route("/", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Boss credentials
        if username == "12001504" and password == "2001":
            session["user"] = "12001504"
            return redirect(url_for("dashboard"))

        # Normal employee login
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM employee WHERE Username=%s AND Password=%s", (username, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            session["user"] = username
            return redirect(url_for("form_page"))
        else:
            error = "Invalid credentials"

    return render_template("login.html", error=error)

# ----------------- FORM PAGE -----------------
@app.route("/form", methods=["GET", "POST"])
def form_page():
    if "user" not in session or session["user"] == "12001504":
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT material_code FROM Material")
    materials = [row["material_code"] for row in cursor.fetchall()]
    cursor.close()
    conn.close()

    if request.method == "POST":
        data = {
            "material_code": request.form.get("material_code"),
            "material_description": request.form.get("material_description", ""),
            "vendor_code": request.form.get("vendor_code"),
            "vendor_name": request.form.get("vendor_name", ""),
            "po_number": request.form.get("po_number"),
            "Quantity": request.form.get("Quantity"),
            "po_date": request.form.get("po_date"),
            "delivery_date": request.form.get("delivery_date"),
            "delivery_status": request.form.get("delivery_status"),
            "lead_time": request.form.get("lead_time"),
            "review_date": request.form.get("review_date")
        }

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Material_Submissions
            (material_code, material_description, vendor_code, vendor_name, po_number, Quantity,
             po_date, delivery_date, delivery_status, lead_time, review_date)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            data["material_code"], data["material_description"], data["vendor_code"], data["vendor_name"],
            data["po_number"], data["Quantity"], data["po_date"], data["delivery_date"],
            data["delivery_status"], data["lead_time"], data["review_date"]
        ))
        conn.commit()
        cursor.close()
        conn.close()

        return render_template("success.html", data=data)

    return render_template("form.html", materials=materials)

# ----------------- AUTOSUGGEST APIS -----------------
@app.route("/search_materials")
def search_materials():
    term = request.args.get("q", "").strip()
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT material_code, material_description, Uom, Plant
        FROM Material
        WHERE material_description LIKE %s
        ORDER BY material_description
        LIMIT 10
    """, (f"%{term}%",))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(results)

@app.route("/search_vendors/<material_code>")
def search_vendors(material_code):
    term = request.args.get("q", "").strip()
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT vendor_code, vendor_name
        FROM Vendor
        WHERE material_code=%s AND vendor_name LIKE %s
        ORDER BY vendor_name
        LIMIT 10
    """, (material_code, f"%{term}%"))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(results)

@app.route("/get_material_details/<material_code>")
def get_material_details(material_code):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Material WHERE material_code=%s", (material_code,))
    material = cursor.fetchone()
    cursor.close()
    conn.close()
    return jsonify(material or {})

@app.route("/get_vendor_codes/<material_code>")
def get_vendor_codes(material_code):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT vendor_code FROM Vendor WHERE material_code=%s", (material_code,))
    codes = [row["vendor_code"] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return jsonify(codes)

@app.route("/get_vendor_name/<material_code>/<vendor_code>")
def get_vendor_name(material_code, vendor_code):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT vendor_name FROM Vendor WHERE material_code=%s AND vendor_code=%s",
                   (material_code, vendor_code))
    vendor = cursor.fetchone()
    cursor.close()
    conn.close()
    return jsonify(vendor or {})

# ----------------- DASHBOARD -----------------
'''@app.route("/dashboard", methods=["GET"])
def dashboard():
    if "user" not in session or session["user"] != "12001504":
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch distinct filters
    cursor.execute("SELECT DISTINCT vendor_name FROM Material_Submissions WHERE vendor_name IS NOT NULL")
    all_vendors = [row["vendor_name"] for row in cursor.fetchall()]

    cursor.execute("SELECT DISTINCT delivery_date FROM Material_Submissions WHERE delivery_date IS NOT NULL ORDER BY delivery_date")
    all_delivery_dates = [row["delivery_date"].strftime("%Y-%m-%d") for row in cursor.fetchall()]

    # Filters
    delivery_status = request.args.get("delivery_status", "")
    vendors = request.args.getlist("vendors")
    review_start = request.args.get("review_start")
    review_end = request.args.get("review_end")
    delivery_start = request.args.get("delivery_start")
    delivery_end = request.args.get("delivery_end")

    # Build base query
    query = """
        SELECT material_code, material_description, delivery_date, SUM(Quantity) AS total_qty
        FROM Material_Submissions
        WHERE 1=1
    """
    params = []

    if delivery_status:
        query += " AND delivery_status=%s"
        params.append(delivery_status)

    if vendors:
        placeholders = ",".join(["%s"] * len(vendors))
        query += f" AND vendor_name IN ({placeholders})"
        params.extend(vendors)

    if review_start and review_end:
        query += " AND review_date BETWEEN %s AND %s"
        params.extend([review_start, review_end])

    if delivery_start and delivery_end:
        query += " AND delivery_date BETWEEN %s AND %s"
        params.extend([delivery_start, delivery_end])

    query += " GROUP BY material_code, material_description, delivery_date ORDER BY material_code, delivery_date"
    cursor.execute(query, params)
    rows = cursor.fetchall()

    # Build pivot table data
    pivot_map = {}
    for r in rows:
        code = r["material_code"]
        desc = r["material_description"]
        date = r["delivery_date"].strftime("%Y-%m-%d")
        qty = int(r["total_qty"] or 0)

        if (code, desc) not in pivot_map:
            pivot_map[(code, desc)] = {
                "material_code": code,
                "material_description": desc,
                "dates": {d: 0 for d in all_delivery_dates},
                "grand_total": 0
            }
        pivot_map[(code, desc)]["dates"][date] = qty
        pivot_map[(code, desc)]["grand_total"] += qty

    pivot_data = list(pivot_map.values())

    # Compute column totals
    column_totals = {d: 0 for d in all_delivery_dates}
    grand_total_all = 0
    for item in pivot_data:
        for d, qty in item["dates"].items():
            column_totals[d] += qty
        grand_total_all += item["grand_total"]

    cursor.close()
    conn.close()

    return render_template(
        "dashboard.html",
        filters={
            "delivery_status": delivery_status,
            "vendors": vendors,
            "review_start": review_start,
            "review_end": review_end,
            "delivery_start": delivery_start,
            "delivery_end": delivery_end
        },
        all_vendors=all_vendors,
        all_delivery_dates=all_delivery_dates,
        pivot_data=pivot_data,
        column_totals=column_totals,
        grand_total_all=grand_total_all
    )

'''
@app.route("/dashboard", methods=["GET"])
def dashboard():
    if "user" not in session or session["user"] != "12001504":
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # --- Fetch distinct filters ---
    cursor.execute("SELECT DISTINCT vendor_name FROM Material_Submissions WHERE vendor_name IS NOT NULL")
    all_vendors = [row["vendor_name"] for row in cursor.fetchall()]

    cursor.execute("""
        SELECT DISTINCT review_date FROM Material_Submissions 
        WHERE review_date IS NOT NULL 
        ORDER BY review_date
    """)
    all_review_dates = [row["review_date"].strftime("%Y-%m-%d") for row in cursor.fetchall()]

    cursor.execute("""
        SELECT DISTINCT delivery_date FROM Material_Submissions 
        WHERE delivery_date IS NOT NULL 
        ORDER BY delivery_date
    """)
    all_delivery_dates = [row["delivery_date"].strftime("%Y-%m-%d") for row in cursor.fetchall()]

    # --- Read filters ---
    delivery_status = request.args.get("delivery_status", "")
    vendors = request.args.getlist("vendors")
    review_start = request.args.get("review_start")
    review_end = request.args.get("review_end")
    delivery_start = request.args.get("delivery_start")
    delivery_end = request.args.get("delivery_end")

    # --- Build filtered query ---
    query = """
        SELECT material_code, material_description, delivery_date, SUM(Quantity) AS total_qty
        FROM Material_Submissions
        WHERE 1=1
    """
    params = []

    if delivery_status:
        query += " AND delivery_status=%s"
        params.append(delivery_status)

    if vendors:
        placeholders = ",".join(["%s"] * len(vendors))
        query += f" AND vendor_name IN ({placeholders})"
        params.extend(vendors)

    if review_start and review_end:
        query += " AND review_date BETWEEN %s AND %s"
        params.extend([review_start, review_end])

    if delivery_start and delivery_end:
        query += " AND delivery_date BETWEEN %s AND %s"
        params.extend([delivery_start, delivery_end])

    query += " GROUP BY material_code, material_description, delivery_date ORDER BY material_code, delivery_date"
    cursor.execute(query, params)
    rows = cursor.fetchall()

    # --- Build Pivot Table Data ---
    pivot_map = {}
    for r in rows:
        code = r["material_code"]
        desc = r["material_description"]
        date = r["delivery_date"].strftime("%Y-%m-%d")
        qty = int(r["total_qty"] or 0)

        if (code, desc) not in pivot_map:
            pivot_map[(code, desc)] = {
                "material_code": code,
                "material_description": desc,
                "dates": {d: 0 for d in all_delivery_dates},
                "grand_total": 0
            }
        pivot_map[(code, desc)]["dates"][date] = qty
        pivot_map[(code, desc)]["grand_total"] += qty

    pivot_data = list(pivot_map.values())

    # --- Column Totals ---
    column_totals = {d: 0 for d in all_delivery_dates}
    grand_total_all = 0
    for item in pivot_data:
        for d, qty in item["dates"].items():
            column_totals[d] += qty
        grand_total_all += item["grand_total"]

    cursor.close()
    conn.close()

    return render_template(
        "dashboard.html",
        filters={
            "delivery_status": delivery_status,
            "vendors": vendors,
            "review_start": review_start,
            "review_end": review_end,
            "delivery_start": delivery_start,
            "delivery_end": delivery_end
        },
        all_vendors=all_vendors,
        all_review_dates=all_review_dates,  # ✅ added this line
        all_delivery_dates=all_delivery_dates,
        pivot_data=pivot_data,
        column_totals=column_totals,
        grand_total_all=grand_total_all
    )

# ----------------- EXPORT ROUTES -----------------
@app.route("/download_csv")
def download_csv():
    conn = get_db_connection()
    df = pd.read_sql("SELECT * FROM Material_Submissions", conn)
    conn.close()
    si = StringIO()
    df.to_csv(si, index=False)
    return Response(si.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment;filename=dashboard_data.csv"})

@app.route("/download_excel")
def download_excel():
    conn = get_db_connection()
    df = pd.read_sql("SELECT * FROM Material_Submissions", conn)
    conn.close()
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Dashboard")
    output.seek(0)
    return send_file(output, as_attachment=True,
                     download_name="dashboard_data.xlsx",
                     mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# ----------------- LOGOUT -----------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

# ----------------- RUN -----------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
