import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, CallbackContext, filters
from forwarder import bot, OWNER_ID
from forwarder.utils.publicise_helpers import (
    parse_custom_formatting,
    get_first_destination_chat_ID,
    send_to_admin_group,
    reset_user_data,
    is_valid_state
)

# Enable logging
logger = logging.getLogger(__name__)

# Command to handle /publicise
async def publicise(update: Update, context: CallbackContext) -> None:
    logger.info("Received /publicise command.")
    reset_user_data(context)
    context.user_data["state"] = "waiting_for_photo_or_na"
    await update.message.reply_text(
        "Please send a publicity picture (optional) or type 'na' if no picture is required."
    )

# Handler for photo or "na"
async def handle_photo_or_na(update: Update, context: CallbackContext) -> None:
    logger.info("Handling photo or 'na' input.")
    if not is_valid_state(context, "waiting_for_photo_or_na"):
        return

    if update.message.text and update.message.text.strip().lower() == "na":
        context.user_data["photo"] = "na"
        context.user_data["state"] = "waiting_for_message"
        await update.message.reply_text("Got it! Now, please send the message you want to publicise.")
    elif update.message.photo:
        context.user_data["photo"] = update.message.photo[-1].file_id
        context.user_data["state"] = "waiting_for_message"
        await update.message.reply_text("Photo received! Now, please send the message you want to publicise.")
    else:
        await update.message.reply_text(
            "Invalid input. Please send a picture or type 'na' if no picture is required."
        )

# Handler for the final message
async def handle_text(update: Update, context: CallbackContext) -> None:
    logger.info("Handling final message input.")
    user_message = update.message.text
    logger.info(f"User's raw input: {user_message}")

    if not is_valid_state(context, "waiting_for_message"):
        logger.warning("User not in the correct state for final message.")
        return

    try:
        formatted_message = parse_custom_formatting(user_message)
        logger.info(f"Formatted message: {formatted_message}")
    except ValueError as e:
        logger.error(f"Formatting error: {e}")
        await update.message.reply_text("Your message contains invalid formatting. Please fix it and try again.")
        return

    context.user_data["message"] = formatted_message
    photo = context.user_data.get("photo")
    destination_chat_ID = get_first_destination_chat_ID()

    try:
        if photo != "na":
            sent_message = await context.bot.send_photo(
                chat_id=destination_chat_ID,
                photo=photo,
                caption=f"New message for verification:\n\n{formatted_message}",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Accept", callback_data=f"accept|{update.effective_user.id}"),
                     InlineKeyboardButton("Reject", callback_data=f"reject|{update.effective_user.id}")]
                ]),
            )
        else:
            sent_message = await context.bot.send_message(
                chat_id=destination_chat_ID,
                text=f"New message for verification:\n\n{formatted_message}",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Accept", callback_data=f"accept|{update.effective_user.id}"),
                     InlineKeyboardButton("Reject", callback_data=f"reject|{update.effective_user.id}")]
                ]),
            )
        logger.info("Message sent to admin group for verification.")
        await update.message.reply_text("Your message has been sent for approval.")
        context.user_data["sent_message_id"] = sent_message.message_id  # Store sent message ID
    except Exception as e:
        logger.error(f"Error sending message to admin group: {e}")
        await update.message.reply_text("Failed to send your message for approval. Please try again.")

    reset_user_data(context)

# Callback query handler for button clicks
async def handle_button_click(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    try:
        action, user_id = query.data.split("|")
        user_id = int(user_id)

        if action == "accept":
            await context.bot.send_message(
                chat_id=user_id,
                text="Your message has been accepted and publicised!"
            )
            await query.edit_message_text(
                text=query.message.text + "\n\nAction: Accepted.",
                parse_mode="HTML"
            )
        elif action == "reject":
            await query.edit_message_text(
                text=query.message.text + "\n\nAction: Rejected. Please type /feedback to send your reason.",
                parse_mode="HTML"
            )
            context.user_data["reject_user_id"] = user_id
    except Exception as e:
        logger.error(f"Error processing button click: {e}")
        await query.edit_message_text(text="An error occurred while processing the action.")

# Handler for /feedback command
async def feedback(update: Update, context: CallbackContext) -> None:
    logger.info("Handling feedback.")
    reject_user_id = context.user_data.get("reject_user_id")
    if not reject_user_id:
        await update.message.reply_text("No rejection process found.")
        return

    reason = update.message.text.replace("/feedback", "").strip()
    if not reason:
        await update.message.reply_text("Please provide a reason after /feedback.")
        return

    try:
        await context.bot.send_message(
            chat_id=reject_user_id,
            text=f"Your message was rejected. Reason:\n\n{reason}",
            parse_mode="HTML"
        )
        await update.message.reply_text("Rejection reason sent successfully.")
        context.user_data.pop("reject_user_id", None)
    except Exception as e:
        logger.error(f"Error sending rejection feedback: {e}")
        await update.message.reply_text("An error occurred while sending the rejection reason.")

# Register handlers
bot.add_handler(CommandHandler("publicise", publicise))
bot.add_handler(CommandHandler("feedback", feedback))
bot.add_handler(MessageHandler(filters.PHOTO & filters.ChatType.PRIVATE & filters.User(OWNER_ID), handle_photo_or_na))
bot.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"^(na|NA|Na|nA)$") & filters.ChatType.PRIVATE & filters.User(OWNER_ID), handle_photo_or_na))
bot.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE & filters.User(OWNER_ID), handle_text))
bot.add_handler(CallbackQueryHandler(handle_button_click))
