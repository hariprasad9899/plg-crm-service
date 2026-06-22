### Steps to run the app

0. python3 -m venv venv
1. Activate virtual environment:
   - **Linux/Mac**: `source venv/bin/activate`
   - **Windows**: `.venv\Scripts\Activate.ps1`
2. python3 -m pip install -r requirements.txt
3. uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
Test
