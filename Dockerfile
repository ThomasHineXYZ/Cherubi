FROM python:3.9-buster

RUN apt-get update && \
    apt-get -y install build-essential

# Add the bot files to the home folder
ADD . .
ADD docker/launch-bot.sh .

# Map /config to host defined config path (used to store configurations)
VOLUME /config

# Install the required Python libraries
RUN pip install --no-cache-dir -r requirements.txt

# Run the bot
CMD ["/bin/bash", "launch-bot.sh"]
