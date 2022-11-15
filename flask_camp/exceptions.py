from werkzeug.exceptions import Conflict, BadRequest


class ConfigurationError(Exception):
    pass


class EditConflict(Conflict):
    def __init__(self, your_version, last_version):
        super().__init__("A new version exists")
        self.data = {
            "last_version": last_version,
            "your_version": your_version,
        }


class CantHideLastVersion(BadRequest):
    def __init__(self) -> None:
        super().__init__("The last version of a document cannot be hidden")


class CantDeleteLastVersion(BadRequest):
    def __init__(self) -> None:
        super().__init__("The last version of a document cannot be deleted")
