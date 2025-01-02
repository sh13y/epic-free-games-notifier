import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = os.getenv("SMTP_PORT")
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
TO_EMAIL = os.getenv("TO_EMAIL")

def fetch_free_games():
    """Fetch free games from the Epic Games Store."""
    url = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    
    free_games = []
    for game in data.get("data", {}).get("Catalog", {}).get("searchStore", {}).get("elements", []):
        if game.get("promotions"):
            for promo in game["promotions"].get("promotionalOffers", []):
                for offer in promo.get("promotionalOffers", []):
                    free_games.append({
                        "title": game.get("title"),
                        "url": f"https://store.epicgames.com/en-US/p/{game.get('productSlug')}",
                        "start_date": offer.get("startDate"),
                        "end_date": offer.get("endDate"),
                    })
    return free_games

def send_email(free_games):
    """Send an email with details about free games."""
    if not free_games:
        print("No free games to notify.")
        return
    
    subject = "Free Games on Epic Games Store!"
    body = "Here are the free games currently available on the Epic Games Store:\n\n"
    for game in free_games:
        body += f"- {game['title']} (Valid until: {game['end_date']})\n  Link: {game['url']}\n\n"
    
    msg = MIMEMultipart()
    msg["From"] = EMAIL
    msg["To"] = TO_EMAIL
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL, PASSWORD)
            server.send_message(msg)
            print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")

def main():
    """Main function to fetch games and send notifications."""
    print("Fetching free games...")
    free_games = fetch_free_games()
    if free_games:
        print("Free games found! Sending notification...")
        send_email(free_games)
    else:
        print("No free games available at the moment.")

if __name__ == "__main__":
    main()
