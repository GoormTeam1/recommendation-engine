import redis
import pandas as pd
from datetime import date
import os
import json

# Redis 연결
r = redis.Redis(host='localhost', port=6379, db=0)

# 카테고리 매핑 리스트
CATEGORIES = ['us',
              'world',
              'politics',
              'business',
              'health',
              'entertainment',
              'style',
              'travel',
              'sports',
              'science',
              'climate',
              'weather']

def import_default_recommendation_data():
    today_str = date.today().isoformat()
    csv_path = os.path.join("data", today_str, "news.csv")

    # CSV 읽기
    df = pd.read_csv(csv_path)

    # 카테고리 매핑
   # df['category'] = df['category'].apply(lambda idx: CATEGORIES[int(idx)])

    # 최신 뉴스 정렬 기준 컬럼이 없다면 'publishedDate' 혹은 'news_id' 기준 사용
    if 'publishedDate' in df.columns:
        df['publishedDate'] = pd.to_datetime(df['publishedDate'])
        df = df.sort_values(by='publishedDate', ascending=False)
    else:
        df = df.sort_values(by='news_id', ascending=False)

    # 카테고리별로 가장 최신 뉴스만 추출
    latest_by_category = df.groupby('category').head(1)

    # 필요한 컬럼만 선택하여 리스트로 변환
    default_recommendations = latest_by_category[['news_id', 'category']].to_dict(orient='records')

    # Redis 저장
    redis_key = "recommendation:default"
    r.setex(redis_key, 86400, json.dumps(default_recommendations))
    print(f"✅ 저장 완료: {redis_key} → {default_recommendations}")

# 함수 실행
import_default_recommendation_data()
