import pandas as pd
import random
from faker import Faker
from datetime import datetime, timedelta
import os

fake = Faker('ko_KR')

NUM_USERS = 10
NUM_NEWS = 30
NUM_SCRAPS = 50

LEVELS = ['초급', '중급', '고급']
GENDERS = ['남자', '여자']
CATEGORIES = ['경제', '사회', '국제', '문화', '연예', '스포츠', 'IT','과학','생활']
SCRAP_TYPES = ['like', 'scrap', 'wrong_answer']


# 1. users.csv
users = []
today = datetime.today()

for i in range(1, NUM_USERS + 1):
    birth_date = fake.date_of_birth(minimum_age=18, maximum_age=40)
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

    users.append({
        'user_id': i,
        'email': fake.email(),
        'username': fake.user_name(),
        'gender': random.choice(GENDERS),
        'age': age,
        'level': random.choice(LEVELS)
    })

pd.DataFrame(users).to_csv("../data/users.csv", index=False)

# 2. news.csv
news = []
for i in range(1, NUM_NEWS + 1):
    news.append({
        'news_id': i,
        'title': fake.sentence(nb_words=6),
        'category': random.choice(CATEGORIES),
        'publishedDate': fake.date_time_between(start_date='-30d', end_date='now')
    })
pd.DataFrame(news).to_csv("../data/news.csv", index=False)

# 3. scrap.csv
scraps = []
for _ in range(NUM_SCRAPS):
    scraps.append({
        'user_id': random.randint(1, NUM_USERS),
        'news_id': random.randint(1, NUM_NEWS),
        'type': random.choice(SCRAP_TYPES),
        'created_at': fake.date_time_between(start_date='-7d', end_date='now')
    })
pd.DataFrame(scraps).to_csv("../data/scrap.csv", index=False)

print("더미 데이터 생성 완료: users.csv, news.csv, scrap.csv")
