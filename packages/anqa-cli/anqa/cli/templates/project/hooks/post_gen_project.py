from anqa.cli.utils import call_command, remove_paths


def main():
    pre_commit = eval("{{ cookiecutter.pre_commit }}")  # nosec
    if pre_commit:
        call_command(["pre-commit", "install"])
    else:
        remove_paths([".pre-commit-config.yaml"])
    alembic_enabled = eval("{{ cookiecutter.alembic }}")  # nosec
    if not alembic_enabled:
        remove_paths(["alembic.ini", "migrations"])
    else:
        call_command(["anqa", "add", "db"])
    docker = eval("{{ cookiecutter.docker }}")  # nosec
    if not docker:
        remove_paths(["Dockerfile", "docker-compose.yaml"])
    taskfile = eval("{{cookiecutter.taskfile}}")  # nosec
    if not taskfile:
        remove_paths(["Taskfile.yml"])


if __name__ == "__main__":
    main()
