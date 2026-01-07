import json
import os

FILE_NAME = "highscore.json"

def load_highscore():
    if not os.path.exists(FILE_NAME):
        return 0
    try:
        with open(FILE_NAME, "r", encoding="utf-8") as f:
            data = json.load(f)
            return int(data.get("highscore", 0))
    except Exception:
        return 0

def save_highscore(score: int):
    try:
        with open(FILE_NAME, "w", encoding="utf-8") as f:
            json.dump({"highscore": int(score)}, f, ensure_ascii=False, indent=2)
    except Exception:
        pass
