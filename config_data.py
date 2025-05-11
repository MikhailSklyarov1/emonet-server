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

emotion_category_map_en = {
    'serenity': 'positive', 'ecstasy': 'positive', 'admiration': 'positive',
    'trust': 'positive', 'interest': 'positive', 'anticipation': 'positive',
    'acceptance': 'positive', 'joy': 'positive',

    'anger': 'negative', 'grief': 'negative', 'sadness': 'negative',
    'annoyance': 'negative', 'rage': 'negative', 'vigilance': 'negative',
    'displeasure': 'negative', 'disgust': 'negative', 'sorrow': 'negative',
    'fear': 'negative', 'anxiety': 'negative', 'terror': 'negative',

    'amazement': 'neutral', 'nothing': 'neutral', 'confusion': 'neutral',
    'boredom': 'neutral', 'surprise': 'neutral'
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

model_weights_en = {
    "deepseek/deepseek-r1-distill-qwen-32b:free": {
        "positive": 0.3,
        "negative": 0.3,
        "neutral": 0.3,
        "mixed": 0.6,
    },
    "qwen/qwq-32b:free": {
        "positive": 0.2,
        "negative": 0.2,
        "neutral": 0.2,
        "mixed": 0.5,
    },
    "mistralai/mistral-small-3.1-24b-instruct:free": {
        "positive": 0.6,
        "negative": 0.7,
        "neutral": 0.8,
        "mixed": 0.9,
    },
}

emotions_list_by_lang = {
    "ru": [
        'безмятежность', 'восторг', 'восхищение', 'гнев', 'горе', 'грусть',
        'доверие', 'досада', 'злость', 'изумление', 'интерес', 'настороженность',
        'неудовольствие', 'ничего', 'ожидание', 'отвращение', 'печаль',
        'принятие', 'радость', 'растерянность', 'скука', 'страх', 'тревога',
        'удивление', 'ужас'
    ],
    "en": [
        'serenity', 'ecstasy', 'admiration', 'anger', 'grief', 'sadness',
        'trust', 'annoyance', 'rage', 'amazement', 'interest', 'vigilance',
        'displeasure', 'nothing', 'anticipation', 'disgust', 'sorrow',
        'acceptance', 'joy', 'confusion', 'boredom', 'fear', 'anxiety',
        'surprise', 'terror'
    ]
}

MODELS = [
    "deepseek/deepseek-r1-distill-qwen-32b:free",
    "qwen/qwq-32b:free",
    "mistralai/mistral-small-3.1-24b-instruct:free",
]