#!/bin/bash

if [ $BOT ]; then
    sed -i "s/BOT_TOKEN/$BOT/g" /app/config.ini
fi

if [ $USER ]; then
    sed -i "s/UID/$USER/g" /app/config.ini
fi

if [ $SERVER ]; then
    sed -i "s~EMBY_SERVER~$SERVER~g" /app/config.ini
fi

if [ $API ]; then
    sed -i "s/EMBY_API_KEY/$API/g" /app/config.ini
fi



/app/main.py