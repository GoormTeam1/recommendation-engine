import pandas as pd
import lightgbm as lgb
import pickle
import os
import numpy as np
from datetime import datetime
from lightgbm import early_stopping, log_evaluation
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

# 오늘 날짜 폴더 설정
today_str = datetime.today().strftime('%Y-%m-%d')
DATA_DIR = f"../data/{today_str}"
MODEL_DIR = f"../models/{today_str}"
os.makedirs(MODEL_DIR, exist_ok=True)

# 경로 설정
USER_CSV = os.path.join(DATA_DIR, "users.csv")
NEWS_CSV = os.path.join(DATA_DIR, "news.csv")
SCRAP_CSV = os.path.join(DATA_DIR, "scrap.csv")
INTEREST_CSV = os.path.join(DATA_DIR, "user_interest.csv")
MODEL_PATH = os.path.join(MODEL_DIR, "lightgbm_model.pkl")

# 1. 데이터 불러오기
users = pd.read_csv(USER_CSV)
news = pd.read_csv(NEWS_CSV)
scrap = pd.read_csv(SCRAP_CSV)
interests = pd.read_csv(INTEREST_CSV)

# 2. 점수 매핑
score_map = {'like': 100, 'scrap': 50, 'wrong_answer': 1}
scrap['score'] = scrap['status'].map(score_map)

# 3. 흥미 여부 계산을 위한 중간 병합
news_cat = news[['news_id', 'category']]
temp = scrap.merge(news_cat, on='news_id', how='left') \
            .merge(interests, on='user_id', how='left', suffixes=('', '_interest'))

temp['interest_match'] = (temp['category'] == temp['category_interest']).astype(int)

# 흥미 있는 경우 하나라도 있으면 플래그 1
interest_flags = temp.groupby(['user_id', 'news_id'])['interest_match'].max().reset_index()

# 스코어 가중치 적용
scrap_unique = scrap.groupby(['user_id', 'news_id'])['score'].max().reset_index()
scored = scrap_unique.merge(interest_flags, on=['user_id', 'news_id'], how='left')
scored['interest_match'] = scored['interest_match'].fillna(0)
scored['score'] = scored['score'] * (1 + 0.2 * scored['interest_match'])  # 20% 가중치

# 4. 뉴스 조회 수 계산 및 log1p 변환
view_counts = scrap.groupby('news_id').size().reset_index(name='news_view_count')
news = news.merge(view_counts, on='news_id', how='left')
news['news_view_count'] = news['news_view_count'].fillna(0)
news['news_view_count'] = np.log1p(news['news_view_count'])

# 5. 피처 병합
users = users[['user_id', 'gender', 'level', 'age']]
news = news[['news_id', 'category', 'news_view_count']]

final = scored.merge(users, on='user_id', how='left') \
              .merge(news, on='news_id', how='left')

# 6. 피처/레이블 설정
features = final[['gender', 'level', 'category', 'age', 'interest_match','news_view_count']].copy()
labels = final['score']

# 7. 인코딩
for col in ['gender', 'level', 'category']:
    le = LabelEncoder()
    features[col] = le.fit_transform(features[col].astype(str))

# 8. 데이터 분할
X_train, X_test, y_train, y_test = train_test_split(
    features, labels, test_size=0.3, random_state=42
)

print("✅ 학습 샘플 수:", len(X_train), "/ 검증 샘플 수:", len(X_test))
print("📊 점수 분포:\n", labels.value_counts())

# 9. LightGBM 학습
train_data = lgb.Dataset(X_train, label=y_train)
valid_data = lgb.Dataset(X_test, label=y_test)

params = {
    'objective': 'regression',
    'metric': 'rmse',
    'verbose': -1
}

model = lgb.train(
    params,
    train_data,
    valid_sets=[valid_data],
    num_boost_round=300,
    callbacks=[
        early_stopping(stopping_rounds=30),
        log_evaluation(period=10)
    ]
)

print("📈 Best RMSE:", model.best_score['valid_0']['rmse'])

# 10. 모델 저장
with open(MODEL_PATH, 'wb') as f:
    pickle.dump(model, f)

print(f"모델 학습 완료! → 저장 경로: {MODEL_PATH}")
