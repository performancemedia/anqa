import typer

cli = typer.Typer()


@cli.command(help="Show hello message")
def hello():
    typer.secho("Hello", fg="green")


@cli.command(help="Create new Anqa project")
def new():
    typer.secho("Creating new...", fg="green")
