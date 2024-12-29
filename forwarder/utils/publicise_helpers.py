import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.constants import ParseMode
import json
import re # For custom formatting

# Enable logging
logger = logging.getLogger(__name__)

# Function to get the first destination chat ID
def get_first_destination_chat_ID() -> int:
    import json

    with open("chat_list.json", "r") as file:
        data = json.load(file)
    return data[0]["destination"]

def parse_custom_formatting(user_input: str) -> str:
    """
    Converts custom formatting syntax to HTML for Telegram.
    Handles:
    - (b)bold(/b) -> <b>
    - (i)italic(/i) -> <i>
    - (u)underline(/u) -> <u>
    - (s)strikethrough(/s) -> <s>
    - [text](url) -> <a href="url">text</a>
    """
    try:
        # Replace custom syntax with HTML tags
        formatted = re.sub(r"\(b\)(.*?)\(/b\)", r"<b>\1</b>", user_input)  # Bold
        formatted = re.sub(r"\(i\)(.*?)\(/i\)", r"<i>\1</i>", formatted)  # Italic
        formatted = re.sub(r"\(u\)(.*?)\(/u\)", r"<u>\1</u>", formatted)  # Underline
        formatted = re.sub(r"\(s\)(.*?)\(/s\)", r"<s>\1</s>", formatted)  # Strikethrough
        
        # Ensure URLs are converted correctly
        formatted = re.sub(r"\[(.*?)\]\((https?:\/\/[^\s]+)\)", r'<a href="\2">\1</a>', formatted)  # Hyperlink

        # Log the intermediate state for debugging
        print(f"DEBUG: Intermediate formatted text: {formatted}")

        # Validate the resulting HTML
        from xml.etree.ElementTree import fromstring, ParseError
        try:
            fromstring(f"<div>{formatted}</div>")  # Wrapping in a div for validation
        except ParseError as e:
            raise ValueError(f"Unbalanced or invalid tags in formatting: {e}")

        return formatted

    except Exception as e:
        raise ValueError(f"Error in parsing custom formatting: {e}")

# Function to reset user data
def reset_user_data(context):
    context.user_data.clear()
    logger.info("User data reset.")

# Function to validate the user's current state
def is_valid_state(context, required_state):
    if context.user_data.get("state") != required_state:
        logger.warning(f"User not in the correct state: {required_state}")
        return False
    return True

# Function to send a message to the admin group
async def send_to_admin_group(bot: Bot, user_message: str, photo: str, user_id: int) -> int:
    destination_chat_ID = get_first_destination_chat_ID()

    try:
        if photo and photo != "na":
            sent_message = await bot.send_photo(
                chat_id=destination_chat_ID,
                photo=photo,
                caption=f"New message for verification:\n\n{user_message}",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Accept", callback_data=f"accept|{user_id}"),
                     InlineKeyboardButton("Reject", callback_data=f"reject|{user_id}")]
                ]),
            )
        else:
            sent_message = await bot.send_message(
                chat_id=destination_chat_ID,
                text=f"New message for verification:\n\n{user_message}",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Accept", callback_data=f"accept|{user_id}"),
                     InlineKeyboardButton("Reject", callback_data=f"reject|{user_id}")]
                ]),
            )
        logger.info("Message sent to admin group for verification.")
        return sent_message.message_id
    except Exception as e:
        logger.error(f"Error sending message to admin group: {e}")
        return None
