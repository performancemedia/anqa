import os
from typing import Any

import typer
from cookiecutter.exceptions import OutputDirExistsException
from cookiecutter.main import cookiecutter

TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "templates")


def fill_template(template_name: str, context: dict[str, Any]):
    try:
        cookiecutter(
            os.path.join(TEMPLATES_DIR, template_name),
            extra_context=context,
            no_input=True,
        )
    except OutputDirExistsException:
        typer.echo(f"Folder {context['name']} already exists. 😞")
    else:
        typer.echo(f"FastAPI {template_name} created successfully! 🎉")
