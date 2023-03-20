from typing import Dict, List, Union

from fastapi import APIRouter
from pydantic import PyObject

from anqa.core.abc.service import AbstractSideService
from anqa.core.settings import AppSettings
from anqa.core.utils.imports import ImportedType


class ApiSettings(AppSettings):
    tags_metadata: Union[PyObject, Dict[str, str]] = {}
    side_services: List[AbstractSideService] = []
    routers: List[ImportedType[APIRouter]] = []
