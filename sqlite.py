import sqlite3
import pandas as pd

# Đường dẫn tới file CSV và SQLite DB
csv_file_path = r'C:\Users\xuant\OneDrive\Máy tính\LuanVanTotNghiep\dbHouse_Price.csv'
sqlite_db_path = r'C:\Users\xuant\OneDrive\Máy tính\LuanVanTotNghiep\House_Price.db'

# Đọc dữ liệu từ CSV
df = pd.read_csv(csv_file_path)

# Kết nối đến cơ sở dữ liệu SQLite
conn = sqlite3.connect(sqlite_db_path)
cursor = conn.cursor()

# Chuyển dữ liệu từ DataFrame vào bảng 'articles' trong SQLite
table_name = 'House_Price'
df.to_sql(table_name, conn, if_exists='replace', index=False)

# Kiểm tra xem bảng 'articles' có tồn tại và lấy 5 dòng đầu tiên
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (table_name,))
if cursor.fetchone():
    print(f"Bảng '{table_name}' tồn tại.")
    cursor.execute(f"SELECT * FROM {table_name} LIMIT 5;")
    rows = cursor.fetchall()
    for row in rows:
        print(row)
else:
    print(f"Bảng '{table_name}' không tồn tại.")

# Đóng kết nối
conn.close()
