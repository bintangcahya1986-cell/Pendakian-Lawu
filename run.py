"""
Entry point — run with:
    python run.py
or in production use gunicorn:
    gunicorn -w 2 -b 0.0.0.0:5000 "run:app"
"""
from dotenv import load_dotenv
load_dotenv()

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
