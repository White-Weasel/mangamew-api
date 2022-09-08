# Backend cho MangaMew.

## Set up project:

* Khôi phục databse PostgreSQL từ file db_backup/db_bak.backup.
* Thêm một service với tên `mangadex_clone_service` trong file `pg_service.conf`của PostgreSQL. 
File pg_service.conf thường nằm tại thư mục `C:\Users\<User name>\AppData\Local\postgres\pg_service.conf` trên Window hoặc `~/.pg_service.conf` trên Linux. Tạo mới file nếu file chưa tồn tại.
* Ví dụ nội dung file pg_service.conf:
```ini 
[mangaMew_service]
host=localhost
user=postgres
password=<Your password here>
dbname=<Your database's name>
port=5432
```
- Cài đặt các package cần thiết:
`pip install -r requirements.txt`
- Khởi động server: `py main.py`
