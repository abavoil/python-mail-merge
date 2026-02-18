# Python Mail Merge

A lightweight mail merge tool using Python, SMTP for batch filling HTML template from CSV data and sending it by mail.

## ✨ Features

*   **📂 Job-Based Organization**: Keep different campaigns (exams, newsletters, announcements) in separate folders under `jobs/`.
*   **Safe Preview Mode**: Generate HTML files locally to check layouts and placeholders before sending a single email.
*   **Anti-Spam Compliance**: Automatically generates a `text/plain` version alongside the HTML to improve deliverability.
*   **Advanced Config**: Supports global settings with local overrides, including **CC** and **BCC** support.
*   **Secure**: Designed to work with App Passwords (Gmail) and standard SMTP servers.

---

## 📂 Project Structure

```text
python-mail-merge/
├── main.py                  # The execution script
├── default-config.json      # Global SMTP & default settings
├── jobs/                    # Folder containing your mailing campaigns
│   ├── math_exam/           # Example Job
│   │   ├── config.json      # Local overrides (subject, specific links)
│   │   ├── data.csv         # Recipient list and variables
│   │   └── template.html    # HTML Email design
│   └── newsletter_nov/
│       └── ...
└── README.md
```

---

## ⚙️ Configuration

### 1. Global Configuration (`default-config.json`)
Located at the root. Set your SMTP credentials and defaults here.

```json
{
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 465,
    "sender_email": "your.name@gmail.com",
    "password": "your-app-password-here",
    "csv_file": "data.csv",
    "template_file": "template.html",
    "email_column": "email",
    "email_subject": "Update for <<Firstname>>",
    "cc": [],
    "bcc": [],
    "constants": {}
}
```

### 2. Job Configuration (`jobs/math_exam/config.json`)
Located inside a job folder. Any value here overrides the global default.

```json
{
    "email_subject": "Math Results - <<Prenom>> <<Nom>>",
    "cc": ["admin@school.com"],
    "constants": {
        "school_name": "University of Science",
        "link_correction": "https://1drv.ms/u/..."
    }
}
```

---

## 🚀 Usage

The script is run via the command line. You must specify the folder of the job you want to process.

### 1. Dry Run / Preview (Recommended)
Before sending, generate the emails locally to verify variables and layout.

```bash
python main.py jobs/math_exam --preview
```
*   **Output:** Creates a `previews/` folder inside `jobs/math_exam/`.
*   **Action:** Open the generated HTML files in your browser to inspect them.

### 2. Send Emails
Once you are satisfied with the preview, remove the flag to send them for real.

```bash
python main.py jobs/math_exam
```

---

## 🛠️ Setup & Best Practices

### 1. Gmail Security & App Passwords
If using Gmail, your standard login password **will not work**.
1. Go to your Google Account > **Security**.
2. Enable **2-Step Verification**.
3. Go to **2-Step Verification** > **App Passwords**.
4. Create a new app (name it "MailMerge") and use the generated 16-character code as the `"password"` in your JSON.

### 2. Placeholder Syntax
In your **HTML Template** and **Email Subject**, use `<<ColumnName>>`.
*   The script looks for `ColumnName` in your **CSV**.
*   If not found, it looks in the `"constants"` dictionary in your **JSON**.

### 3. CSV Encoding
Always save your CSV files in **UTF-8** encoding. This ensures that names with accents (é, è, ç) or special characters are displayed correctly.

### 4. Rate Limits
Be aware of your email provider's daily limits (e.g., Gmail Personal is ~500 emails/day). Exceeding this may temporarily block your account.

---

## ⚖️ License
This project is released under the **MIT License**. Feel free to use and modify it for your personal or professional needs.