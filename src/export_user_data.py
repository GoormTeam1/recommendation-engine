import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime
import os

# 날짜별 디렉토리 생성
today_str = datetime.today().strftime('%Y-%m-%d')
output_dir = f"../data/{today_str}"
os.makedirs(output_dir, exist_ok=True)

# 유저 DB 연결
user_db_url = 'mysql+pymysql://username:password@localhost:3306/user_db'
user_engine = create_engine(user_db_url)

# 테이블 목록
tables = {
    "user": "users.csv",
    "user_interest": "user_interest.csv"
}

for table_name, file_name in tables.items():
    df = pd.read_sql(f"SELECT * FROM {table_name}", user_engine)
    df.to_csv(os.path.join(output_dir, file_name), index=False)
    print(f"[✓] {table_name} → {output_dir}/{file_name}")
