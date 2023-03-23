import json
import os
import subprocess  # nosec


def call_command(*args, **kwargs):  # nosec
    subprocess.run(*args, **kwargs)


def get_context():
    context_str = r"""
    {{ cookiecutter | jsonify }}
    """
    return json.loads(context_str)


def remove_paths(paths: list):
    base_dir = os.getcwd()
    for path in paths:
        path = os.path.join(base_dir, path)
        if path and os.path.exists(path):
            if os.path.isdir(path):
                os.rmdir(path)
            else:
                os.unlink(path)
