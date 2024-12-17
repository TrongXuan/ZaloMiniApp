
import pandas as pd

# Đường dẫn tệp CSV ban đầu
input_file_path = r'C:\Users\xuant\OneDrive\Máy tính\LuanVan\chitiet1.csv'

# Đọc dữ liệu từ tệp CSV
data = pd.read_csv(input_file_path)

# Đổi tên các cột
columns_mapping = {
    "Diện tích sử dụng": "Usable_Area",
    "Diện tích đất": "Land_Area",
    "Phòng ngủ": "Bedrooms",
    "Nhà tắm": "Bathrooms",
    "Pháp lý": "Legal",
    "Ngày đăng": "Posted_Date",
    "Mã BĐS": "Property_ID"
}
data.rename(columns=columns_mapping, inplace=True)

# Đường dẫn tệp CSV mới
output_file_path = r'C:\Users\xuant\OneDrive\Máy tính\LuanVan\chitiet2.csv'

# Lưu tệp với mã hóa UTF-8
data.to_csv(output_file_path, index=False, encoding='utf-8-sig')

print(f"Tệp đã được lưu tại: {output_file_path}")
