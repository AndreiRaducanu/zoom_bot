# Use official Python image
FROM python:3.12-slim

# Install necessary dependencies including Chrome's required libraries
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    gnupg \
    # Chrome dependencies
    libglib2.0-0 \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libcairo2 \
    && rm -rf /var/lib/apt/lists/*

# Download and install Chrome
RUN wget https://storage.googleapis.com/chrome-for-testing-public/134.0.6998.165/linux64/chrome-linux64.zip && \
    unzip chrome-linux64.zip -d /opt && \
    rm chrome-linux64.zip && \
    ln -s /opt/chrome-linux64/chrome /usr/local/bin/chrome

# Download and install ChromeDriver
RUN wget https://storage.googleapis.com/chrome-for-testing-public/134.0.6998.165/linux64/chromedriver-linux64.zip && \
    unzip chromedriver-linux64.zip -d /opt && \
    rm chromedriver-linux64.zip && \
    ln -s /opt/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver

# Verify installations
RUN chrome --version && chromedriver --version

# Install Python dependencies
RUN pip install --upgrade pip \
    && pip install selenium \
    && pip install poetry

WORKDIR /app

COPY . /app

# When container starts, just run bash
CMD ["/bin/bash"]