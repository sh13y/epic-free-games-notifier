import datetime
import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = os.getenv("SMTP_PORT")
EMAIL = os.getenv("EMAIL")  # This is your SMTP login email
PASSWORD = os.getenv("PASSWORD")
TO_EMAIL = os.getenv("TO_EMAIL")
FROM_EMAIL = os.getenv(
    "FROM_EMAIL"
)  # This is the email you want to appear in the "From" field


def format_date(date_string):
    """Format the date string to a more readable format."""
    try:
        date_obj = datetime.datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S.000Z")
        return date_obj.strftime(
            "%B %d, %Y at %I:%M %p"
        )  # Example: January 09, 2025 at 04:00 PM
    except ValueError:
        logging.error(f"Error parsing date: {date_string}")
        return date_string  # Return the original string if parsing fails


def fetch_free_games():
    """Fetch free games from the Epic Games Store."""
    url = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        logging.error(f"Error fetching free games: {e}")
        return None

    free_games = []
    try:
        games: list[dict] = data["data"]["Catalog"]["searchStore"]["elements"]
    except (KeyError, TypeError):
        return None

    for game in games:
        if not game.get("promotions"):
            continue

        for promo in game["promotions"].get("promotionalOffers", []):
            for offer in promo.get("promotionalOffers", []):
                # Check if the game is free (no price or marked as "free")
                discounted_price = (
                    game.get("price", {}).get("totalPrice", {}).get("discountPrice", 0)
                )

                # Check if it's free
                if discounted_price != 0:
                    continue

                # Extracting the correct urlSlug from catalogNs.mappings
                url_slug = next(
                    (
                        mapping.get("pageSlug")
                        for mapping in game.get("catalogNs", {}).get("mappings", [])
                        if mapping.get("pageSlug")
                    ),
                    None,
                )

                # Ensure url_slug is not None
                if not url_slug:
                    continue

                free_games.append(
                    {
                        "title": game.get("title"),
                        "description": game.get(
                            "description", "No description available."
                        ),
                        "original_price": "Free",
                        "discounted_price": "Free",
                        "image_url": game.get("keyImages", [{}])[0].get("url", ""),
                        "url": f"https://store.epicgames.com/en-US/p/{url_slug}",
                        "start_date": offer.get("startDate"),
                        "end_date": offer.get("endDate"),
                    }
                )
    return free_games


def send_email(free_games):
    """Send an email with details about free games."""
    if not free_games:
        logging.info("No free games to notify.")
        return None

    subject = "Free Games on Epic Games Store!"

    # Modern, professional, and responsive email body with a border
    body = """
    <html>
    <head>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f9;
                padding: 20px;
                margin: 0;
            }
            .container {
                max-width: 600px;
                margin: 0 auto;
                background-color: #fff;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                border: 1px solid #ddd;
            }
            .header {
                text-align: center;
                color: #333;
            }
            .header h2 {
                margin: 0;
                font-size: 24px;
            }
            .content {
                margin-top: 20px;
            }
            .game {
                text-align: center;
                border-bottom: 1px solid #ddd;
                padding: 20px 0;
            }
            .game img {
                border-radius: 8px;
                max-width: 100%;
                height: auto;
            }
            .game-details {
                margin-top: 10px;
            }
            .game-details h3 {
                margin: 0;
                font-size: 18px;
                color: #333;
            }
            .game-details p {
                margin: 5px 0;
                color: #777;
                font-size: 14px;
            }
            .game-details .price {
                font-size: 16px;
                font-weight: bold;
                color: #333;
            }
            .game-details .price span {
                background-color: red;
                color: white;
                padding: 3px 6px;
                text-decoration: none;
                border-radius: 3px;
                font-weight: bold;
                display: inline-block;
                margin-top: 10px;
            }
            .game-details a {
                background-color: #fcb900;
                color: black;
                padding: 8px 16px;
                text-decoration: none;
                border-radius: 5px;
                font-weight: bold;
                display: inline-block;
                margin-top: 10px;
            }
            .game-details .offer-end {
                font-size: 14px;
                color: #888;
                margin-top: 20px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Free Games Available on the Epic Games Store!</h2>
                <p>Don't miss out on these amazing FREE games:</p>
            </div>
            <div class="content">
    """
    # Build the email body with the game's details, including image, description, and price
    for game in free_games:
        end_date = format_date(
            game["end_date"]
        )  # Format the end date for better readability
        body += f"""
        <div class="game">
            <img src="{game['image_url']}" alt="{game['title']}" />
            <div class="game-details">
                <h3>{game['title']}</h3>
                <p>{game['description']}</p>
                <p class="price">Price: <span>{game['original_price']}</span></p>
                <a href="{game['url']}">Claim Your Free Game Now!</a>
                <p class="offer-end"><i>Offer ends: {end_date}</i></p>
            </div>
        </div>
        """

    body += """
            </div>
        </div>
    </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["From"] = FROM_EMAIL  # Use the 'From' email address specified in .env
    msg["To"] = TO_EMAIL
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html"))

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
