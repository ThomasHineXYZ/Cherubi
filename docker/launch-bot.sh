#!/usr/bin/env bash

# Checks if the file is present. If it is, copy it
if [ ! -e "/config/.env.local" ]; then
    echo "Copying a blank local env file to config"

    # Copy the file over to the config directory
    cp "./.env.local.example" "/config/.env.local"
fi

# Fix permission issues
echo "Fixing potential config file permission issues"
chown -R 99:100 "/config"
chmod -R 777 "/config"

# Symbolic link the config folder files
if [ ! -e "./.env.local" ]; then
    echo "Linking the config files to the current directory"

    # Copy the file over to the config directory
    ln -s "/config/.env.local" "./.env.local"
fi

# Then finally start the bot
python bot
