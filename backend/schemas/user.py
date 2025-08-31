from marshmallow import Schema, fields

class UserSchema(Schema):
    id = fields.Int()
    uuid = fields.Str()
    email = fields.Email()
    first_name = fields.Str()
    last_name = fields.Str()
    city = fields.Str()
    latitude = fields.Float(allow_none=True)
    longitude = fields.Float(allow_none=True)
    trust_score = fields.Int()
