import pandas as pd
import lightgbm as lgb
import pickle
import os
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

# 경로 설정
USER_CSV = "../data/users.csv"
NEWS_CSV = "../data/news.csv"
SCRAP_CSV = "../data/scrap.csv"
MODEL_PATH = "../models/lightgbm_model.pkl"

# 1. 데이터 불러오기
users = pd.read_csv(USER_CSV)
news = pd.read_csv(NEWS_CSV)
scrap = pd.read_csv(SCRAP_CSV)

# 2. 행동 점수 매핑
score_map = {'like': 3, 'scrap': 2, 'wrong_answer': 1}
scrap['score'] = scrap['type'].map(score_map)

# 3. 중복 제거 및 점수 최대값 사용
scrap_unique = scrap.groupby(['user_id', 'news_id'])['score'].max().reset_index()

# 4. 병합: 필요한 컬럼만 선택 후 병합
users = users[['user_id', 'gender', 'level','age']]
news = news[['news_id', 'category']]
merged = scrap_unique.merge(users, on='user_id', how='left') \
                     .merge(news, on='news_id', how='left')

# 5. 피처 선택
features = merged[['gender', 'level', 'category']].copy()
labels = merged['score']

# 6. 인코딩
for col in features.columns:
    le = LabelEncoder()
    features[col] = le.fit_transform(features[col].astype(str))

# 7. 학습/테스트 분할
X_train, X_test, y_train, y_test = train_test_split(
    features, labels, test_size=0.2, random_state=42
)

# 8. 모델 학습
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
    num_boost_round=100,
    callbacks=[lgb.early_stopping(stopping_rounds=10)]
)

# 9. 모델 저장
with open(MODEL_PATH, 'wb') as f:
    pickle.dump(model, f)

print(f"모델 학습 완료! → 저장 경로: {MODEL_PATH}")
