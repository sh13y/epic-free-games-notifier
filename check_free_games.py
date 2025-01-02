import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuration
SMTP_SERVER = "smtp.gmail.com"  # Your SMTP server
SMTP_PORT = 587
EMAIL = "your_email@example.com"  # Your email
PASSWORD = "your_email_password"  # Your email password
TO_EMAIL = "to_email@example.com"  # Recipient's email

def fetch_free_games():
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
    subject = "Free Games on Epic Games Store!"
    body = "Here are the free games currently available on the Epic Games Store:\n\n"
    for game in free_games:
        body += f"- {game['title']} (Valid until: {game['end_date']})\n  Link: {game['url']}\n\n"
    
    msg = MIMEMultipart()
    msg["From"] = EMAIL
    msg["To"] = TO_EMAIL
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL, PASSWORD)
        server.send_message(msg)
        print("Email sent successfully.")

def main():
    free_games = fetch_free_games()
    if free_games:
        send_email(free_games)
    else:
        print("No free games available at the moment.")

if __name__ == "__main__":
    main()
