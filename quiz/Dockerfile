FROM python:3.13-alpine3.20

COPY src /app/src
COPY pyproject.toml poetry.lock /app/

WORKDIR /app

ENV PYTHONPATH=/app/src

RUN pip install poetry 
RUN poetry config virtualenvs.create false && \
    poetry install --no-root --no-interaction --no-ansi

WORKDIR /app/src

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]