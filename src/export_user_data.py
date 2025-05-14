import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()  # .env 파일을 읽어 환경변수로 설정

# 날짜별 디렉토리 생성
today_str = datetime.today().strftime('%Y-%m-%d')
output_dir = f"../data/{today_str}"
os.makedirs(output_dir, exist_ok=True)

# 유저 DB 연결
user_db_url = os.getenv("DB_URL_USER")
print(f"DB URL: {user_db_url}")
user_engine = create_engine(user_db_url)


# 테이블 존재 여부 확인 및 없으면 생성
def ensure_table_exists(engine, table_name, create_sql):
    with engine.connect() as conn:
        result = conn.execute(text(f"""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_name = '{table_name}'
        """))
        exists = result.scalar() > 0
        if not exists:
            print(f"[!] '{table_name}' 테이블이 존재하지 않습니다. 생성 중...")
            conn.execute(text(create_sql))
            print(f"[+] '{table_name}' 테이블 생성 완료.")
        else:
            print(f"[✓] '{table_name}' 테이블 존재 확인됨.")


# 테이블 생성 SQL 정의
create_user_table_sql = """
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    user_email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    username VARCHAR(255) NOT NULL,
    level VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

create_user_interest_table_sql = """
CREATE TABLE user_interest (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
"""

# 테이블 목록 및 파일명 정의
tables = {
    "users": {
        "filename": "users.csv",
        "create_sql": create_user_table_sql
    },
    "user_interest": {
        "filename": "user_interest.csv",
        "create_sql": create_user_interest_table_sql
    }
}

# 테이블 생성 확인 및 CSV로 저장
# for table_name, info in tables.items():
#     ensure_table_exists(user_engine, table_name, info["create_sql"])
try:
    df = pd.read_sql(f"SELECT user_id,birth_date,create_at,user_email,gender,level FROM users", user_engine)
    print(df)
    df.to_csv(os.path.join(output_dir, "users.csv"), index=False)
    print(f"[→] users → {output_dir}/users")
except ProgrammingError as e:
    print(f"[X] users 조회 실패: {e}")
try:
    df = pd.read_sql(f"SELECT * FROM user_interest", user_engine)
    print(df)
    df.to_csv(os.path.join(output_dir, "user_interest.csv"), index=False)
    print(f"[→] user_interest → {output_dir}/user_interest")
except ProgrammingError as e:
    print(f"[X] user_interest 조회 실패: {e}")
