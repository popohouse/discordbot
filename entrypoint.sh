#!/bin/sh

eval "$(ssh-agent -s)"

git pull https://github.com/unknownpopo/discordbot.git

pip install --no-cache-dir -r requirements.txt

exec python -u index.py