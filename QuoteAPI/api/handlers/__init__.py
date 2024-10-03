from api import app
from flask import jsonify
from werkzeug.exceptions import HTTPException


def validate(in_data, method='post'):
    rating = in_data.setdefault('rating', 1)
    if rating not in range(1, 6) and method == 'post':
        in_data['rating'] = 1
    elif rating not in range(1, 6) and method == 'put':
        in_data.pop('rating')
    in_data.setdefault('text', 'Quote is text')
    return in_data


@app.errorhandler(HTTPException)
def handle_exeption(e):
    """Функция для перехвата HTTP ошибок и возврата в виде JSON."""
    return jsonify({"message": str(e)}), e.code