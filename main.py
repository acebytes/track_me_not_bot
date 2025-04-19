import os
import re
import base64
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse
from Crypto.Cipher import AES #upm package(pycryptodome)
from Crypto.Util.Padding import pad #upm package(pycryptodome)
from Crypto.Random import get_random_bytes #upm package(pycryptodome)
import base64
import logging
import requests
from urllib.parse import urlparse, urlunparse

from telegram import Update #upm package(python-telegram-bot[webhooks])
from telegram.ext import filters, ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes #upm package(python-telegram-bot[webhooks])

# Configure the logging system
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Create a logger object
logger = logging.getLogger(__name__)


TELEGRAM_API_TOKEN = os.environ['TELEGRAM_API_TOKEN']


def strip_url_parameters(full_url: str) -> str:
    """
    Returns the base URL without query parameters or fragments.

    Args:
        full_url (str): The complete URL (with optional query or fragment).

    Returns:
        str: The cleaned base URL.
    """
    parsed = urlparse(full_url)
    cleaned_url = urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        '',  # params
        '',  # query
        ''   # fragment
    ))
    return cleaned_url

def encrypt_message(message, key):
  # Generate a random IV
  iv = get_random_bytes(16)
  cipher = AES.new(key, AES.MODE_CBC, iv)
  ct_bytes = cipher.encrypt(pad(message.encode('utf-8'), AES.block_size))
  ct = base64.b64encode(iv + ct_bytes).decode('utf-8')
  return ct

def safe_encode(data):
  # Base64 encode
  encoded = base64.b64encode(data.encode())
  print("Base64 Encoded:", encoded.decode())
  # Make it URL-safe
  return encoded.decode().replace('+', '-').replace('/', '_').rstrip('=')

def remove_the_tracking(parsed_url):

    # Check if the domain is www.youtube.com
    if "youtu" in parsed_url.netloc:
        # Parse query parameters
        query_params = parse_qs(parsed_url.query)
        # Keep only the 'v' parameter
        filtered_params = {key: value for key, value in query_params.items() if key == 'v'}
        # Reconstruct the query string
        query_string = urlencode(filtered_params, doseq=True)
        
    elif "tiktok" in parsed_url.netloc or "reddit" in parsed_url.netloc:
        # Use the full URL for request
        full_url = urlunparse(parsed_url)
        try:
            response = requests.get(full_url)
            clean_url = strip_url_parameters(response.url)
            return clean_url
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching URL: {e}")
            # If request fails, just remove the query parameters
            return urlunparse(parsed_url._replace(query=""))

    else:
        # For all other domains, remove the query string
        query_string = ""

    # Reconstruct the URL with the new query string
    return urlunparse(parsed_url._replace(query=query_string))


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')

async def get_dl(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    key =  os.environ['CRYPTO_KEY']
    dl_domain = os.environ['DL_SERVER_DOMAIN']

    text = update.effective_message.text
    command_parts = text.split()

    if len(command_parts) < 2:
        await update.effective_message.reply_text("Please provide a URL after the /get command.")
        return

    command = command_parts[0]
    url = command_parts[1]
    parsed_url = urlparse(url)
    # if a valid url
    if(bool(parsed_url.scheme) and bool(parsed_url.netloc)):

      if command == "/get":
        # encode URL
        encoded_url = safe_encode(url)
        await update.message.reply_text(f'dl link: {dl_domain}v/{encoded_url}')
      else:
        await update.message.reply_text(f'some issue here')
    else:
       await update.message.reply_text(f'not valid url')

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Send me a url to remove tracking parameters. Tested on YT, IG, eBay, and more')


async def removeTracking(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    # Using regex to extract the first URL from the text
    url_pattern = r'https?://[\w.-]+(?:\.[\w.-]+)*[/\w.-]*(?:\?\S+)?(?=\s|$)'
    match = re.search(url_pattern, update.message.text)

    if match:
      url = match.group(0)
      parsed_url = urlparse(url)

      # Check if the URL is a valid URL
      if(bool(parsed_url.scheme) and bool(parsed_url.netloc)):
        trimmed_url = remove_the_tracking(parsed_url)
        await update.message.reply_text(trimmed_url)

      else:
        await update.message.reply_text("no URL found")
    else:
        await update.message.reply_text("no URL found")


app = ApplicationBuilder().token(TELEGRAM_API_TOKEN).build()

app.add_handler(CommandHandler("hello", hello))
app.add_handler(CommandHandler("help", help))
# app.add_handler(CommandHandler("get", get_dl))

app.add_handler(MessageHandler(filters.Regex(r'^/get\s+\S+'), get_dl))
app.add_handler(MessageHandler(filters=None, callback=removeTracking))

app.run_webhook(listen='0.0.0.0', port=8080, webhook_url=os.environ['TELEGRAM_WEBHOOK_URL'])


# import os
# import re
# from urllib.parse import parse_qs, urlencode, urlparse, urlunparse
# import logging

# from telegram import Update #upm package(python-telegram-bot[webhooks])
# from telegram.ext import filters, ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes #upm package(python-telegram-bot[webhooks])

# # Configure the logging system
# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# # Create a logger object
# logger = logging.getLogger(__name__)


# TELEGRAM_API_TOKEN = os.environ['TELEGRAM_API_TOKEN']


# def remove_the_tracking(parsed_url):

#     # Check if the domain is www.youtube.com
#     if "youtu" in parsed_url.netloc:
#         # Parse query parameters
#         query_params = parse_qs(parsed_url.query)
#         # Keep only the 'v' parameter
#         filtered_params = {key: value for key, value in query_params.items() if key == 'v'}
#         # Reconstruct the query string
#         query_string = urlencode(filtered_params, doseq=True)
#     else:
#         # For all other domains, remove the query string
#         query_string = ""

#     # Reconstruct the URL with the new query string
#     return urlunparse(parsed_url._replace(query=query_string))


# async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     await update.message.reply_text(f'Hello {update.effective_user.first_name}')


# async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     await update.message.reply_text(f'Send me a url to remove tracking parameters. Tested on YT, IG, eBay, and more')


# async def removeTracking(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

#     # Using regex to extract the first URL from the text
#     url_pattern = r'https?://[\w.-]+(?:\.[\w.-]+)*[/\w.-]*(?:\?\S+)?(?=\s|$)'
#     match = re.search(url_pattern, update.message.text)

#     if match:
#       url = match.group(0)
#       parsed_url = urlparse(url)

#       # Check if the URL is a valid URL
#       if(bool(parsed_url.scheme) and bool(parsed_url.netloc)):
#         trimmed_url = remove_the_tracking(parsed_url)
#         await update.message.reply_text(trimmed_url)

#       else:
#         await update.message.reply_text("no URL found")
#     else:
#         await update.message.reply_text("no URL found")


# app = ApplicationBuilder().token(TELEGRAM_API_TOKEN).build()

# app.add_handler(CommandHandler("hello", hello))
# app.add_handler(CommandHandler("help", help))

# app.add_handler(MessageHandler(filters=None, callback=removeTracking))

# app.run_webhook(listen='0.0.0.0', port=8080, webhook_url=os.environ['TELEGRAM_WEBHOOK_URL'])