# ZoomBot - Automated Zoom Meeting Joiner 🤖

**I recommend using this bot with Amazon EC2 and scheduling it with the EC2 instance scheduler + cron jobs to fully automate the Zoom meeting joining process.**

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/Docker-✓-blue.svg" alt="Docker">
  <img src="https://img.shields.io/badge/Selenium-Chromium-green.svg" alt="Selenium">
</p>

## 📌 Table of Contents
- Features
- Requirements
- Installation
- Configuration
- Usage

## ✨ Features
- Auto-joins Zoom meetings via the web client
- Headless Chrome browser support
- Docker containerization for easy setup and portability
- Environment variable configuration for flexibility
- EC2 optimized for seamless cloud deployment

## 📋 Requirements
- Docker 

## 🚀 Installation

1. **Clone the repository**:
    ```bash
    git clone https://github.com/AndreiRaducanu/zoom_bot.git
    cd zoom_bot
    ```

2. **Create your environment file (`.env`)**:
    ```bash
    cat > .env <<EOL
    ZOOM_USERNAME=YourDisplayName
    ZOOM_MEETING_ID=1234567890
    ZOOM_MEETING_PASSWORD=SecretPass
    EOL
    ```

3. **Build the Docker image**:
    ```bash
    docker build -t zoom_bot .
    ```

## ⚙️ Configuration

### Required Environment Variables
| Variable             | Example             | Description                             |
|----------------------|---------------------|-----------------------------------------|
| `ZOOM_USERNAME`       | "John Doe"          | Your display name                       |
| `ZOOM_MEETING_ID`     | "123456789"         | 9-11 digit Zoom meeting ID              |
| `ZOOM_MEETING_PASSWORD`| "Secret123"        | Zoom meeting passcode                   |

## 💻 Usage

### Basic Execution
Run the bot with the environment file:
```bash
docker run --env-file .env --rm zoom_bot
