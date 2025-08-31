from marshmallow import Schema, fields

class ListingSchema(Schema):
    id = fields.Int()
    uuid = fields.Str()
    title = fields.Str()
    description = fields.Str()
    category = fields.Str(allow_none=True)
    subcategory = fields.Str(allow_none=True)
    brand = fields.Str(allow_none=True)
    estimated_value = fields.Float(allow_none=True)
    ai_estimated_value = fields.Float(allow_none=True)
    ai_confidence = fields.Float(allow_none=True)
    latitude = fields.Float(allow_none=True)
    longitude = fields.Float(allow_none=True)
    status = fields.Str()
