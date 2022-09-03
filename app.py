from cms.application import Application


def create_app(**kwargs):
    app = Application(**kwargs)

    return app
