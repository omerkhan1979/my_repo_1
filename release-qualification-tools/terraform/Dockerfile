FROM python:3.10.9-slim As compiled-image

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
COPY . /rq

RUN pip install -U pip \
    && apt-get update \
    && apt install -y curl netcat \
   && pip3 install poetry\
    && cd /rq \
    && poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi


FROM compiled-image
COPY --from=compiled-image /rq /rq
WORKDIR /rq
CMD ["uvicorn", "services.rq_service:app", "--host", "0.0.0.0", "--port", "8000"]