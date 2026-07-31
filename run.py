import os
from app import create_app, db

app = create_app(os.getenv('FLASK_CONFIG', 'default'))

if __name__ == '__main__':
    print("=" * 60)
    print("Starting Personal Financial Management System (FinTech Platform)...")
    print("   Serving on: http://127.0.0.1:5000")
    print("=" * 60)
    app.run(host='127.0.0.1', port=5000, debug=True)
