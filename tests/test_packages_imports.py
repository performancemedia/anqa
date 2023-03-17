from pydantic import BaseModel


def test_core_import():
    from anqa.core.schema import BaseSchema

    assert issubclass(BaseSchema, BaseModel)


def test_rest_package_import():
    from anqa.rest.factory import create_fastapi_app

    assert callable(create_fastapi_app)
