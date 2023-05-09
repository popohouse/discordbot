FROM python:3.10-alpine
LABEL maintainer="UnknownPopo <admin@popo.house>"

LABEL build_date="2023-05-09"
RUN apk update && apk upgrade
RUN apk add --no-cache git make build-base linux-headers libpq-dev
WORKDIR /discord_bot
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "-u", "index.py"]
