# Backend cho MangaMew sử dụng Mangadex API.
Do api của mangadex chặn cross-origin request nên cần có một proxy server nhận request từ frontend và trả về kết quả request được từ api của Mangadex.
## Set up project:
- Cài đặt các package cần thiết: `pip install -r requirements.txt`
- Khởi động server: `py main.py`