# Use an official Python runtime as the parent image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . .

# Install Chrome, wget, gnupg2, and curl
RUN apt-get update && apt-get install -y --fix-missing \
    wget \
    gnupg2 \
    curl \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' \
    && apt-get update \
    && apt-get install -y google-chrome-stable


# Install ChromeDriver
RUN CHROME_DRIVER_VERSION=`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE` && \
    wget -N http://chromedriver.storage.googleapis.com/$CHROME_DRIVER_VERSION/chromedriver_linux64.zip -P ~/ && \
    unzip ~/chromedriver_linux64.zip -d ~/ && \
    rm ~/chromedriver_linux64.zip && \
    mv -f ~/chromedriver /usr/local/bin/chromedriver && \
    chown root:root /usr/local/bin/chromedriver && \
    chmod 0755 /usr/local/bin/chromedriver

# Install Python packages from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable for Flask to run in production
ENV FLASK_ENV=production

# Run app.py when the container launches
CMD ["flask", "run", "--host=0.0.0.0"]
