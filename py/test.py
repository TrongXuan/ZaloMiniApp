import sqlite3

def get_house_db():
    try:
        # Kết nối cơ sở dữ liệu
        conn = sqlite3.connect(r'C:\Users\xuant\OneDrive\Máy tính\LuanVan\House_Price.db')
        cursor = conn.cursor()
        cursor.execute('SELECT name FROM sqlite_master WHERE type="table";')
        tables = cursor.fetchall()
        print(f"Tables in DATABASE_HOUSE: {tables}")  # In ra danh sách bảng trong cơ sở dữ liệu
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

# Gọi hàm kiểm tra
get_house_db()
