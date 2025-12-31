from flask import Flask, render_template, request, jsonify, session
import datetime, re
from googlesheet import save_session_after_email
from Emailservice import send_campaign3_email   # import email function

app = Flask(__name__)
app.secret_key = "legacy_secret_key"

# -----------------------
# Main page
# -----------------------
@app.route("/")
def chatbot():
    session.clear()
    return render_template("Chatbot.html")

# -----------------------
# Name
# -----------------------
@app.route("/submit_name", methods=["POST"])
def submit_name():
    name = request.json.get("name", "").strip()
    if not name:
        return jsonify(error="Please enter your name.")
    session["name"] = name
    return jsonify(message=f"Hi {name}, let’s get to know you better.", next="dob")

# -----------------------
# DOB
# -----------------------
@app.route("/submit_dob", methods=["POST"])
def submit_dob():
    dob = request.json.get("dob", "").strip()
    try:
        birth_date = datetime.datetime.strptime(dob, "%d/%m/%Y")
        age = datetime.date.today().year - birth_date.year
        if age < 18:
            return jsonify(error="You must be at least 18 years old.")
    except:
        return jsonify(error="Invalid format of Date of Birth. Please use DD/MM/YYYY.")
    
    session["dob"] = dob
    session["age"] = age
    return jsonify(message=f"{age} is an excellent age to start planning for retirement.", next="retirement")

# -----------------------
# Retirement Age
# -----------------------
@app.route("/submit_retirement", methods=["POST"])
def submit_retirement():
    try:
        retirement_age = int(request.json.get("retirement_age"))
        if retirement_age < 18 or retirement_age > 100:
            raise ValueError
    except:
        return jsonify(error="Invalid retirement age.")
    session["retirement_age"] = retirement_age
    years_left = retirement_age - session["age"]
    return jsonify(message=f"You plan to retire at {retirement_age}. That is about {years_left} years away.", next="monthly")

# -----------------------
# Monthly Need
# -----------------------
@app.route("/submit_monthly", methods=["POST"])
def submit_monthly():
    try:
        monthly = float(request.json.get("monthly"))
        if monthly <= 0:
            raise ValueError
    except:
        return jsonify(error="Invalid monthly amount.")
    session["monthly"] = monthly
    total = monthly * 12 * 20
    return jsonify(
        message=(
            f"Got it. Estimated monthly need during your retirement is RM {monthly:,.2f}.\n"
            f"Based on estimation of 20 years during your retirement, "
            f"you will need approximately RM {total:,.2f}."
        ),
        next="epf"
    )

# -----------------------
# EPF / Savings
# -----------------------
@app.route("/submit_epf", methods=["POST"])
def submit_epf():
    try:
        epf = float(request.json.get("epf"))
        if epf < 0:
            raise ValueError
    except:
        return jsonify(error="Invalid EPF amount.")

    session["epf"] = epf
    age = session["age"]
    years = max(0, 60 - age)

    if epf > 0:
        projected = epf * (1.055 ** years)
        msg = f"That's great! The projected amount in your EPF savings at age 60 is RM {projected:,.2f}."
    else:
        msg = "It’s alright. It’s never too late to start saving."

    return jsonify(message=msg, next="contribution")

# -----------------------
# Contribution
# -----------------------
@app.route("/submit_contribution", methods=["POST"])
def submit_contribution():
    try:
        amount = float(request.json.get("amount"))
        if amount < 0:
            raise ValueError
    except:
        return jsonify(error="Invalid contribution amount.")

    session["contribution"] = amount
    age = session["age"]
    retirement_age = session["retirement_age"]
    n = retirement_age - age
    r = 0.07  # annual return
    annual = amount * 12
    fv = annual * ((1 + r) ** n - 1) / r  # future value of contributions

    epf = session.get("epf", 0)
    years_epf = max(0, 60 - age)
    epf_growth = epf * (1.055 ** years_epf)

    total_savings = fv + epf_growth

    messages = [
        f"By saving RM {amount:.2f} per month, your estimated savings at age {retirement_age} is RM {fv:,.2f}.",
        f"Great news. By opting to start saving for your retirement now, your estimated total retirement savings at age 60 (including EPF) is RM {total_savings:,.2f}."
    ]

    return jsonify(messages=messages, next="phone")

# -----------------------
# Phone
# -----------------------
@app.route("/submit_phone", methods=["POST"])
def submit_phone():
    phone = request.json.get("phone", "").replace(" ", "").replace("-", "")
    pattern = re.compile(r'^(\+60|60)[0-9]{9}$|^01[0-9]{8}$')
    if not pattern.match(phone):
        return jsonify(error="Invalid Malaysian phone number.")
    session["phone"] = phone
    return jsonify(message="Phone number saved.", next="email")

# -----------------------
# Email (save session and send email)
# -----------------------
@app.route("/submit_email", methods=["POST"])
def submit_email():
    email = request.json.get("email", "")
    pattern = re.compile(r'^[^@]+@[^@]+\.[^@]+$')
    if not pattern.match(email):
        return jsonify(error="Invalid email address.")
    
    session["email"] = email

    # Save session to Google Sheets
    save_session_after_email(session)

    # Send summary email
    send_campaign3_email(session)
    
    return jsonify(
        message="Are you interested to learn more about planning for your retirement?",
        next="signup"
    )

# -----------------------
# Signup
# -----------------------
@app.route("/submit_signup", methods=["POST"])
def submit_signup():
    choice = request.json.get("choice", "").lower()
    session["signup"] = choice
    
    messages = [
        "Great! Thank you so much for your interest. We will contact you soon. Subject to terms and conditions of approved policy after recommendation by authorised.",
        'Thank you for contacting us. Feel free to reach out to us if you would like more information <a href="https://wa.me/60168357258" target="_blank">Clik to Contact Agent</a>'
    ]
    
    return jsonify(messages=messages, next="end")

# -----------------------
# Run Flask
# -----------------------
if __name__ == "__main__":
    app.run(debug=True)
