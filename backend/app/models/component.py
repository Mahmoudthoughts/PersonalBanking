from .. import db


class Component(db.Model):
    """Breakdown of a transaction."""

    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.id'))
    label = db.Column(db.Text, nullable=False)
    amount = db.Column(db.Numeric(10, 2))
    vat = db.Column(db.Numeric(10, 2))

    transaction = db.relationship('Transaction', back_populates='components')

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Component {self.label} {self.amount}>"
