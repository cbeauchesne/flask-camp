from flask_restful import Resource
from werkzeug.exceptions import NotFound

from cms import database
from cms.decorators import moderator_required
from cms.models.user import User as UserModel


class BlockUserView(Resource):
    @moderator_required
    def put(self, id):

        user = UserModel.get(id=id)

        if not user:
            raise NotFound()

        user.blocked = True
        database.session.commit()

        return {"status": "ok"}

    @moderator_required
    def delete(self, id):
        user = UserModel.get(id=id)

        if not user:
            raise NotFound()

        user.blocked = False
        database.session.commit()

        return {"status": "ok"}
