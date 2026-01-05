import requests
from bs4 import BeautifulSoup
import smtplib
import os
import time
from dotenv import load_dotenv
load_dotenv()
# --- CONFIGURATION ---
# 1. THE URL
URL = "https://www.amazon.in/GUESS-White-Dial-Men-Watch/dp/B07HBLDVP3/ref=sr_1_1_sspa?crid=2GW9XMRZXN43Z&dib=eyJ2IjoiMSJ9.OoIKv06C8NtXMIAqS7d4_bj0tm5b6asFBqdAOZ_T8mv98lY5CaWT3TvC0-NxoMJmeGb1KNLBDoq2zEvdVk9Ktq7p-HDqmanCVng9uJuYFl1la2sr_0ii3MYuA6js85I5mAgY23w8gbwEQhxX8DF5W3MZneX6j49QSNGYkJ3naXRzhdXASF14ihq-3LCGE8eOa7jVCrtXtZSLhFL1nNkhlLQz3CtofONH1JNsV_igXT1i8z7Ee7njau863h2TxIJQhCLwineOOlRU0GgAhj3RNoAfELim3SXRxejMV0GHWxk.CJ8x6GLF-RZgrv2d_eeNGPGUV31uaI77Ons3xKKzlZ4&dib_tag=se&keywords=watch&qid=1767632984&s=apparel&sprefix=watch+%2Capparel%2C506&sr=1-1-spons&aref=sj8hgR2Gtw&sp_csd=d2lkZ2V0TmFtZT1zcF9hdGY&psc=1"

# 2. THE TARGET PRICE
# The current price looks to be around ₹199 - ₹299. 
# Set this to your desired buy price.
TARGET_PRICE = 20000.00 

# 3. HTML SELECTORS
# Amazon uses the class "a-price-whole" for the main number (e.g., "199").
ELEMENT_ID = None 

ELEMENT_CLASS = "a-price-whole" 
ELEMENT_TAG = "span"

# --- EMAIL SECRETS ---
EMAIL_ADDRESS = os.environ.get("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
RECEIVER_EMAIL = os.environ.get("RECEIVER_EMAIL")

def get_product_price(url):
    """
    Fetches the URL, finds the price element using ID or Class, 
    and returns a clean float number.
    """
    # Headers make the script look like a real browser (Chrome on Windows)
    headers = {
        "User-Agent": "CCBot/2.0 (https://commoncrawl.org/faq/)",
        "Accept-Language": "en-US,en;q=0.9"
    }

    try:
        print(f"Connecting to: {url[:50]}...") # Print first 50 chars of URL
        response = requests.get(url, headers=headers)
        response.raise_for_status() 

        soup = BeautifulSoup(response.content, "html.parser")
        price_element = None

        # --- LOGIC TO FIND THE ELEMENT ---
        if ELEMENT_ID:
            print(f"Searching for ID: {ELEMENT_ID}")
            price_element = soup.find(id=ELEMENT_ID)
        elif ELEMENT_CLASS and ELEMENT_TAG:
            print(f"Searching for Class: {ELEMENT_CLASS} in tag: {ELEMENT_TAG}")
            price_element = soup.find(ELEMENT_TAG, class_=ELEMENT_CLASS)

        # --- LOGIC TO CLEAN THE DATA ---
        if price_element:
            raw_text = price_element.get_text().strip()
            print(f"Raw text found: '{raw_text}'") 

            # Remove currency symbols and commas (e.g. "$1,299.00" -> "1299.00")
            clean_text = raw_text.replace("$", "").replace("£", "").replace("€", "").replace(",", "")
            
            # Handle cases where there is extra text (e.g. "USD 50.00")
            # We filter the string to keep only digits and the dot
            clean_text = "".join([c for c in clean_text if c.isdigit() or c == '.'])

            try:
                price_number = float(clean_text)
                return price_number
            except ValueError:
                print(f"Error: Could not convert '{clean_text}' to a number.")
                return None
        else:
            print("Error: Element not found. Please check your ID/Class selector.")
            return None

    except Exception as e:
        print(f"Connection Error: {e}")
        return None

def send_email(price, product_url):
    """
    Sends the email notification.
    """
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        print("Skipping email: Credentials not found in environment variables.")
        return

    subject = f"Price Alert! Dropped to {price}"
    body = f"The price is now {price}!\n\nLink: {product_url}"
    msg = f"Subject: {subject}\n\n{body}"

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as connection:
            connection.starttls()
            connection.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            connection.sendmail(EMAIL_ADDRESS, RECEIVER_EMAIL, msg)
            print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

def main():
    print("--- Starting Price Tracker ---")
    current_price = get_product_price(URL)
    
    if current_price:
        print(f"Current Price: {current_price}")
        print(f"Target Price:  {TARGET_PRICE}")
        
        if current_price < TARGET_PRICE:
            print(">>> PRICE IS LOW! Initiating email sequence...")
            send_email(current_price, URL)
        else:
            print(">>> Price is still too high. Checking again tomorrow.")
    else:
        print(">>> Failed to retrieve valid price data.")

if __name__ == "__main__":

    main()
