from typing import Any, Optional

from anqa.rest.views.views import L
from anqa.rest.views.viewsets import APIViewSet


class FeatureViews(APIViewSet):
    async def list(self, *args, **kwargs) -> L:
        pass

    async def create(self, *args, **kwargs) -> Any:
        pass

    async def retrieve(self, *args, **kwargs) -> Optional[Any]:
        pass

    async def update(self, *args, **kwargs):
        pass

    async def destroy(self, *args, **kwargs) -> None:
        pass
