from typing import Dict, List, Union

from fastapi import APIRouter
from pydantic import PyObject

from anqa.core.abc.service import AbstractSideService
from anqa.core.settings import AppSettings
from anqa.core.utils.imports import ImportedType


class ApiSettings(AppSettings):
    routers: List[Union[APIRouter, PyObject]] = []
    tags_metadata: Union[ImportedType, Dict[str, str]] = {}
    side_services: List[AbstractSideService] = []
