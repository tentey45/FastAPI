@echo off
cd /d "c:\Users\kfumi\OneDrive\Desktop\AnB\FastAPI\fastapi_todo_app"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
