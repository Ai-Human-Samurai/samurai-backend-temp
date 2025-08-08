📄 manual_check.py — Manual Reminder Diagnostics
This script is used to manually inspect active reminders in the database.

✅ What it does:
Connects to the local database via SQLAlchemy session.

Fetches all active reminders using get_active_reminders().

Prints:

Reminder text

Scheduled time

User ID

📦 Usage:
bash
Копировать
Редактировать
python scripts/manual_check.py
🛠️ Output Example:
sql
Копировать
Редактировать
📋 Found 2 active reminders:

→ [User 42] "Take your meds" at 2025-07-25 07:30:00  
→ [User 17] "Call your mentor" at 2025-07-25 09:00:00
💡 Notes:
This is a debug utility for developers.

You can extend it with filters (--user, --pending-only, etc) if needed.

Make sure the DB is initialized and populated before use.

