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
users = pd.read_csv(USER_CSV).rename(columns={'user_id': 'user_id'})
news = pd.read_csv(NEWS_CSV)
scrap = pd.read_csv(SCRAP_CSV)
user_interests = pd.read_csv(INTEREST_CSV).rename(columns={'category_id': 'category_interest'})

# 2. 나이 계산: birth_date → age
def calculate_age(birth_str):
    birth = pd.to_datetime(birth_str)
    today = datetime.today()
    return today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))

users['age'] = users['birth_date'].apply(calculate_age)

# 3. scrap에 user_id 붙이기
scrap = scrap.merge(users[['user_id', 'user_email']], left_on='user_email', right_on='user_email', how='left')
missing_ids = scrap['user_id'].isna().sum()
if missing_ids > 0:
    print(f"⚠️ user_id가 없는 행 수: {missing_ids}")

# 4. 점수 매핑
score_map = {'like': 100, 'scrap': 50, 'wrong_answer': 1}
scrap['score'] = scrap['status'].map(score_map)

# 5. 흥미 여부 계산
news_cat = news[['news_id', 'category']]
temp = scrap.merge(news_cat, on='news_id', how='left') \
            .merge(user_interests, on='user_id', how='left')
temp['interest_match'] = (temp['category'] == temp['category_interest']).astype(int)

interest_flags = temp.groupby(['user_id', 'news_id'])['interest_match'].max().reset_index()

# 6. 최종 점수 계산
scrap_unique = scrap.groupby(['user_id', 'news_id'])['score'].max().reset_index()
scored = scrap_unique.merge(interest_flags, on=['user_id', 'news_id'], how='left')
scored['interest_match'] = scored['interest_match'].fillna(0)
scored['score'] *= (1 + 0.2 * scored['interest_match'])

# 7. 뉴스 조회 수 계산 및 변환
view_counts = scrap.groupby('news_id').size().reset_index(name='news_view_count')
news = news.merge(view_counts, on='news_id', how='left')
news['news_view_count'] = news['news_view_count'].fillna(0)
news['news_view_count'] = np.log1p(news['news_view_count'])

# 8. 피처 병합
user_features = users[['user_id', 'gender', 'level', 'age']]
news_features = news[['news_id', 'category', 'news_view_count']]
final = scored.merge(user_features, on='user_id', how='left') \
              .merge(news_features, on='news_id', how='left')

# 9. 피처 및 라벨 분리
features = final[['gender', 'level', 'category', 'age', 'interest_match', 'news_view_count']].copy()
labels = final['score']

# 10. 인코딩
for col in ['gender', 'level', 'category']:
    le = LabelEncoder()
    features[col] = le.fit_transform(features[col].astype(str))

# 11. 학습/검증 분할
X_train, X_test, y_train, y_test = train_test_split(
    features, labels, test_size=0.3, random_state=42
)

print("✅ 학습 샘플 수:", len(X_train), "/ 검증 샘플 수:", len(X_test))
print("📊 점수 분포:\n", labels.value_counts())

# 12. LightGBM 학습
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

# 13. 모델 저장
with open(MODEL_PATH, 'wb') as f:
    pickle.dump(model, f)

print(f"🎉 모델 학습 완료! → 저장 경로: {MODEL_PATH}")
