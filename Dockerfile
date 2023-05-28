FROM python:3.10-slim-buster
LABEL maintainer="UnknownPopo <admin@popo.house>"
LABEL build_date="2023-05-09"

RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y git make build-essential libpq-dev libffi-dev

WORKDIR /discord_bot
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "-u", "index.py"]