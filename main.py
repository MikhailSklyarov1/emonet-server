from flask import Flask, request, jsonify
from flask_cors import CORS
import httpx
import asyncio
import json
import os
from config_data import (
    emotion_category_map,
    emotion_category_map_en,
    model_weights,
    model_weights_en,
    emotions_list_by_lang,
    MODELS,
)

app = Flask(__name__)
CORS(app)

API_KEY = os.getenv("API_KEY")
API_URL = "https://openrouter.ai/api/v1/chat/completions"


def build_prompt_and_messages(text: str, lang: str) -> tuple[str, list]:
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

    return system_msg, [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": prompt},
        {"role": "user", "content": user_msg},
    ]


async def query_llm(text: str, model: str, lang: str) -> str:
    system_msg, messages = build_prompt_and_messages(text, lang)

    payload = {
        "model": model,
        "messages": messages,
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(API_URL, headers=headers, json=payload, timeout=60)

    if response.status_code == 200:
        result = response.json()["choices"][0]["message"]["content"].strip().lower()
        print("Ответ модели", model, ":", result)
        return result
    else:
        raise Exception(response.text)


async def get_emotion_from_model(text: str, model: str, lang: str, category_map: dict) -> dict:
    emotion = await query_llm(text, model, lang)
    return {
        "emotion": emotion,
        "votes": [
            {
                "model": model,
                "emotion": emotion,
                "category": category_map.get(emotion, "neutral" if lang == "en" else "нейтральная"),
                "weight": "-",
            }
        ],
    }


async def get_emotion_voting(text: str, lang: str, category_map: dict, weights: dict) -> dict:
    scores = {}
    votes = []

    async def get_vote(model: str):
        try:
            response_emotion = await query_llm(text, model, lang)
            emotion_list = [e.strip() for e in response_emotion.split(",")]

            if len(emotion_list) > 1:
                category = "mixed" if lang == "en" else "смешанная"
            else:
                emotion = emotion_list[0]
                category = category_map.get(emotion, "neutral" if lang == "en" else "нейтральная")

            weight = weights[model].get(category, 0)

            for em in emotion_list:
                scores[em] = scores.get(em, 0) + weight

            return {
                "model": model,
                "emotion": response_emotion,
                "category": category,
                "weight": weight,
            }
        except Exception as e:
            print(f"Ошибка при запросе к {model}: {e}")
            return None

    tasks = [get_vote(model) for model in MODELS]
    results = await asyncio.gather(*tasks)

    for vote in results:
        if vote:
            votes.append(vote)

    if not scores:
        raise Exception("Не удалось определить эмоции")

    best_emotion = max(scores.items(), key=lambda kv: kv[1])[0]

    return {
        "emotion": best_emotion,
        "votes": votes,
    }


def validate_request_data(data: dict) -> tuple[str, str]:
    text = data.get("text")
    selected_model = data.get("model")
    if not text or not selected_model:
        raise ValueError("Некорректный запрос")
    return text, selected_model


@app.route("/api/emotion", methods=["POST"])
async def detect_emotion():
    try:
        data = request.get_json()
        text, selected_model = validate_request_data(data)
        lang = data.get("lang", "ru")

        category_map = emotion_category_map if lang == "ru" else emotion_category_map_en
        weights = model_weights if lang == "ru" else model_weights_en

        if selected_model != "voting":
            result = await get_emotion_from_model(text, selected_model, lang, category_map)
        else:
            result = await get_emotion_voting(text, lang, category_map, weights)

        return jsonify(result)

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    import os
    import sys

    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    app.run(debug=True)
