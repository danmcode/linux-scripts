# -*- coding: utf-8 -*-
import os
import shutil
import smtplib
import subprocess
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuración de la base de datos
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "")
IGNORE_TABLES = os.getenv("IGNORE_TABLES", "").split(",") if os.getenv("IGNORE_TABLES") else []

# Paths
BACKUP_DIR = os.getenv("BACKUP_DIR", "/tmp/db_backups")
NETWORK_DRIVE = os.getenv("NETWORK_DRIVE", "")

# Email
EMAIL_HOST = os.getenv("EMAIL_HOST", "")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "465"))
EMAIL_USER = os.getenv("EMAIL_USER", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
EMAIL_TO = os.getenv("EMAIL_TO", "")


def backup_database():
    """Realiza el backup de la base de datos y devuelve la ruta del archivo generado."""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR, exist_ok=True)

    backup_file = os.path.join(
        BACKUP_DIR,
        "backup_{}_{}.sql".format(DB_NAME, datetime.now().strftime('%Y%m%d_%H%M%S'))
    )

    ignore_tables_cmd = ' '.join(
        "--ignore-table={}.{}".format(DB_NAME, table.strip()) for table in IGNORE_TABLES if table.strip()
    )
    comando = "mysqldump -u {} -p'{}' {} {} > {}".format(
        DB_USER, DB_PASSWORD, DB_NAME, ignore_tables_cmd, backup_file
    )

    result = subprocess.run(
        comando,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )

    if result.returncode != 0:
        raise RuntimeError("mysqldump failed: {}".format(result.stderr))

    return backup_file


def send_email(message, subject=None, emails_cc=None):
    """Envía un correo electrónico con el mensaje proporcionado.
       emails_cc es opcional y debe ser una lista de correos.
    """
    if emails_cc is None:
        emails_cc = []

    recipients = [EMAIL_TO] + emails_cc

    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = EMAIL_TO
    if emails_cc:
        msg['Cc'] = ", ".join(emails_cc)
    msg['Subject'] = subject or "BACKUP DB {}".format(DB_NAME)
    msg.attach(MIMEText(message, 'plain'))

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT, context=context) as server:
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_USER, recipients, msg.as_string())

    print("Message sent!")


def main():
    try:
        # Verify network drive
        if not os.path.exists(NETWORK_DRIVE):
            message = "ERROR: La unidad de red {} no está montada o no existe.".format(NETWORK_DRIVE)
            send_email(message, subject="ERROR BACKUP DB {}".format(DB_NAME))
            return

        # Perform backup
        backup_file = backup_database()

        # Copy to network drive
        shutil.copy(backup_file, NETWORK_DRIVE)

        # Delete local backup
        os.remove(backup_file)

        # Notify success
        fecha_realizacion = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message = "✅ Se ha realizado una copia de seguridad de la base de datos {} en {}.".format(DB_NAME, fecha_realizacion)
        send_email(message)

    except Exception as e:
        fecha_realizacion = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message = "❌ No se pudo realizar la copia de seguridad de {} en {}:\n{}".format(DB_NAME, fecha_realizacion, e)
        send_email(message, subject="ERROR BACKUP DB {}".format(DB_NAME))


if __name__ == "__main__":
    main()
