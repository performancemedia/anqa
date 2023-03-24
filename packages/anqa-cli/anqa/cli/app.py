from typing import Optional

import typer
from questionary.form import form

from ._version import __version__
from .enum import CreateEnum, PackageEnum, Python, StrEnum
from .generator import fill_template
from .helpers import binary_question, question
from .utils import call_command

cli = typer.Typer(
    add_completion=True,
    help="Boostrap Anqa based projects in seconds!",
    name="Anqa CLI",
)


@cli.command(help="Show hello message")
def version():
    typer.secho(f"Anqa CLI v{__version__}", fg="green")


@cli.command(help="Create new Anqa project")
def startproject(
    project: str,
    interactive: bool = typer.Option(True, help="Run in interactive mode"),
    docker: bool = typer.Option(True),
    pre_commit: bool = typer.Option(True, "--pre-commit"),
    python: Python = typer.Option(Python.v3_11),
    taskfile: bool = typer.Option(True),
    alembic: bool = typer.Option(True),
):
    typer.secho("Creating new...", fg="green")
    if interactive:
        result = form(
            python=question(Python),
            pre_commit=binary_question("pre commit"),
            docker=binary_question("docker"),
            taskfile=binary_question("taskfile"),
            alembic=binary_question("alembic"),
        ).ask()
        context = dict(name=project, **result)
    else:
        context = dict(
            name=project,
            python=python,
            pre_commit=pre_commit,
            docker=docker,
            taskfile=taskfile,
            alembic=alembic,
        )
    for k, v in context.items():
        if isinstance(v, StrEnum):
            context[k] = str(v.value)
    fill_template("project", context)


@cli.command(help="Create new app/api/service")
def new(kind: CreateEnum, name: str):
    return fill_template(kind.value, {"name": name})


@cli.command(help="Add anqa package")
def add(
    package: PackageEnum,
    extras: Optional[str] = typer.Option(None, "--extras"),
):
    command = ["poetry", "add"]
    package_name = f"anqa-{package.value}"
    if extras:
        command.append(f"'{package_name}[{extras}]'")
    else:
        command.append(package_name)

    for cmd in (command, ["poetry", "lock"], ["poetry", "install"]):
        call_command(cmd)

    typer.secho(f"Successfully installed {package_name}")
