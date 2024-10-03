from api import db, app
from api.models.quote import QuoteModel
from api.models.author import AuthorModel
from typing import Any
from flask import jsonify, abort, request
from . import validate
from sqlalchemy.exc import InvalidRequestError
from http import HTTPStatus
from sqlalchemy import func


# URL: /quotes
@app.route("/quotes")
def get_quotes() -> list[dict[str, Any]]:
    """ Функция неявно преобразовывает список словарей в JSON."""
    quotes_db = db.session.scalars(db.select(QuoteModel)).all()
    quotes = []
    for quote in quotes_db:
        quotes.append(quote.to_dict())
    return jsonify(quotes), 200


# URL: /authors/1/quotes
@app.route("/authors/<int:author_id>/quotes")
def get_author_quotes(author_id):
    """ Функция неявно преобразовывает список словарей в JSON."""
    author = db.session.get(AuthorModel, author_id)
    quotes = []
    for quote in author.quotes:
        quotes.append(quote.to_dict())
    
    return jsonify(author=author.to_dict() | {"quotes": quotes}), 200


@app.route("/quotes/<int:quote_id>")
def get_quote(quote_id: int) -> dict:
    """ Функция возвращает цитату по значению ключа id=quote_id."""
    quote = db.get_or_404(QuoteModel, quote_id)
    return jsonify(quote.to_dict()), HTTPStatus.OK


@app.route("/authors/<int:author_id>/quotes", methods=['POST'])
def create_quote(author_id):
    raw_data = request.json
    data = validate(raw_data)
    author = db.get_or_404(AuthorModel, author_id)
    try:
        quote = QuoteModel(author, **data)
        db.session.add(quote)
        db.session.commit()
    except Exception as e:
        abort(503, f"error: {str(e)}")
    except TypeError:
        return (
            (
                "Invalid data. Required: author, text, rating (optional). "
                f"Received: {', '.join(data.keys())}"
            ),
            HTTPStatus.BAD_REQUEST,
        )

    return quote.to_dict(), HTTPStatus.CREATED


@app.route("/quotes/<int:quote_id>", methods=["PUT"])
def edit_quote(quote_id):
    quote: QuoteModel = db.get_or_404(QuoteModel, quote_id)

    raw_data: dict = request.json
    data = validate(raw_data)

    if len(data) == 0:
        return "No valid data to update", HTTPStatus.BAD_REQUEST

    try:
        for key, value in data.items():
            if not hasattr(quote, key):
                raise Exception(f"Invalid key: {key}. Valid: author, text, rating")
            setattr(quote, key, value)
        db.session.commit()
        return quote.to_dict(), 200
    except Exception as e:
        return str(e), HTTPStatus.BAD_REQUEST


@app.route("/quotes/<int:quote_id>", methods=["DELETE"])
def delete_quote(quote_id: int):
    quote = db.get_or_404(QuoteModel, quote_id)
    db.session.delete(quote)
    try:
        db.session.commit()
        return f"Quote with id {quote_id} deleted"
    except Exception as e:
        db.session.rollback()
        abort(503, f"Database error: {str(e)}")


@app.get("/quotes/count")
def quotes_count():
    """Function to count all quotes."""
    count = db.session.scalar(func.count(QuoteModel.id))
    return jsonify(count=count), 200


@app.route("/quotes/filter")
def filter_quotes():
    try:
        data = request.args.copy()
        quotes = db.session.execute(db.select(QuoteModel).filter_by(**data)).scalars()
    except InvalidRequestError:
        return (
            (
                "Invalid data. Possible keys: author, text, rating. "
                f"Received: {', '.join(request.args.keys())}"
            ),
            HTTPStatus.BAD_REQUEST,
        )
    except Exception as e:
        abort(503, f'Database error: {str(e)}')
    return jsonify([quote.to_dict() for quote in quotes]), 200
