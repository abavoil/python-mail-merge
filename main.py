import csv
import json
import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def load_config(default_path="default-config.json", custom_path="config.json"):
    with open(default_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    
    if os.path.exists(custom_path):
        with open(custom_path, "r", encoding="utf-8") as f:
            custom_config = json.load(f)
            # Deep update for constants if they exist in custom_config
            if "constants" in custom_config:
                config["constants"].update(custom_config.pop("constants"))
            config.update(custom_config)
            
    return config

def main():
    # 1. Load Configuration and Template
    cfg = load_config()
    
    with open(cfg["template_file"], "r", encoding="utf-8") as f:
        raw_template = f.read()

    # 2. Setup Email Server
    context = ssl.create_default_context()
    
    print(f"Connecting to {cfg['smtp_server']}...")
    server = smtplib.SMTP_SSL(cfg["smtp_server"], cfg["smtp_port"], context=context)
    server.login(cfg["sender_email"], cfg["password"])
    print("Login successful.")

    # 3. Process CSV
    with open(cfg["csv_file"], mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            recipient_email = row[cfg["email_column"]]
            
            # Merge CSV data and Constant fields for interpolation
            # This creates a combined dictionary for replacement
            data_to_inject = {**cfg["constants"], **row}
            
            # Interpolation: Body
            html_body = raw_template
            for key, value in data_to_inject.items():
                html_body = html_body.replace(f"<<{key}>>", str(value))
            
            # Interpolation: Subject
            subject = cfg["email_subject"]
            for key, value in data_to_inject.items():
                subject = subject.replace(f"<<{key}>>", str(value))
                
            # Construct Email
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = cfg["sender_email"]
            msg["To"] = recipient_email
            
            msg.attach(MIMEText(html_body, "html"))
            
            # Send
            server.sendmail(cfg["sender_email"], recipient_email, msg.as_string())
            print(f"✅ Sent to: {recipient_email}")
            break

    server.quit()
    print("All tasks completed.")

if __name__ == "__main__":
    main()