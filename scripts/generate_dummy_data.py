import pandas as pd
import random
from faker import Faker
from datetime import datetime, timedelta
import os

fake = Faker('ko_KR')

NUM_USERS = 100
NUM_NEWS = 600
NUM_SCRAPS = 4000

LEVELS = ['초급', '중급', '고급']
GENDERS = ['남자', '여자']
CATEGORIES = ['경제', '사회', '국제', '문화', '연예', '스포츠', 'IT', '과학', '생활']
SCORE_PROB = {'like': 0.2, 'scrap': 0.5, 'wrong_answer': 0.3}

today = datetime.today()

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

    # 관심 카테고리 1~3개
    interested = random.sample(CATEGORIES, k=random.randint(1, 3))
    for category in interested:
        user_interests.append({'user_id': i, 'category': category})

# 2. news.csv
news = []
for i in range(1, NUM_NEWS + 1):
    news.append({
        'news_id': i,
        'title': fake.sentence(nb_words=6),
        'category': random.choice(CATEGORIES),
        'publishedDate': fake.date_time_between(start_date='-30d', end_date='now')
    })

# 3. scrap.csv (흥미 카테고리에 따른 점수 확률 반영)
scraps = []
for _ in range(NUM_SCRAPS):
    user = random.choice(users)
    news_item = random.choice(news)
    user_id = user['user_id']
    news_id = news_item['news_id']
    news_category = news_item['category']

    user_interest_categories = [ui['category'] for ui in user_interests if ui['user_id'] == user_id]

    # 흥미있는 카테고리면 like 확률 높임
    if news_category in user_interest_categories:
        scrap_type = random.choices(['like', 'scrap', 'wrong_answer'], weights=[0.5, 0.4, 0.1])[0]
    else:
        scrap_type = random.choices(['like', 'scrap', 'wrong_answer'], weights=[0.05, 0.4, 0.55])[0]

    scraps.append({
        'user_id': user_id,
        'news_id': news_id,
        'type': scrap_type,
        'created_at': fake.date_time_between(start_date='-7d', end_date='now')
    })

# 저장
os.makedirs("../data", exist_ok=True)
pd.DataFrame(users).to_csv("../data/users.csv", index=False)
pd.DataFrame(news).to_csv("../data/news.csv", index=False)
pd.DataFrame(scraps).to_csv("../data/scrap.csv", index=False)
pd.DataFrame(user_interests).to_csv("../data/user_interest.csv", index=False)

print("✅ 현실적인 더미 데이터 생성 완료: users.csv, news.csv, scrap.csv, user_interest.csv")
