from werkzeug.exceptions import NotFound

from cms import database
from cms.decorators import allow_moderator
from cms.models.user import User as UserModel
from cms.views.core import BaseResource


class BlockUserView(BaseResource):
    @allow_moderator
    def put(self, id):

        user = UserModel.get(id=id)

        if not user:
            raise NotFound()

        user.blocked = True
        database.session.commit()

        return {"status": "ok"}

    @allow_moderator
    def delete(self, id):
        user = UserModel.get(id=id)

        if not user:
            raise NotFound()

        user.blocked = False
        database.session.commit()

        return {"status": "ok"}
