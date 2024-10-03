from typing import Any
from flask import Flask, jsonify, request, abort
from http import HTTPStatus
from pathlib import Path
from werkzeug.exceptions import HTTPException
# imports for sqlalchemy
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, func, ForeignKey
from sqlalchemy.exc import InvalidRequestError
from flask_migrate import Migrate


class Base(DeclarativeBase):
    pass


BASE_DIR = Path(__file__).parent

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{BASE_DIR / 'quotes.db'}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(model_class=Base)
db.init_app(app)
migrate = Migrate(app, db)



class AuthorModel(db.Model):
    __tablename__ = 'authors'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[int] = mapped_column(String(32), index= True, unique=True)
    quotes: Mapped[list['QuoteModel']] = relationship(back_populates='author', lazy='dynamic')

    def __init__(self, name):
        self.name = name

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
            }


class QuoteModel(db.Model):
    __tablename__ = 'quotes'

    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[str] = mapped_column(ForeignKey('authors.id'))
    author: Mapped['AuthorModel'] = relationship(back_populates='quotes')
    text: Mapped[str] = mapped_column(String(255))
    rating: Mapped[int] = mapped_column(server_default='1')

    def __init__(self, author, text):
        self.author = author
        self.text  = text


    def to_dict(self):
        return {
            "id": self.id,
            "text": self.text
        }

@app.errorhandler(HTTPException)
def handle_exeption(e):
    """Функция для перехвата HTTP ошибок и возврата в виде JSON."""
    return jsonify({"message": str(e)}), e.code



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
    quote = db.get_or_404(quote_id)
    return jsonify(quote.to_dict()), HTTPStatus.OK


@app.get("/quotes/count")
def quotes_count():
    """Function to count all quotes."""
    count = db.session.scalar(func.count(QuoteModel.id))
    return jsonify(count=count), 200



@app.route("/quotes", methods=['POST'])
def create_quote():
    data = request.json

    if "rating" not in data or not data["rating"] in range(1, 6):
        data["rating"] = 1

    try:
        quote = QuoteModel(**data)
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

    data: dict = request.json
    if "rating" in data and not data["rating"] in range(1, 6):
        data.pop("rating")
    if len(data) == 0:
        return "No valid data to update", HTTPStatus.BAD_REQUEST

    try:
        for key, value in data.items():
            if not hasattr(quote, key):
                raise Exception(f"Invalid key: {key}. Valid: author, text, rating")
            setattr(quote, key, value)
        db.session.commit()
        return quote.to_dict()
    except Exception as e:
        return str(e), HTTPStatus.BAD_REQUEST


@app.route("/quotes/<int:quote_id>", methods=["DELETE"])
def delete_quote(quote_id: int):
    quote = db.get_or_404(QuoteModel, quote_id)
    db.session.delete(quote)
    try:
        db.session.commit()
        return f"Quote with id {id} deleted"
    except Exception as e:
        db.session.rollback()
        abort(503, f"Database error: {str(e)}")


@app.route("/quotes/filter")
def filter_quotes():
    """DONE: change to work with database."""
    try:
        quotes = db.session.scalars(QuoteModel).filter_by(**request.args).all()
    except InvalidRequestError:
        return (
            (
                "Invalid data. Possible keys: author, text, rating. "
                f"Received: {', '.join(request.args.keys())}"
            ),
            HTTPStatus.BAD_REQUEST,
        )

    return jsonify([quote.to_dict() for quote in quotes]), 200


if __name__ == "__main__":
   app.run(debug=True, port=5000)