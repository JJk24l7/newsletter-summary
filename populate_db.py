from app import db, News, app  # app.py에서 db, News 모델, Flask 애플리케이션 가져오기

# Flask 애플리케이션 컨텍스트 설정
with app.app_context():
    

    # 샘플 데이터 추가
    sample_news = [
        News(
            title="현대백화점, 면세점·지누스 효과에 1분기 영업이익 63% 증가",
            date="2025.05.09. 오후 4:29",
            company="서울경제",
            keyword="백화점, 현대, 매출, 영업이익, 증가",
            wordcloud_image="economy_wordcloud6.png",  
            url="https://n.news.naver.com/mnews/article/011/0004483420?sid=101",
            category="경제",  # 카테고리 추가
        ),
        News(
            title="백종원의 '300억 협력 지원금' 카드...가맹점주 마음 얻을까",
            date="2025.05.09. 오후 5:53",
            company="한국일보",
            keyword="대표, 가맹점, 지원, 간담회, 백종원",
            wordcloud_image="economy_wordcloud7.png",  
            url="https://n.news.naver.com/mnews/article/469/0000863883?sid=101",
            category="경제"  # 카테고리 추가
        ),
        News(
            title="최태원 'AI 이미 늦었다…잘 할 수 있는 한국형 AI에 집중해야'",
            date="2025.05.09. 오후 7:05",
            company="한경비즈니스",
            keyword="AI, 회장, 인공지능, 데이터, SK",
            wordcloud_image="economy_wordcloud8.png", 
            url="https://n.news.naver.com/mnews/article/050/0000090579",
            category="경제"  # 카테고리 추가
        ),
        
        News(
            title="'美 관세 통상위기, 새로운 국제질서 구축 기회로 삼아야'",
            date="2025.05.09. 오후 7:02",
            company="아이뉴스24",
            keyword="관세, 대응, 미국, 행정부, 트럼프",
            wordcloud_image="economy_wordcloud9.png",
            url="https://n.news.naver.com/mnews/article/031/0000931034",
            category="경제"  # 카테고리 추가
        ),
        News(
            title="대한항공, 캐나다 2위 항공사 '웨스트젯' 지분 10% 인수…미주서 영토 확장",
            date="2025.05.09. 오후 7:06",
            company="서울경제",
            keyword="대한항공, 지분, 웨스트, 인수, 시장",
            wordcloud_image="economy_wordcloud10.png",
            url="https://n.news.naver.com/mnews/article/011/0004483502",
            category="경제"  # 카테고리 추가
        )
    ]

    # 데이터 중복 확인 후 삽입
    for news in sample_news:
        existing_news = News.query.filter_by(title=news.title).first()
        if not existing_news:
            db.session.add(news)
    db.session.commit()

    print("샘플 데이터 삽입 완료!")


