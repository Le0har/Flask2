from api import ma
from marshmallow import EXCLUDE
from api.models.quote import QuoteModel
from api.schemas.author import AuthorSchema


def rating_validate(value):
    return value in range(1,6)


class QuoteSchema(ma.SQLAlchemySchema):
    class Meta:
        model = QuoteModel
        unknown = EXCLUDE

    id = ma.auto_field()
    text = ma.auto_field()
    author = ma.Nested(AuthorSchema())
    author_id = ma.auto_field()
    rating = ma.Integer(strict=True, validate=rating_validate)


quote_schema = QuoteSchema(exclude=['author_id'])
quotes_schema = QuoteSchema(many=True, exclude=['author'])
quote_without_rating = QuoteSchema(exclude=['rating'])
