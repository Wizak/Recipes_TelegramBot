from datetime import datetime
from app import db



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), index=True, nullable=False)
    username = db.Column(db.String(100), index=True, nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    acess= db.Column(db.Boolean, default=False, nullable=False)



class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), index=True, nullable=False)
    date_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)



class Description(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    review = db.Column(db.BLOB)
    components = db.Column(db.Text, index=True, nullable=False)
    description = db.Column(db.Text, index=True, nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)