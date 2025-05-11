from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import os

app = Flask(__name__)
CORS(app)

API_KEY = os.getenv("API_KEY")
API_URL = "https://openrouter.ai/api/v1/chat/completions"

MODELS = [
    "deepseek/deepseek-r1-distill-qwen-32b:free",
    "qwen/qwq-32b:free",
    "mistralai/mistral-small-3.1-24b-instruct:free",
]

emotion_category_map = {
    'безмятежность': 'положительная', 'восторг': 'положительная',
    'восхищение': 'положительная', 'доверие': 'положительная',
    'интерес': 'положительная', 'ожидание': 'положительная',
    'принятие': 'положительная', 'радость': 'положительная',

    'гнев': 'отрицательная', 'горе': 'отрицательная',
    'грусть': 'отрицательная', 'досада': 'отрицательная',
    'злость': 'отрицательная', 'настороженность': 'отрицательная',
    'неудовольствие': 'отрицательная', 'отвращение': 'отрицательная',
    'печаль': 'отрицательная', 'страх': 'отрицательная',
    'тревога': 'отрицательная', 'ужас': 'отрицательная',

    'изумление': 'нейтральная', 'ничего': 'нейтральная',
    'растерянность': 'нейтральная', 'скука': 'нейтральная',
    'удивление': 'нейтральная'
}

model_weights = {
    "deepseek/deepseek-r1-distill-qwen-32b:free": {
        "положительная": 0.2,
        "отрицательная": 0.2,
        "нейтральная": 0.2,
        "смешанная": 0.6,
    },
    "qwen/qwq-32b:free": {
        "положительная": 0.2,
        "отрицательная": 0.2,
        "нейтральная": 0.2,
        "смешанная": 0.5,
    },
    "mistralai/mistral-small-3.1-24b-instruct:free": {
        "положительная": 0.6,
        "отрицательная": 0.7,
        "нейтральная": 0.8,
        "смешанная": 0.9,
    },
}


def query_llm(text: str, model: str, task: str) -> str:
    """Общий метод запроса к LLM"""
    content = ""
    if task == "category":
        content = (
            f"Определи категорию эмоций из перечня: положительная, отрицательная, нейтральная, смешанная. "
            f"Ответь одним словом. Вот текст: {text}"
        )

        payload = {
            "model": model,
            "messages": [{"role": "user", "content": content}],
        }
    elif task == "emotion":
        emotions_list = [
            'безмятежность', 'восторг', 'восхищение', 'гнев', 'горе',
            'грусть', 'доверие', 'досада', 'злость', 'изумление',
            'интерес', 'настороженность', 'неудовольствие', 'ничего',
            'ожидание', 'отвращение', 'печаль', 'принятие', 'радость',
            'растерянность', 'скука', 'страх', 'тревога', 'удивление', 'ужас'
        ]

        prompt = f"""Определи ОДНУ основную эмоцию в тексте. Ответь только одним словом из списка:
            {', '.join(emotions_list)}. Не добавляй пояснений!"""

        payload = {
            "model": model,
            "messages": [
                    {"role": "system", "content": "Ты определяешь эмоции в текстах."},
                    {"role": "user", "content": prompt},
                    {"role": "user", "content": f"Текст: {text}. Выведи одну эмоцию одним словом"}
                ],
        }


    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        print("Ответ модели ", model, ": ", response.json()["choices"][0]["message"]["content"].strip().lower())
        return response.json()["choices"][0]["message"]["content"].strip().lower()
    else:
        raise Exception(response.text)


@app.route("/api/emotion", methods=["POST"])
def detect_emotion():
    data = request.get_json()
    text = data.get("text")
    selected_model = data.get("model")

    if not text or not selected_model:
        return jsonify({"error": "Некорректный запрос"}), 400

    if selected_model != "voting":
        try:
            emotion = query_llm(text, selected_model, "emotion")
            return jsonify({"emotion": emotion})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    scores = {}

    for model in MODELS:
        try:
            response_emotion = query_llm(text, model, "emotion")

            emotion_list = [e.strip() for e in response_emotion.split(",")]

            if len(emotion_list) > 1:
                category = "смешанная"
            else:
                emotion = emotion_list[0]
                category = emotion_category_map.get(emotion, "нейтральная")

            weight = model_weights[model].get(category, 0)

            for em in emotion_list:
                scores[em] = scores.get(em, 0) + weight

        except Exception as e:
            print(f"Ошибка при запросе к {model}: {e}")

    if not scores:
        return jsonify({"error": "Не удалось определить эмоции"}), 500

    best_emotion = max(scores.items(), key=lambda kv: kv[1])[0]
    return jsonify({"emotion": best_emotion})



if __name__ == "__main__":
    app.run(debug=True)
