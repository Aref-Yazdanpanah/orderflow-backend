from rest_framework import routers


class ExtendableRouter(routers.DefaultRouter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trailing_slash = "/?"

    def extend(self, router):
        self.registry.extend(router.registry)
