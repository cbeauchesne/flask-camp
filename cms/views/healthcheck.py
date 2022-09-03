from flask_restful import Resource


class HealthCheckView(Resource):
    def get(self):
        return {"status": "ok"}
