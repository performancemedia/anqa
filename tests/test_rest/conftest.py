import pytest
from fastapi import FastAPI


@pytest.fixture
def fastapi_app():
    return FastAPI()
