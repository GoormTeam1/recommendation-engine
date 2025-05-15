import requests
from faker import Faker
import random
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

fake = Faker('ko_KR')

CATEGORIES = ['us', 'world', 'politics', 'business', 'health', 'entertainment',
              'style', 'travel', 'sports', 'science', 'climate', 'weather']

def generate_birthdate(start_year=1985, end_year=2005):
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    return (start + timedelta(days=random.randint(0, (end - start).days))).date()

def generate_dummy_user():
    birth_date = generate_birthdate()
    level = random.choice(['상', '중', '하'])
    gender = random.choice(['남자', '여자'])
    category_names = random.sample(CATEGORIES, k=random.randint(1, 4))
    category_list = category_names
    return {
        "email": fake.email(),
        "password": "Test1234",
        "username": fake.user_name(),
        "level": level,
        "birthDate": birth_date.isoformat(),
        "gender": gender,
        "categoryList": category_list
    }

def generate_dummy_scrap(user_email):
    return {
        "userEmail": user_email,
        "newsId": random.randint(1, 300),
        "status": random.choice(["like", "wrong"])
    }

def signup_and_scrap(i):
    signup_url = "http://localhost:8080/api/user/signup"
    scrap_url = "http://localhost:8082/api/scrabs"

    user = generate_dummy_user()
    try:
        signup_res = requests.post(signup_url, json=user)
        result = f"[{i}] 가입: {signup_res.status_code}"

        if signup_res.status_code in (200, 201):
            for j in range(3):
                scrap_data = generate_dummy_scrap(user['email'])
                scrap_res = requests.post(scrap_url, json=scrap_data)
                result += f" | 스크랩{j}: {scrap_res.status_code}"
        else:
            result += f" | ❌ 가입 실패"

    except Exception as e:
        result = f"[{i}] ❌ 예외 발생: {e}"

    return result

# 병렬 실행
if __name__ == "__main__":
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(signup_and_scrap, i) for i in range(100)]
        for future in as_completed(futures):
            print(future.result())
