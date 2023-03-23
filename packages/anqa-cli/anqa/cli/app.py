from typing import Optional

import typer
from questionary.form import form

from ._version import __version__
from .enum import CreateEnum, PackageEnum, PythonVersion, YesNoEnum
from .generator import fill_template
from .helpers import binary_question, question
from .utils import call_command

cli = typer.Typer(
    add_completion=True,
    help=f"Boostrap Anqa based projects in seconds! v{__version__}",
    name="Anqa CLI",
)


@cli.command(help="Show hello message")
def hello():
    typer.secho("Hello", fg="green")


@cli.command(help="Create new Anqa project")
def startproject(
    project: str,
    interactive: YesNoEnum = typer.Option(
        YesNoEnum.yes, help="Run in interactive mode"
    ),
    docker: YesNoEnum = typer.Option(YesNoEnum.yes),
    pre_commit: YesNoEnum = typer.Option(YesNoEnum.yes, "--pre-commit"),
    python: PythonVersion = typer.Option(PythonVersion.PY3_11),
    taskfile: YesNoEnum = typer.Option(YesNoEnum.yes),
):
    typer.secho("Creating new...", fg="green")
    if interactive:
        result = form(
            python=question(PythonVersion),
            pre_commit=binary_question("pre commit"),
            docker=binary_question("docker"),
            taskfile=binary_question("taskfile"),
        ).ask()
        context = dict(name=project, **result)
    else:
        context = dict(
            name=project,
            python=python,
            pre_commit=pre_commit,
            docker=docker,
            taskfile=taskfile,
        )
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
    if extras:
        command.append(f"'{package}[{extras}]'")
    else:
        command.append(package)

    for cmd in (command, ["poetry", "lock"], ["poetry", "install"]):
        call_command(cmd)

    typer.secho(f"Successfully installed {package.value}")
