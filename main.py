import os
import re
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from telegram import Update #upm package(python-telegram-bot[webhooks])
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes #upm package(python-telegram-bot[webhooks])


def find_url(text):
    # This regex pattern is designed to find most URLs.
    # It looks for strings starting with http:// or https://,
    # followed by one or more characters that are not spaces.
    pattern = r"https?://[\w.-]+(?:\.[\w.-]+)*[/\w.-]*(?:\?\S+)?(?=\s|$)"
    match = re.search(pattern, text)

    # If a match is found, return the matched URL.
    if match:
        return match.group(0)
    else:
        # Return a message indicating no URL found, or handle it as you see fit.
        return "No URL found in the text."

def remove_the_tracking(parsed_url):

    # Check if the domain is www.youtube.com
    if "youtu" in parsed_url.netloc:
        # Parse query parameters
        query_params = parse_qs(parsed_url.query)
        # Keep only the 'v' parameter
        filtered_params = {key: value for key, value in query_params.items() if key == 'v'}
        # Reconstruct the query string
        query_string = urlencode(filtered_params, doseq=True)
    else:
        # For all other domains, remove the query string
        query_string = ""

    # Reconstruct the URL with the new query string
    return urlunparse(parsed_url._replace(query=query_string))


    
TELEGRAM_API_TOKEN = os.environ['TELEGRAM_API_TOKEN']
async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')

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
app.add_handler(MessageHandler(filters=None, callback=removeTracking))

app.run_webhook(listen='0.0.0.0', port=8080, webhook_url=os.environ['TELEGRAM_WEBHOOK_URL'])