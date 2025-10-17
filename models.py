from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Record(db.Model):
    __tablename__ = 'records'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    date = db.Column(db.Date, nullable=False)
    pdf_link = db.Column(db.String(200), nullable=False)
    status = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<Record {self.id} - {self.name}>'
