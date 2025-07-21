from .. import db

transaction_tags = db.Table(
    "transaction_tags",
    db.Column("transaction_id", db.Integer, db.ForeignKey("transaction.id"), primary_key=True),
    db.Column("tag_id", db.Integer, db.ForeignKey("tag.id"), primary_key=True),
)


class Transaction(db.Model):
    """Credit card transaction."""

    id = db.Column(db.Integer, primary_key=True)
    transaction_date = db.Column(db.Date, nullable=False)
    posting_date = db.Column(db.Date)
    description = db.Column(db.Text, nullable=False)
    original_amount = db.Column(db.Numeric(10, 2))
    vat = db.Column(db.Numeric(10, 2))
    total_amount = db.Column(db.Numeric(10, 2))
    currency = db.Column(db.String(10))
    is_credit = db.Column(db.Boolean, default=False)
    cardholder_name = db.Column(db.String(100))
    source_file = db.Column(db.String(200))

    tags = db.relationship("Tag", secondary=transaction_tags, backref="transactions")
    components = db.relationship(
        "Component", back_populates="transaction", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Transaction {self.description} {self.total_amount}>"
