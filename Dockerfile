FROM python:3.9-slim

WORKDIR /app

COPY . /app

RUN python -m venv /venv
RUN /venv/bin/pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y supervisor

EXPOSE 8000

ENV PATH="/venv/bin:$PATH"

CMD ["/usr/bin/supervisord"]
