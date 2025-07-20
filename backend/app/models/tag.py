from .. import db

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('tag.id'))
    parent = db.relationship('Tag', remote_side=[id], backref='children')
