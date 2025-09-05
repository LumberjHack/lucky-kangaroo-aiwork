from flask import Blueprint
from flask_restx import Api, Resource

api_blueprint = Blueprint("api", __name__)
api = Api(api_blueprint, version="1.0", title="Lucky Kangaroo API", doc="/")

ns = api.namespace("ping", description="health")
@ns.route("/")
class Ping(Resource):
    def get(self):
        return {"pong": True}
