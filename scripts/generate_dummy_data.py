import pandas as pd
import random
from faker import Faker
from datetime import datetime, timedelta
import os

fake = Faker('ko_KR')

NUM_USERS = 100
NUM_NEWS = 600
NUM_SCRAPS = 4000

LEVELS = ['상', '중', '하']
GENDERS = ['남자', '여자']
CATEGORIES = ['US', 'World', 'Pollitics', 'Business', 'Heallth',
              'Entertainment', 'Style', 'Travel', 'Sports',
              'Science', 'Climate', 'Weather']
SCORE_PROB = {'like': 0.2, 'scrap': 0.5, 'wrong_answer': 0.3}

today = datetime.today()
today_str = today.strftime('%Y-%m-%d')
DATA_DIR = f"../data/{today_str}"
os.makedirs(DATA_DIR, exist_ok=True)

# 1. users.csv
users = []
user_interests = []
for i in range(1, NUM_USERS + 1):
    birth_date = fake.date_of_birth(minimum_age=18, maximum_age=60)
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    gender = random.choice(GENDERS)
    level = random.choice(LEVELS)

    users.append({
        'user_id': i,
        'email': fake.email(),
        'username': fake.user_name(),
        'gender': gender,
        'age': age,
        'level': level
    })

    interested = random.sample(CATEGORIES, k=random.randint(1, 3))
    for category in interested:
        user_interests.append({'user_id': i, 'category': category})

# 2. news.csv
news = []
for i in range(1, NUM_NEWS + 1):
    news.append({
        'news_id': i,
        'category': random.choice(CATEGORIES),
        'published_at': fake.date_time_between(start_date='-30d', end_date='now'),
        'level': random.choice(LEVELS)  # ✅ 뉴스에도 level 추가
    })

# 3. scrap.csv
scraps = []
for _ in range(NUM_SCRAPS):
    user = random.choice(users)
    news_item = random.choice(news)
    user_id = user['user_id']
    news_id = news_item['news_id']
    news_category = news_item['category']
    user_interest_categories = [ui['category'] for ui in user_interests if ui['user_id'] == user_id]

    if news_category in user_interest_categories:
        scrap_type = random.choices(['like', 'scrap', 'wrong_answer'], weights=[0.5, 0.4, 0.1])[0]
    else:
        scrap_type = random.choices(['like', 'scrap', 'wrong_answer'], weights=[0.05, 0.4, 0.55])[0]

    scraps.append({
        'user_id': user_id,
        'news_id': news_id,
        'status': scrap_type,
        'created_at': fake.date_time_between(start_date='-7d', end_date='now')
    })

# ✅ 날짜 기반 디렉터리에 저장
pd.DataFrame(users).to_csv(os.path.join(DATA_DIR, "users.csv"), index=False)
pd.DataFrame(news).to_csv(os.path.join(DATA_DIR, "news.csv"), index=False)
pd.DataFrame(scraps).to_csv(os.path.join(DATA_DIR, "scrap.csv"), index=False)
pd.DataFrame(user_interests).to_csv(os.path.join(DATA_DIR, "user_interest.csv"), index=False)

print(f"✅ 더미 데이터 생성 완료 → 저장 경로: {DATA_DIR}")
