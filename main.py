import argparse
import csv
import json
import re
import smtplib
import ssl
import sys
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def get_args():
    """Parses command line arguments."""
    parser = argparse.ArgumentParser(
        description="Python Mail Merge Tool: Bulk send HTML emails using a CSV file and an HTML template.",
        epilog="""Examples:
  # 1. Generate preview files (Recommended first step)
  python main.py jobs/math_exam --preview

  # 2. Send emails for real
  python main.py jobs/math_exam""",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("folder", type=Path, help="Path to the job folder containing config.json, data.csv, etc.")
    parser.add_argument("--preview", action="store_true", help="Dry run: Generate HTML files in a 'previews' folder instead of sending emails")
    return parser.parse_args()

def load_config(base_dir, default_path="default-config.json"):
    """Loads default config and merges with local config.json."""
    # Load Global
    try:
        with open(default_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except FileNotFoundError:
        sys.exit(f"Error: Could not find '{default_path}'.")

    # Load Local and Merge
    custom_path = base_dir / "config.json"
    if custom_path.exists():
        with open(custom_path, "r", encoding="utf-8") as f:
            custom_config = json.load(f)
            if "constants" in custom_config:
                config.setdefault("constants", {}).update(custom_config.pop("constants"))
            config.update(custom_config)
    return config

def setup_smtp(cfg):
    """Initializes and returns the authenticated SMTP server connection."""
    context = ssl.create_default_context()
    print(f"Connecting to {cfg['smtp_server']}...")
    try:
        server = smtplib.SMTP_SSL(cfg["smtp_server"], cfg["smtp_port"], context=context)
        server.login(cfg["sender_email"], cfg["password"])
        print("Login successful.")
        return server
    except Exception as e:
        sys.exit(f"Connection failed: {e}")

def strip_html(html_content):
    """Converts HTML to plain text for the email fallback."""
    text = re.sub(r'(<br\s*/?>|</p>|</div>)', '\n', html_content, flags=re.IGNORECASE)
    return re.sub(r'<[^>]+>', '', text).strip()

def interpolate(template, subject_template, data):
    """Replaces placeholders <<key>> with values from data dictionary."""
    body = template
    subject = subject_template
    for key, value in data.items():
        placeholder = f"<<{key}>>"
        val_str = str(value)
        body = body.replace(placeholder, val_str)
        subject = subject.replace(placeholder, val_str)
    return subject, body

def save_preview(folder, index, recipient, subject, body):
    """Saves the generated email as an HTML file."""
    # Create distinct filename
    filename = f"{index}_{recipient}.html"
    
    preview_dir = folder / "previews"
    preview_dir.mkdir(exist_ok=True)
    
    with open(preview_dir / filename, "w", encoding="utf-8") as f:
        f.write(f"<!-- Subject: {subject} -->\n" + body)
    print(f"📄 Preview saved: {filename}")

def send_email(server, cfg, recipient, subject, body):
    """Constructs MIME message and sends it via SMTP."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = cfg["sender_email"]
    msg["To"] = recipient

    # Handle CC
    cc_list = cfg.get("cc", [])
    if cc_list:
        msg["Cc"] = ", ".join(cc_list)

    # Attach Parts
    msg.attach(MIMEText(strip_html(body), "plain"))
    msg.attach(MIMEText(body, "html"))

    # Send (Recipients = To + Cc + Bcc)
    all_recipients = [recipient] + cc_list + cfg.get("bcc", [])
    
    try:
        server.sendmail(cfg["sender_email"], all_recipients, msg.as_string())
        print(f"✅ Sent to: {recipient}")
    except Exception as e:
        print(f"❌ Failed to send to {recipient}: {e}")

def main():
    args = get_args()

    if not args.folder.is_dir():
        sys.exit(f"Error: Folder '{args.folder}' does not exist.")

    # 1. Load Resources
    cfg = load_config(args.folder)
    csv_path = args.folder / cfg["csv_file"]
    
    try:
        with open(args.folder / cfg["template_file"], "r", encoding="utf-8") as f:
            raw_template = f.read()
    except FileNotFoundError:
        sys.exit(f"Error: Template file not found in {args.folder}")

    # 2. Setup Server (if not preview)
    server = None
    if not args.preview:
        server = setup_smtp(cfg)
    else:
        print(f"🔵 PREVIEW MODE: Outputs will be saved to '{args.folder}/previews/'")

    # 3. Process Batch
    try:
        with open(csv_path, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            
            for i, row in enumerate(reader, 1):
                recipient = row.get(cfg["email_column"])
                if not recipient:
                    print(f"⚠️  Skipped row {i}: Missing email column '{cfg['email_column']}'")
                    continue

                # Prepare Data
                data = {**cfg.get("constants", {}), **row}
                subject, body = interpolate(raw_template, cfg["email_subject"], data)

                # Action
                if args.preview:
                    save_preview(args.folder, i, recipient, subject, body)
                else:
                    send_email(server, cfg, recipient, subject, body)

    except FileNotFoundError:
        sys.exit(f"Error: CSV file '{cfg['csv_file']}' not found in {args.folder}")
    finally:
        if server:
            server.quit()
            print("\nAll tasks completed.")

if __name__ == "__main__":
    main()