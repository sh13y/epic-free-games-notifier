import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get SMTP and email configuration from environment variables
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = os.getenv("SMTP_PORT")
EMAIL = os.getenv("EMAIL")  # This is your SMTP login email
PASSWORD = os.getenv("PASSWORD")
TO_EMAIL = os.getenv("TO_EMAIL")
FROM_EMAIL = os.getenv("FROM_EMAIL")  # This is the email you want to appear in the "From" field

def fetch_free_games():
    """Fetch free games from the Epic Games Store."""
    url = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions"
    response = requests.get(url)
    response.raise_for_status()  # Raise an error if the request failed
    data = response.json()  # Parse the response as JSON
    
    free_games = []
    for game in data.get("data", {}).get("Catalog", {}).get("searchStore", {}).get("elements", []):
        if game.get("promotions"):
            for promo in game["promotions"].get("promotionalOffers", []):
                for offer in promo.get("promotionalOffers", []):
                    # Check if the game is free (no price or marked as "free")
                    original_price = game.get("price", {}).get("totalPrice", {}).get("originalPrice", 0)
                    discounted_price = game.get("price", {}).get("totalPrice", {}).get("discountPrice", 0)
                    
                    if original_price == 0 and discounted_price == 0:  # Check if it's free
                        free_games.append({
                            "title": game.get("title"),
                            "description": game.get("description", "No description available."),
                            "original_price": "Free",
                            "discounted_price": "Free",
                            "image_url": game.get("keyImages", [{}])[0].get("url", ""),
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
    body = """
    <html>
    <body>
        <h2>Free Games Available on the Epic Games Store!</h2>
        <p>Here are the free games currently available on the Epic Games Store:</p>
        <table border="0" cellspacing="20" cellpadding="10">
    """
    
    # Build the email body with the game's details, including image, description, and price
    for game in free_games:
        body += f"""
        <tr>
            <td>
                <img src="{game['image_url']}" alt="{game['title']}" width="150" />
            </td>
            <td>
                <h3>{game['title']}</h3>
                <p>{game['description']}</p>
                <p><b>Original Price:</b> {game['original_price']}</p>
                <p><b>Discounted Price:</b> {game['discounted_price']}</p>
                <p><a href="{game['url']}">Get it now!</a></p>
                <p><i>Valid until: {game['end_date']}</i></p>
            </td>
        </tr>
        """
    
    body += """
        </table>
    </body>
    </html>
    """

    # Create the email message
    msg = MIMEMultipart("alternative")
    msg["From"] = FROM_EMAIL  # Use the 'From' email address specified in .env
    msg["To"] = TO_EMAIL
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html"))

    try:
        print("Connecting to SMTP server...")
        with smtplib.SMTP(SMTP_SERVER, int(SMTP_PORT)) as server:
            server.set_debuglevel(1)  # Enable debug logs
            server.starttls()  # Secure the connection
            print("Logging in to SMTP server...")
            server.login(EMAIL, PASSWORD)  # Log in to the SMTP server
            print("Sending email...")
            server.send_message(msg)  # Send the email
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
