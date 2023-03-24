ARG WORKDIR=/app

FROM python:{{cookiecutter.python}}-slim AS python-base
ARG WORKDIR


ARG USERNAME=appuser
ARG USER_UID=1000
ARG USER_GID=$USER_UID

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV POETRY_VERSION 1.4.0
ENV POETRY_VIRTUALENVS_IN_PROJECT true

WORKDIR $WORKDIR

RUN apt-get update && apt-get install -y curl \
    && rm -rf /var/lib/apt/lists/*

RUN adduser -u $USER_UID --disabled-password --gecos "" $USERNAME && chown -R $USERNAME $WORKDIR
USER $USERNAME
ENV PATH /app/.venv/bin:$PATH:/home/$USERNAME/.local/bin

RUN pip install --user -U pip
RUN curl -sSL https://install.python-poetry.org | python3 -

COPY ./poetry.lock ./pyproject.toml ./

RUN poetry install --only main

FROM python-base AS {{cookiecutter.name}}-dev

COPY --from=python-base /app /app
COPY ./{{cookiecutter.name}} .

EXPOSE 8000
# CMD ["uvicorn", "{{cookiecutter.name}}.api.asgi:app", "--host", "0.0.0.0", "--port", "8000", "--http", "h11", "--log-level", "info"]


FROM {{cookiecutter.name}}-dev AS {{cookiecutter.name}}-test

COPY --from=python-base /app /app
COPY .flake8 ./tests ./

RUN poetry install --all-extras