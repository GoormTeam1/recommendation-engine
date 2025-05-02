import pandas as pd
import pickle
from sklearn.preprocessing import LabelEncoder
import os

# 경로 설정
USER_CSV = "../data/users.csv"
NEWS_CSV = "../data/news.csv"
MODEL_PATH = "../models/lightgbm_model.pkl"
OUTPUT_PATH = "../data/recommendations.csv"

# 1. 데이터 불러오기
users = pd.read_csv(USER_CSV)
news = pd.read_csv(NEWS_CSV)

# 2. 피처 조합 (모든 사용자 × 모든 뉴스)
candidate_rows = []
for _, user in users.iterrows():
    for _, article in news.iterrows():
        candidate_rows.append({
            'user_id': user['user_id'],
            'news_id': article['news_id'],
            'gender': user['gender'],
            'level': user['level'],
            'category': article['category']
        })

df_candidates = pd.DataFrame(candidate_rows)

# 3. 인코딩
for col in ['gender', 'level', 'category']:
    le = LabelEncoder()
    df_candidates[col] = le.fit_transform(df_candidates[col].astype(str))

# 4. 모델 불러오기
with open(MODEL_PATH, 'rb') as f:
    model = pickle.load(f)

# 5. 예측
df_candidates['score'] = model.predict(df_candidates[['gender', 'level', 'category']])

# 6. 사용자별 Top-N 추천 추출
top_n = 50
recommendations = df_candidates.sort_values(by='score', ascending=False) \
    .groupby('user_id').head(top_n) \
    .sort_values(['user_id', 'score'], ascending=[True, False])

# 7. 저장
recommendations.to_csv(OUTPUT_PATH, index=False)

print(f"추천 결과 저장 완료 → {OUTPUT_PATH}")
