# googlesheet.py
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# -----------------------------
# Google Sheets Setup
# -----------------------------
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

CREDS = Credentials.from_service_account_file(
    "ServiceAccount.json",
    scopes=SCOPE
)

client = gspread.authorize(CREDS)

SPREADSHEET_NAME = "ChatBotData"
WORKSHEET_NAME = "Campaign3"

HEADERS = [
    "Name",
    "Birth of Date",
    "Age",
    "Retirement Age",
    "Monthly Needed",
    "EPF/Savings",
    "Monthly Contribution",
    "Phone",
    "Email",
    "Timestamp",
    "Email_sent",
    "Whatsapp"
]

# -----------------------------
# Initialize Sheet
# -----------------------------
def init_sheet():
    """Ensure spreadsheet, worksheet, and headers exist."""
    try:
        sh = client.open(SPREADSHEET_NAME)
    except gspread.SpreadsheetNotFound:
        sh = client.create(SPREADSHEET_NAME)

    try:
        sheet = sh.worksheet(WORKSHEET_NAME)
    except gspread.WorksheetNotFound:
        sheet = sh.add_worksheet(
            title=WORKSHEET_NAME,
            rows=1000,
            cols=len(HEADERS)
        )

    all_values = sheet.get_all_values()
    if not all_values:
        sheet.append_row(HEADERS)

    return sheet

# -----------------------------
# Generate WhatsApp Link
# -----------------------------
def generate_whatsapp_link(phone):
    if not phone:
        return ""
    phone_clean = ''.join(filter(str.isdigit, str(phone)))
    return f"https://wa.me/{phone_clean}"

# -----------------------------
# Append new session
# -----------------------------
def save_session_after_email(session_data, email_sent=False):
    """Append a new row with optional Email_sent timestamp."""
    sheet = init_sheet()

    row_update_ts = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    email_ts = datetime.now().strftime("%d/%m/%Y %H:%M:%S") if email_sent else ""
    wa_link = generate_whatsapp_link(session_data.get("phone", ""))

    row = [
        session_data.get("name", ""),
        session_data.get("dob", ""),
        session_data.get("age", ""),
        session_data.get("retirement_age", ""),
        session_data.get("monthly", ""),
        session_data.get("epf", ""),
        session_data.get("contribution", ""),
        session_data.get("phone", ""),
        session_data.get("email", ""),
        row_update_ts,   # Timestamp
        email_ts,        # Email_sent
        wa_link          # Whatsapp
    ]

    all_values = sheet.get_all_values()
    next_row = len(all_values) + 1
    sheet.insert_row(row, next_row)
    print(f"Row added for {session_data.get('name', '')} at row {next_row}")

    return session_data.get("email")  # for optional update

# -----------------------------
# Update Email_sent timestamp
# -----------------------------
def update_email_sent(email):
    """Update Email_sent timestamp for a specific email (column 9)."""
    sheet = init_sheet()
    all_values = sheet.get_all_values()

    for idx, row in enumerate(all_values, start=1):
        # Check only the Email column (column 9, index 8)
        if len(row) >= 9 and row[8].strip() == email.strip():
            email_ts = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            sheet.update_cell(idx, 11, email_ts)  # Column 11 = Email_sent
            print(f"Email_sent timestamp updated at row {idx}")
            return

    print("No matching email found to update Email_sent.")
