from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, filters, CallbackContext, CallbackQueryHandler
from telegram.constants import ParseMode

from forwarder import bot, OWNER_ID

PM_START_TEXT = """
Hey {}, I'm {}!
I'm a bot used to forward messages from one chat to another.

To obtain a list of commands, use /help.
"""

PM_HELP_TEXT = """
Here is a list of usable commands:
 - /id : Get your own telegram user ID.
 - /help : Sends you this help message.
 - /publicise <message> : Forwards the provided message to the admins.
 
Markdown formatting is supported in messages. Here are some examples:
    Bold - (b) text (/b) 
    Italic - (i) text (/i) 
    Strikethrough - (s) text (/s) 
    hyperlink - [text](url) 
    Underline - (u) text (/u) 

just send /id in private chat/group/channel and i will reply it's id.
"""

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    message = update.effective_message
    if not (chat and message):
        return

    if not chat.type == "private":
        await message.reply_text("Contact me via PM to get a list of usable commands.")
    else:
        await message.reply_text(PM_HELP_TEXT)
        
bot.add_handler(CommandHandler("help", help_command))