from flask import session  # 맨 위에 추가(시연하고 지우기기)
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import or_

from models import db, User, News

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/yujeo/OneDrive/바탕 화면/산프코딩/웹/app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    Migrate(app, db)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.route('/')
    def index():
        all_news = News.query.all()
        return render_template('index.html', news_items=all_news)

    @app.route('/search', methods=['GET'])
    def search():
        keyword = request.args.get('keyword', '')
        category = request.args.get('category', '')

        query = News.query
        if keyword:
            query = query.filter(or_(
                News.keyword.like(f"%{keyword}%"),
                News.title.like(f"%{keyword}%")
            ))
        if category:
            query = query.filter(News.category == category)

        filtered_news = query.all()

        # ✅ 로그인한 사용자의 북마크된 뉴스 ID
        bookmarked_news_ids = []
        if current_user.is_authenticated:
            bookmarked_news_ids = [n.id for n in current_user.favorites]
        else:
            # [시연용] 로그인 안 한 경우 세션에서 북마크 읽기
            # [시연 후 삭제]
            bookmarked_news_ids = session.get('bookmarked_ids', [])

        return render_template('search.html',
                               news_items=filtered_news,
                               keyword=keyword,
                               selected_category=category,
                               bookmarked_news_ids=bookmarked_news_ids)

    @app.route('/mypage')
    def mypage():
        return render_template('mypage.html')

    @app.route('/api/suggestions')
    def get_suggestions():
        query = request.args.get('q', '').strip()
        suggestions = set()
        if not query:
            return jsonify(suggestions=[])
        matched_news = News.query.filter(News.keyword.like(f"%{query}%")).all()
        for news in matched_news:
            if news.keyword:
                for kw in news.keyword.split(','):
                    kw = kw.strip()
                    if query in kw and kw != query:
                        suggestions.add(kw)
        return jsonify(suggestions=list(suggestions))

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            email = request.form['email']
            pw = request.form['password']
            hashed_pw = generate_password_hash(pw)
            user = User(email=email, password=hashed_pw)
            db.session.add(user)
            db.session.commit()
            return redirect('/login')
        return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            email = request.form['email']
            pw = request.form['password']
            user = User.query.filter_by(email=email).first()
            if user and check_password_hash(user.password, pw):
                login_user(user)

                session['logged_in'] = True
                session['email'] = email
                return redirect('/')
                
        return render_template('login.html')

    @app.route('/logout')
    def logout():
        logout_user()
        session.clear()  # ✅ 세션 정보 전체 삭제
        return redirect('/login')

    @app.route('/bookmark/<int:news_id>', methods=['POST'])
    @login_required
    def bookmark(news_id):
        if current_user.is_authenticated:
            news_item = News.query.get(news_id)
            if news_item in current_user.favorites:
                current_user.favorites.remove(news_item)
            else:
                current_user.favorites.append(news_item)
            db.session.commit()
        else:
        # 🔹 시연용: 로그인 안 해도 북마크 저장
            if 'bookmarked_ids' not in session:
                session['bookmarked_ids'] = []
            bookmarked_ids = session['bookmarked_ids']
            if news_id in bookmarked_ids:
                bookmarked_ids.remove(news_id)
            else:
                bookmarked_ids.append(news_id)
            session['bookmarked_ids'] = bookmarked_ids
        return redirect(request.referrer or '/')

    @app.route('/my_bookmarks')
    @login_required
    def my_bookmarks():
        bookmarks = current_user.favorites
        return render_template('saved_articles.html', news_list=bookmarks)

    return app

app = create_app()

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)



