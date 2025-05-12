from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

favorites = db.Table('favorites',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('news_id', db.Integer, db.ForeignKey('news.id'))
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    favorites = db.relationship('News', secondary=favorites, backref=db.backref('liked_by', lazy='dynamic'))

class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300))
    url = db.Column(db.String(300))
    date = db.Column(db.String(50))
    company = db.Column(db.String(100))
    keyword = db.Column(db.String(300))
    wordcloud_image = db.Column(db.String(300))
    category = db.Column(db.String(100))  # 혹시 카테고리 필터 쓸 거면 필요함
