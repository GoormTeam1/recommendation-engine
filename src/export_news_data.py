import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()  # .env 파일을 읽어 환경변수로 설정


# 날짜별 디렉토리 생성
today_str = datetime.today().strftime('%Y-%m-%d')
output_dir = f"../data/{today_str}"
os.makedirs(output_dir, exist_ok=True)

# 뉴스 DB 연결
news_db_url = os.getenv("DB_URL_NEWS")
news_engine = create_engine(os.getenv("DB_URL_NEWS"))

# 테이블별 쿼리와 파일명
queries = {
    "scrab": {
        "sql": "SELECT user_email, news_id, status FROM scrab",
        "filename": "scrap.csv"
    },
    "news": {
        "sql": "SELECT news_id, category, published_at FROM news",
        "filename": "news.csv"
    }
}

for table, q in queries.items():
    df = pd.read_sql(q["sql"], news_engine)
    df.to_csv(os.path.join(output_dir, q["filename"]), index=False)
    print(f"[✓] {table} → {output_dir}/{q['filename']}")
