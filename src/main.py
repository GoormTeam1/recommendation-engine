import subprocess

def run_script(script_name):
    print(f"실행 중: {script_name}")
    result = subprocess.run(["python", script_name], capture_output=True, text=True)

    if result.returncode != 0:
        print(f"실패: {script_name}")
        print(result.stderr)
        exit(1)  # 실패 시 전체 종료
    else:
        print(f"완료: {script_name}")
        print(result.stdout)

if __name__ == "__main__":
    scripts = [
        "export_user_data.py",
        "export_news_data.py",
        "train_model.py",
        "predict.py",
        "import_recommendation_data.py",
        "import_default_recommendation_data.py",
        "consumer.py"
    ]

    for script in scripts:
        run_script(script)

    print("전체 파이프라인 완료")
