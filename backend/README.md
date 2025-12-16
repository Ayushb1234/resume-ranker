# Backend - Resume Rank Demo

Prereqs:
- Python 3.10+
- System packages:
  - tesseract-ocr
  - poppler-utils (for pdf2image)

Ubuntu:
sudo apt update
sudo apt install -y tesseract-ocr poppler-utils

Install python deps:
pip install -r requirements.txt

Run:
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

The React frontend expects the backend at http://localhost:8000
