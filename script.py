import os
from app import app, db
from sqlalchemy import inspect

with app.app_context():
    try:
        db.create_all()  # 테이블 생성
        print("테이블 생성 완료.")  # 확인용 출력
        print("현재 디렉토리:", os.getcwd())  # 현재 디렉토리 확인
        print("데이터베이스 파일 확인:", os.path.exists("news_project.db"))  # DB 파일 존재 확인
        
        # 테이블 목록 출력
        inspector = inspect(db.engine)
        print(inspector.get_table_names())  # 데이터베이스의 테이블 목록 출력
        
    except Exception as e:
        print("에러 발생:", e)  # 에러 발생 시 출력

