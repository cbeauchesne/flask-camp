from cms.application import Application


def create_app(**kwargs):
    app = Application()

    app.config.from_object(kwargs)

    return app
