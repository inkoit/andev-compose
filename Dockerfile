FROM python:3.10

WORKDIR /code/
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

COPY ./pyproject.toml ./poetry.lock* /code/
RUN poetry install

COPY . /code
ENV PYTHONPATH=/code
