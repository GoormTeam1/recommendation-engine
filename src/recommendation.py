# recommendation.py

import pandas as pd
import pickle
import json
from datetime import datetime
import redis

# Redis 연결
r = redis.Redis(host='localhost', port=6379, db=0)

# 모델 불러오기
today_str = datetime.today().strftime('%Y-%m-%d')
output_model_dir = f"models/{today_str}"
output_news_dir = f"data/{today_str}"
with open(output_model_dir + "/lightgbm_model.pkl", "rb") as f:
    model = pickle.load(f)

# 뉴스 목록 불러오기
news_df = pd.read_csv(output_news_dir+"/news.csv")


def calculate_age(birth_date):
    birth = datetime.strptime(birth_date, "%Y-%m-%d")
    today = datetime.today()
    return today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))


def generate_recommendation_for_user(user):
    age = calculate_age(user['birthDate'])
    interests = user['interests']

    feature_rows = []
    for _, row in news_df.iterrows():
        feature_rows.append({
            "gender": user['gender'],
            "level": user['level'],
            "age": age,
            "category": row['category'],
            "news_view_count": row.get('news_view_count', 0),
            "interest_match": int(row['category'] in interests)
        })

    df = pd.DataFrame(feature_rows)

    # 인코딩
    for col in ["gender", "level", "category"]:
        df[col] = df[col].astype('category').cat.codes

    scores = model.predict(df)
    news_df["score"] = scores

    top_news = news_df.sort_values(by="score", ascending=False).head(10)

    # Redis 저장
    key = f"recommendation:{user['userId']}"
    redis_value = top_news[["news_id", "category", "score"]].to_dict(orient="records")
    print(redis_value)
    r.setex(key, 86400, json.dumps(redis_value))
    print(f"[✓] 추천 저장 완료 → {key}")
