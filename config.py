class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///db.sqlite3'  # SQLite URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'your_secret_key'
    DEBUG = True