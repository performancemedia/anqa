from anqa.cli.utils import call_command, remove_paths


def main():
    pre_commit = "{{ cookiecutter.pre_commit }}"
    if pre_commit == "yes":
        call_command(["pre-commit", "install"])
    alembic_enabled = "{{ cookiecutter.alembic }}"
    if alembic_enabled == "no":
        remove_paths(["alembic.ini", "migrations"])
    else:
        call_command(["anqa", "add", "db"])


if __name__ == "__main__":
    main()
