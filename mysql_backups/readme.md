# 📦 MySQL Backup Script with Network Drive & Email Notification

This script automates backups of a MySQL database, stores them on a mounted network drive, and sends notifications by email.

## ⚙️ Explanation of the Script

- Configuration via .env
- DB credentials, paths, and email settings are loaded using python-dotenv.
- This keeps secrets out of the code.

### Backup Process

- Creates a local folder (BACKUP_DIR) if it doesn’t exist.
- Runs mysqldump with optional ignored tables.
- Stores the dump file with a timestamp.

### Network Drive Check

- Verifies that the mount point (NETWORK_DRIVE) exists before copying.
- If missing, sends an error email instead of failing silently.
- Backup Storage
- Copies the backup file to the mounted drive.
- Deletes the local temporary file afterward.

### Email Notifications

- Sends emails via SMTP (SSL).
- Supports optional CC recipients with emails_cc parameter.
- Sends a ✅ success message or ❌ failure message with error details.

## 🌐 System Configuration

Mount a Network Share Permanently

Add this line to /etc/fstab:

```bash
<REMOTE_DIR> <MOUNT_POINT> cifs credentials=<CREDENTIALS_DIR>,vers=2.1,rw,iocharset=utf8,file_mode=0777,dir_mode=0777,noperm 0 0
```

```bash
<REMOTE_DIR> → Remote SMB/CIFS share (e.g. //192.168.1.10/backups)
<MOUNT_POINT> → Local directory where the share will be mounted (e.g. /mnt/backup_drive)
<CREDENTIALS_DIR> → File with CIFS credentials
```

```bash
CIFS Credentials File (cifs-creds.example)
username=myuser
password=mypassword
```

## Keep this file secure:

```bash
chmod 600 cifs-creds.example
```

#### 📦 Installation of Dependencies

```bash
Install python-dotenv with your package manager:
sudo apt install python3-dotenv
```

##### Or if you prefer a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
pip install python-dotenv
```

## ⏰ Automating with Cron

To run the backup automatically, use cron:

```bash
#Edit the crontab for the user that will run the script:
crontab -e
#Add an entry. Example: run every night at 2 AM:
0 2 * * * /usr/bin/python3 /path/to/backup_script/backup.py >> /var/log/db_backup.log 2>&1
```

Explanation:

```bash
0 2 * * * → Run at 02:00 every day

/usr/bin/python3 → Full path to Python #(check with which python3)
/path/to/backup_script/backup.py #→ Full path to your backup script
>> /var/log/db_backup.log 2>&1 #→ Append output and errors to a log file

#Verify cron jobs:
crontab -l

#Check logs to confirm execution:
tail -f /var/log/db_backup.log
```

## ✅ Summary

- Script automates MySQL backups and saves them to a mounted network share.
- Notifies success/failure via email (with optional CC support).
- Keeps credentials safe using .env and cifs-creds files.
- Can be scheduled via cron for automatic execution.
