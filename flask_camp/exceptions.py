from werkzeug.exceptions import Conflict


class ConfigurationError(Exception):
    pass


class EditConflict(Conflict):
    def __init__(self, your_version, last_version):
        super().__init__("A new version exists")
        self.data = {
            "last_version": last_version,
            "your_version": your_version,
        }
