import pandas as pd

# Đường dẫn tệp CSV ban đầu
input_file_path = r'C:\Users\xuant\OneDrive\Máy tính\LuanVan\articles_data.csv'

# Đọc dữ liệu từ tệp CSV
data = pd.read_csv(input_file_path)

# Thêm cột ID vào đầu
data.insert(0, 'ID', range(1, len(data) + 1))

# Đường dẫn tệp CSV mới
output_file_path = r'C:\Users\xuant\OneDrive\Máy tính\LuanVan\articles_data1.csv'

# Lưu tệp với mã hóa UTF-8
data.to_csv(output_file_path, index=False, encoding='utf-8')

print(f"Tệp đã được lưu tại: {output_file_path}")
