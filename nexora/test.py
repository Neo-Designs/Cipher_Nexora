from db_connect import get_connection

conn = get_connection()
if conn:
    print("🎉 You’re connected, baby!")
else:
    print("💥 Still broken.")
