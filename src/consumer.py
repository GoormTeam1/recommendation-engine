from kafka import KafkaConsumer
import json
from recommendation import generate_recommendation_for_user

# 여러 토픽 구독
consumer = KafkaConsumer(
    'user.signup',
    'user.updateInterest',
    bootstrap_servers='localhost:9092',
    group_id='recommendation-consumer',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

print("[✓] Kafka consumer 시작됨...")

for message in consumer:
    topic = message.topic
    user_payload = message.value
    print(f"[+] 수신한 메시지: {topic} → {user_payload}")

    try:
        if topic == 'user.signup' or topic == 'user.updateInterest':
            generate_recommendation_for_user(user_payload)

        else:
            print(f"[!] 처리하지 않는 토픽입니다: {topic}")
    except Exception as e:
        print(f"추천 처리 중 오류 발생 → 메시지 스킵: {e}")
