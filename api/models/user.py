from sqlalchemy import Column
from sqlalchemy import Text

from cms.models.user import User as BaseUser


class User(BaseUser):
    ui_preferences = Column(Text)

    @classmethod
    def get_dict_columns(cls):
        return (cls.id, cls.username, cls.email, cls.ui_preferences)
