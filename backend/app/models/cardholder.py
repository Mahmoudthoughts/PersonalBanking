from .. import db

class Cardholder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    color = db.Column(db.String(20))
    transactions = db.relationship("Transaction", back_populates="cardholder")
