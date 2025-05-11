from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import os
from config_data import emotion_category_map, emotion_category_map_en, model_weights, model_weights_en, emotions_list_by_lang, MODELS

app = Flask(__name__)
CORS(app)

API_KEY = os.getenv("API_KEY")
API_URL = "https://openrouter.ai/api/v1/chat/completions"


def query_llm(text: str, model: str, lang: str) -> str:
    emotions_list = emotions_list_by_lang.get(lang, emotions_list_by_lang["ru"])

    if lang == "en":
        prompt = f"""Identify ONE main emotion in the text. Respond with ONE word only from this list:
                     {', '.join(emotions_list)}. Do not explain!"""
        system_msg = "You detect emotions in texts."
        user_msg = f"Text: {text}. Output only one emotion as a single word"
    else:
        prompt = f"""Определи ОДНУ основную эмоцию в тексте. Ответь только одним словом из списка:
                     {', '.join(emotions_list)}. Не добавляй пояснений!"""
        system_msg = "Ты определяешь эмоции в текстах."
        user_msg = f"Текст: {text}. Выведи одну эмоцию одним словом"

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": prompt},
            {"role": "user", "content": user_msg}
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
    lang = data.get("lang", "ru")  # по умолчанию "ru"

    if not text or not selected_model:
        return jsonify({"error": "Некорректный запрос"}), 400

    category_map = emotion_category_map if lang == "ru" else emotion_category_map_en
    weights = model_weights if lang == "ru" else model_weights_en

    if selected_model != "voting":
        try:
            emotion = query_llm(text, selected_model, lang)
            return jsonify({"emotion": emotion})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    scores = {}

    for model in MODELS:
        try:
            response_emotion = query_llm(text, model, lang)
            emotion_list = [e.strip() for e in response_emotion.split(",")]

            if len(emotion_list) > 1:
                category = "смешанная" if lang == "ru" else "mixed"
            else:
                emotion = emotion_list[0]
                category = category_map.get(emotion, "нейтральная" if lang == "ru" else "neutral")

            weight = weights[model].get(category, 0)

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
