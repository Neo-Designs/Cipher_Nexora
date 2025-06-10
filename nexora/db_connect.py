import pyodbc

server = 'localhost\SQLEXPRESS'
database = 'NovaCoreUniversity'
driver = '{ODBC Driver 18 for SQL Server}'

def get_connection():
    try:
        conn = pyodbc.connect(
            f'DRIVER={driver};SERVER={server};DATABASE={database};Trusted_Connection=yes;Encrypt=no'
        )
        print("✅ Connected to the database!")
        return conn
    except Exception as e:
        print("❌ Connection failed:", e)
        return None
