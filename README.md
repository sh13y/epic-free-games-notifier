# Epic Free Games Notifier

![Build Status](https://img.shields.io/github/actions/workflow/status/sh13y/epic-free-games-notifier/CI.yml)
![License](https://img.shields.io/github/license/sh13y/epic-free-games-notifier)

A Python script with GitHub Actions integration to notify users about free games on the Epic Games Store via email. Because who doesn't love free games? 🎮

## Features

- Fetches free games from the Epic Games Store. (Yes, free as in zero dollars! 💸)
- Sends email notifications with details about the free games. (No spam, we promise! 📧)
- Scheduled to run daily using GitHub Actions. (Set it and forget it! ⏰)

## Prerequisites

- Python 3.x (Python 2.x is so last decade 🕰️)
- GitHub account (You have one, right? 🤔)

## Setup

### 1. Clone the Repository

```sh
git clone https://github.com/your-username/epic-free-games-notifier.git
cd epic-free-games-notifier
```

### 2. Install Dependencies

```sh
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the root directory of the project and add the following environment variables:

```
SMTP_SERVER=your_smtp_server
SMTP_PORT=your_smtp_port
EMAIL=your_email
PASSWORD=your_email_password
TO_EMAIL=recipient_email
FROM_EMAIL=your_from_email
```

### 4. Run the Script Locally

```sh
python check_free_games.py
```

## GitHub Actions Integration

### 1. Add Secrets to GitHub Repository

Go to your GitHub repository, navigate to `Settings > Secrets and variables > Actions`, and add the following secrets:

- `SMTP_SERVER`
- `SMTP_PORT`
- `EMAIL`
- `PASSWORD`
- `TO_EMAIL`
- `FROM_EMAIL`

### 2. Configure GitHub Actions Workflow

The workflow file is located at `notify_free_games.yml`. It is configured to run daily at 12:00 UTC and can also be triggered manually. (Because sometimes you just can't wait for free games! 🎉)

### 3. Enable GitHub Actions

Ensure that GitHub Actions is enabled for your repository. The workflow will automatically run according to the schedule and send email notifications. (Sit back and relax! 🛋️)

## Script Details

The `check_free_games.py` script performs the following steps:

1. **Fetch Free Games**: The script fetches the list of free games from the Epic Games Store. (Free games, yay! 🥳)
2. **Send Email Notification**: If free games are found, the script sends an email notification with the details of the free games. (Your inbox will thank you! 📬)

### Example Code Snippet

```python
try:
    logging.info("Connecting to SMTP server...")
    with smtplib.SMTP(SMTP_SERVER, int(SMTP_PORT)) as server:
        server.set_debuglevel(1)  # Enable debug logs
        server.starttls()
        logging.info("Logging in to SMTP server...")
        server.login(EMAIL, PASSWORD)
        logging.info("Sending email...")
        server.send_message(msg)
        logging.info("Email sent successfully.")
except Exception as e:
    logging.error(f"Failed to send email: {e}")

def main():
    """Main function to fetch games and send notifications."""
    logging.info("Fetching free games...")
    free_games = fetch_free_games()
    if free_games:
        logging.info("Free games found! Sending notification...")
        send_email(free_games)
    else:
        logging.info("No free games available at the moment.")

if __name__ == "__main__":
    main()
```

## Contributing

Feel free to open issues or submit pull requests if you have any improvements or suggestions. (We love contributions as much as we love free games! ❤️)

## License

This project is licensed under the WTFPL License. See the `LICENSE` file for more details. (Do what you want, it's free! 😎)