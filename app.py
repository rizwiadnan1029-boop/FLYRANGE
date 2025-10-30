from flask import Flask, render_template, jsonify, request, redirect, url_for, session, send_from_directory
import pandas as pd

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Needed for session security

# Your password
PASSWORD = "104270"

# 🔗 Use your published Google Sheet CSV link
EXCEL_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTPIR5j2TyzJAorJsGX9reIhOXQKrTfyDbbv2GreXPDf2nWcBCddhoedW93yEaK1S93imugCke-dRD_/pub?output=csv"

def load_data():
    df = pd.read_csv(EXCEL_URL)
    df.columns = df.columns.str.strip().str.upper()
    df.fillna("NO DATA", inplace=True)
    return df

# 🔐 Login page
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        entered = request.form.get('password')
        if entered == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('home'))
        else:
            return render_template("login.html", error="Wrong password! Try again.")
    return render_template("login.html")

# 🏠 Main page (protected)
@app.route('/home')
def home():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template("index.html")

@app.route('/month/<month>')
def get_month_data(month):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    try:
        df = load_data()
        mask = df['MONTH'].astype(str).str.strip().str.upper() == month.strip().upper()
        month_rows = df[mask]

        if month_rows.empty:
            return jsonify({"error": f"No data found for {month}"})

        row = month_rows.iloc[0].to_dict()
        days_in_month = int(row.get("NO. OF DAYS IN MONTH", 0))
        days_coming = int(row.get("NO. OF DAYS COMING", 0))
        days_absent = row.get("NO. OF DAYS ABSENT", "NO DATA")

        total_bill = days_coming * 50  # ₹50/day

        result = {
            "Month": row.get("MONTH", month),
            "Paid": row.get("PAID", "NO DATA"),
            "Days in Month": days_in_month,
            "Days Coming": days_coming,
            "Days Absent": days_absent,
            "Amount": f"{total_bill:.2f}",
            "Payment Mode": row.get("PAYMENT MODE", "NO DATA")
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": f"Error loading data: {e}"})

@app.route('/annual')
def get_annual_spend():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    try:
        df = load_data()
        df["NO. OF DAYS COMING"] = pd.to_numeric(df["NO. OF DAYS COMING"], errors='coerce').fillna(0)
        total_annual_spend = (df["NO. OF DAYS COMING"] * 50).sum()

        return jsonify({"Total Annual Expenditure": f"{total_annual_spend:.2f}"})
    except Exception as e:
        return jsonify({"error": f"Error calculating annual spend: {e}"})


# 🚪 Logout option
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ✅ Google Search Console Verification Route
@app.route('/googleb5880ca1d0c7a902.html')
def google_verify():
    return send_from_directory('.', 'googleb5880ca1d0c7a902.html')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
