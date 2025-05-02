import pandas as pd
import pickle
from sklearn.preprocessing import LabelEncoder
import os
import numpy as np
from datetime import datetime

# 경로 설정
USER_CSV = "../data/users.csv"
NEWS_CSV = "../data/news.csv"
INTEREST_CSV = "../data/user_interest.csv"
MODEL_PATH = "../models/lightgbm_model.pkl"
OUTPUT_PATH = "../data/recommendations.csv"

# 1. 데이터 불러오기
users = pd.read_csv(USER_CSV)
news = pd.read_csv(NEWS_CSV, parse_dates=['publishedDate'])  # 날짜 파싱
interests = pd.read_csv(INTEREST_CSV)

# 2. news_view_count 결측값 처리 및 log 변환
if 'news_view_count' not in news.columns:
    news['news_view_count'] = 0
news['news_view_count'] = np.log1p(news['news_view_count'])

# 3. 사용자 × 뉴스 조합 생성 + 흥미 여부
candidate_rows = []
for _, user in users.iterrows():
    user_id = user['user_id']
    user_interests = interests[interests['user_id'] == user_id]['category'].tolist()

    for _, article in news.iterrows():
        interest_match = int(article['category'] in user_interests)
        candidate_rows.append({
            'user_id': user_id,
            'news_id': article['news_id'],
            'gender': user['gender'],
            'level': user['level'],
            'age': user['age'],
            'category': article['category'],
            'news_view_count': article['news_view_count'],
            'interest_match': interest_match,
            'publishedDate': article['publishedDate']
        })

df_pred = pd.DataFrame(candidate_rows)

# 4. Label Encoding
for col in ['gender', 'level', 'category']:
    le = LabelEncoder()
    df_pred[col] = le.fit_transform(df_pred[col].astype(str))

# 5. 모델 로드
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"❌ 모델 파일이 존재하지 않습니다: {MODEL_PATH}")

with open(MODEL_PATH, 'rb') as f:
    model = pickle.load(f)

# 6. 예측 및 최신성 가중치
feature_cols = ['gender', 'level', 'category', 'age', 'interest_match', 'news_view_count']
df_pred['score'] = model.predict(df_pred[feature_cols])

# 최신성 가중치 계산: 최근일수록 점수 증가 (가중치 scale은 조정 가능)
today = pd.Timestamp.now().normalize()
df_pred['days_ago'] = (today - df_pred['publishedDate'].dt.normalize()).dt.days
df_pred['recency_weight'] = 1 / (1 + df_pred['days_ago'])  # 최신일수록 1에 가까움
df_pred['adjusted_score'] = df_pred['score'] * df_pred['recency_weight']

# 7. 사용자별 추천 생성 (카테고리 다양성 유지)
top_n_interest = 7
top_n_non_interest = 3
total_n = 10

reco_list = []

for user_id, group in df_pred.groupby('user_id'):
    interest_df = group[group['interest_match'] == 1].sort_values(by='adjusted_score', ascending=False).head(top_n_interest)
    non_interest_df = group[group['interest_match'] == 0].sort_values(by='adjusted_score', ascending=False).head(top_n_non_interest)
    combined = pd.concat([interest_df, non_interest_df])

    # 부족한 경우: 나머지 뉴스 중 점수 순으로 추가
    if len(combined) < total_n:
        already_recommended = set(combined['news_id'])
        remaining_df = group[~group['news_id'].isin(already_recommended)]
        supplement_df = remaining_df.sort_values(by='adjusted_score', ascending=False).head(total_n - len(combined))
        combined = pd.concat([combined, supplement_df])

    reco_list.append(combined)

recommendations = pd.concat(reco_list).sort_values(['user_id', 'adjusted_score'], ascending=[True, False])

# 8. 저장
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
recommendations.to_csv(OUTPUT_PATH, index=False)

print(f"✅ 최신성 + 다양성 반영된 추천 결과 저장 완료 → {OUTPUT_PATH}")
