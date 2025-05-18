# migrate_data.py
from flask import Flask
from app import create_app, db
from models import User, News, Interest, Notification, favorites
from sqlalchemy import create_engine, Table, MetaData
from sqlalchemy.orm import sessionmaker

# 1. SQLite 연결
sqlite_engine = create_engine('sqlite:///app.db')
SQLiteSession = sessionmaker(bind=sqlite_engine)
sqlite_session = SQLiteSession()

# 2. PostgreSQL 연결 (Flask app context 사용)
app = create_app()
with app.app_context():
    db.create_all()  # PostgreSQL 테이블 생성

    # 3. 기존 테이블 데이터 옮기기
    users = sqlite_session.query(User).all()
    news_list = sqlite_session.query(News).all()
    interests = sqlite_session.query(Interest).all()
    notifications = sqlite_session.query(Notification).all()

    for u in users:
        exists = db.session.get(User, u.id)
        if not exists:
            new_u = User(id=u.id, email=u.email, password=u.password)
            db.session.add(new_u)
    for n in news_list:
        exists = db.session.get(News, n.id)
        if not exists:
            new_n = News(
                id=n.id,
                title=n.title,
                url=n.url,
                date=n.date,
                company=n.company,
                keyword=n.keyword,
                wordcloud_image=n.wordcloud_image,
                category=n.category
            )
            db.session.add(new_n)

    for i in interests:
        exists = db.session.get(Interest, i.id)
        if not exists:
            new_i = Interest(
                id=i.id,
                keyword=i.keyword,
                category=i.category,
                user_id=i.user_id
            )
            db.session.add(new_i)

    for noti in notifications:
        db.session.add(Notification(
            id=noti.id,
            user_id=noti.user_id,
            news_id=noti.news_id,
            is_read=noti.is_read
        ))

    # 4. favorites 중간 테이블 옮기기
    sqlite_meta = MetaData()
    sqlite_meta.reflect(bind=sqlite_engine)
    sqlite_favorites = Table('favorites', sqlite_meta, autoload_with=sqlite_engine)

    with sqlite_engine.connect() as conn:
        favorites_data = conn.execute(sqlite_favorites.select()).fetchall()

    for row in favorites_data:
        user_id = row[0]  # 튜플의 첫 번째 요소
        news_id = row[1]  # 두 번째 요소
        insert_stmt = favorites.insert().values(user_id=user_id, news_id=news_id)
        db.session.execute(insert_stmt)


    db.session.commit()
    print("✅ 모든 데이터 마이그레이션 완료 (users, news, interests, notifications, favorites)")

