from anqa.rest.routers import ViewRouter

from .views import FeatureViews

router = ViewRouter(prefix="/{{cookiecutter.name}}")

router.register_view(FeatureViews)
