from marshmallow import ValidationError
from api import db, app, multi_auth
from api.models.quote import QuoteModel
from api.models.author import AuthorModel
from typing import Any
from flask import jsonify, abort, request
from . import validate
from sqlalchemy.exc import InvalidRequestError
from http import HTTPStatus
from sqlalchemy import func
from api.schemas.quote import quote_schema, quotes_schema, quote_without_rating


# URL: /quotes
@app.route("/quotes")
def get_quotes() -> list[dict[str, Any]]:
    """ Функция неявно преобразовывает список словарей в JSON."""
    quotes_db = db.session.scalars(db.select(QuoteModel)).all()
    return jsonify(quotes_schema.dump(quotes_db)), 200


# URL: /authors/1/quotes
@app.route("/authors/<int:author_id>/quotes")
def get_author_quotes(author_id):
    """ Функция неявно преобразовывает список словарей в JSON."""
    author = db.session.get(AuthorModel, author_id)
    quotes = []
    for quote in author.quotes:
        quotes.append(quote)
    
    return jsonify(quotes_schema.dump(quotes)), 200


@app.route("/quotes/<int:quote_id>")
def get_quote(quote_id: int) -> dict:
    """ Функция возвращает цитату по значению ключа id=quote_id."""
    quote = db.get_or_404(QuoteModel, quote_id)
    return jsonify(quote_schema.dump(quote)), HTTPStatus.OK


@app.route("/authors/<int:author_id>/quotes", methods=['POST'])
@multi_auth.login_required
def create_quote(author_id):
    try:
        data = quote_schema.loads(request.data)
    except ValidationError as ve:
        abort(400, f'Validation error: {str(ve)}')
        
    author = db.get_or_404(AuthorModel, author_id)

    try:
        quote = QuoteModel(author, **data)
        db.session.add(quote)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        abort(503, f"Database error: {str(e)}")
    return quote_schema.dump(quote), HTTPStatus.CREATED


@app.route("/quotes/<int:quote_id>", methods=["PUT"])
def edit_quote(quote_id):
    quote: QuoteModel = db.get_or_404(QuoteModel, quote_id)

    try:
        data = quote_schema.loads(request.data)
    except ValidationError as ve:
        data = quote_without_rating(request.data)

        for key, value in data.items():
            setattr(quote, key, value)

    try:    
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        abort(503, f'Database error: {str(e)}')

    return jsonify(quote_schema.dump(quote)), 200


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
                f"Received: {', '.join(data.keys())}"
            ),
            HTTPStatus.BAD_REQUEST,
        )
    except Exception as e:
        abort(503, f'Database error: {str(e)}')
    return jsonify(quotes_schema.dump(quotes)), 200
