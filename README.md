### Steps to run the app

0. python3 -m venv venv
1. source venv/bin/activate
2. .venv\Scripts\Activate.ps1
3. python3 -m pip install -r requirements.txt
4. uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
