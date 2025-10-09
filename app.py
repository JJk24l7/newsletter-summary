from flask import session  # 맨 위에 추가(시연하고 지우기기)
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import or_

from models import db, User, News, Interest, Notification


def create_notifications_for_news(news_item):
    """새 뉴스 1건에 대해 관심사와 매칭되는 모든 사용자에게 Notification 레코드 생성"""
    for user in User.query.all():
        for inter in user.interests:
            kw_hit  = inter.keyword  and inter.keyword  in (news_item.keyword or "")
            cat_hit = inter.category and inter.category == (news_item.category or "")
            if kw_hit or cat_hit:
                exists = Notification.query.filter_by(user_id=user.id,
                                                      news_id=news_item.id).first()
                if not exists:
                    db.session.add(Notification(user_id=user.id, news_id=news_item.id))
                break           # 사용자당 한 번만 생성
    db.session.commit()




def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key'

    import os
    from dotenv import load_dotenv
    if os.environ.get("RENDER") != "true":
        load_dotenv()

    def normalize_db_url(raw: str) -> str:
        url = raw or ""
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
        if "sslmode=" not in url:
            url += ("&" if "?" in url else "?") + "sslmode=require"
        return url

    raw_url = os.getenv("DATABASE_URL")
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "connect_args": {"sslmode": "require"},
    }

    masked = re.sub(r":[^@]+@", ":***@", url)
    print(f"[BOOT] USING DB URL: {masked}")
    print(f"[BOOT] PGSSLMODE={os.environ.get('PGSSLMODE')} RENDER={os.environ.get('RENDER')}")


    db.init_app(app)
    Migrate(app, db)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    @app.context_processor
    def inject_notifications():
        if current_user.is_authenticated:
            notis = Notification.query.filter_by(user_id=current_user.id,
                                                 is_read=False).all()
            return dict(notifications=[n.news for n in notis])
        return dict(notifications=[])
    
    @app.get("/dbping")
    def dbping():
        try:
            with db.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return "db ok", 200
        except Exception as e:
            return f"db error: {e}", 500

    @app.get("/healthz")
    def healthz():
        return "ok", 200

    # ✅ '/' 경로를 search.html과 동일하게 동작하도록 설정
    @app.route('/')
    def index():
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

        bookmarked_news_ids = []
        if current_user.is_authenticated:
            bookmarked_news_ids = [n.id for n in current_user.favorites]
        else:
            bookmarked_news_ids = session.get('bookmarked_ids', [])

        return render_template('search.html',
                               news_items=filtered_news,
                               keyword=keyword,
                               selected_category=category,
                               bookmarked_news_ids=bookmarked_news_ids)

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

        bookmarked_news_ids = []
        if current_user.is_authenticated:
            bookmarked_news_ids = [n.id for n in current_user.favorites]
        else:
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
        session.clear()
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

    @app.route('/interests', methods=['GET', 'POST'])
    @login_required
    def interests():
        if request.method == 'POST':
            keyword = request.form.get('keyword').strip()
            category = request.form.get('category').strip()

            if keyword or category:
                new_interest = Interest(user_id=current_user.id, keyword=keyword, category=category)
                db.session.add(new_interest)
                db.session.commit()

        user_interests = Interest.query.filter_by(user_id=current_user.id).all()
        return render_template('interests.html', interests=user_interests)

    @app.route('/delete_interest/<int:interest_id>', methods=['POST'])
    @login_required
    def delete_interest(interest_id):
        interest = Interest.query.get_or_404(interest_id)
        if interest.user_id != current_user.id:
            return "권한 없음", 403
        db.session.delete(interest)
        db.session.commit()
        return redirect(url_for('interests'))


    return app

app = create_app()

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)


