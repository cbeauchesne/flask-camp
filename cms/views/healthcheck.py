from cms.views.core import BaseResource
from cms.decorators import allow_anonymous


class HealthCheckView(BaseResource):
    @allow_anonymous
    def get(self):
        return {"status": "ok"}
