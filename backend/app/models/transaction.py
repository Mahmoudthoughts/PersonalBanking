from datetime import datetime

from .. import db

transaction_tags = db.Table(
    'transaction_tags',
    db.Column('transaction_id', db.Integer, db.ForeignKey('transaction.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
)


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    cardholder_id = db.Column(db.Integer, db.ForeignKey('cardholder.id'))
    cardholder = db.relationship('Cardholder', back_populates='transactions')
    tags = db.relationship('Tag', secondary=transaction_tags, backref='transactions')
    source_file = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
