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

# 오늘 날짜를 'YYYY-MM-DD' 형식으로 가져옴
today_str = date.today().isoformat()  # 예: '2025-05-02'

# 경로 조합
csv_path = os.path.join("../data", today_str, "recommendations.csv")

# CSV 읽기
df = pd.read_csv(csv_path)

print(df['category'])
# 카테고리 인덱스를 문자열로 변환
df['category'] = df['category'].apply(lambda idx: CATEGORIES[int(idx)])

# 유저별로 그룹핑 후 Redis 저장
for user_id, group in df.groupby("user_id"):
    news_list = group[['news_id', 'category']].to_dict(orient='records')
    redis_key = f"recommendation:{user_id}"
    r.setex(redis_key, 86400, json.dumps(news_list))  # TTL 1일
    print(f"✅ 저장 완료: {redis_key} → {news_list}")
