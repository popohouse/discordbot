FROM python:3.10-alpine
LABEL maintainer="AlexFlipnote <root@alexflipnote.dev>"

LABEL build_date="2022-04-25"
RUN apk update && apk upgrade
RUN apk add --no-cache git make build-base linux-headers openssh-client
WORKDIR /discord_bot
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

# Copy SSH private key into container
ARG SSH_PRIVATE_KEY
RUN mkdir /root/.ssh/
RUN echo "${SSH_PRIVATE_KEY}" > /root/.ssh/id_rsa
RUN chmod 600 /root/.ssh/id_rsa

# Set up SSH agent
RUN eval "$(ssh-agent -s)"
RUN ssh-add /root/.ssh/id_rsa

# Copy entrypoint script into container
COPY entrypoint.sh /entrypoint.sh

# Set entrypoint script as entrypoint
ENTRYPOINT ["/entrypoint.sh"]