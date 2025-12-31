# EmailService.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from googlesheet import update_email_sent

# -----------------------------
# Email Configuration
# -----------------------------
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

EMAIL_ADDRESS = "kkmjpaibot@gmail.com"     # Sender email
EMAIL_PASSWORD = "xtcz rcwz jixf ugnp"      # Gmail App Password

AGENT_WHATSAPP = "https://wa.me/60168357258"

# -----------------------------
# Send Campaign 3 Email
# -----------------------------
def send_campaign3_email(session):
    """
    Sends retirement planning summary email.
    Updates Email_sent timestamp ONLY after successful send.
    """

    recipient = session.get("email", "").strip()
    name = session.get("name", "").strip()

    if not recipient:
        print("❌ No email found in session. Email not sent.")
        return False

    # -----------------------------
    # Build Email
    # -----------------------------
    msg = MIMEMultipart()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = recipient
    msg["Subject"] = "Your Retirement Planning Summary"

    body = f"""
Hi {name},

Thank you for using our retirement planning tool.
Here is a summary of your details:

Name              : {session.get('name')}
Date of Birth     : {session.get('dob')}
Age               : {session.get('age')}
Retirement Age    : {session.get('retirement_age')}
Monthly Need      : RM {session.get('monthly')}
EPF Savings       : RM {session.get('epf')}
Monthly Saving    : RM {session.get('contribution')}
Phone             : {session.get('phone')}
Email             : {session.get('email')}

If you would like to speak to an agent, click below:
{AGENT_WHATSAPP}

Thank you & have a great day.
"""

    msg.attach(MIMEText(body, "plain"))

    # -----------------------------
    # Send Email
    # -----------------------------
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)

        print(f"✅ Email successfully sent to {recipient}")

        # -----------------------------
        # Update Google Sheet
        # -----------------------------
        update_email_sent(recipient)
        print(f"✅ Email_sent timestamp updated for {recipient}")

        return True

    except Exception as e:
        print("❌ Email sending failed")
        print(e)
        return False
