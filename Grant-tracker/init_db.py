# Script to initialize the SQLite database for Grant-tracker
from app import db, app

def main():
    with app.app_context():
        db.create_all()
        print("Database initialized.")

if __name__ == "__main__":
    main()
