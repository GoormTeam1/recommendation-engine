import requests
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker('ko_KR')

# 더미 1명 생성 예시
CATEGORIES = ['US', 'World', 'Politics', 'Business', 'Health', 'Entertainment', 'Style', 'Travel', 'Sports', 'Science',
              'Climate', 'Weather']


def generate_dummy_user():
    birth_date = fake.date_of_birth(minimum_age=20, maximum_age=40)
    level = random.choice(['상', '중', '하'])
    gender = random.choice(['남자', '여자'])
    category_names = random.sample(CATEGORIES, k=random.randint(1, 3))
    category_list = [{"name": name} for name in category_names]

    return {
        "email": fake.email(),
        "password": "Test1234",  # 예시 비밀번호 (서버에서 강제 해시 or 허용)
        "username": fake.user_name(),
        "level": level,
        "birthDate": birth_date.isoformat(),  # JSON 직렬화용 ISO 8601
        "gender": gender,
        "categoryList": category_list
    }


dummy_user = generate_dummy_user()

url = "http://localhost:8080/api/user/signup"  # 실제 API 경로로 수정

response = requests.post(url, json=dummy_user)

print("✅ 요청 상태:", response.status_code)
print("📦 응답 내용:", response.text)
