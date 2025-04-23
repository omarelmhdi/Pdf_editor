
import os
import logging
from telegram.ext import (
    Updater, CommandHandler, MessageHandler, 
    Filters, ConversationHandler, CallbackQueryHandler
)
from handlers import (
    start, help_command, merge_command, split_command, delete_pages_command,
    reorder_command, rotate_command, photo_to_pdf_command, pdf_to_images_command,
    pdf_to_word_command, pdf_to_excel_command, pdf_to_ppt_command,
    word_to_pdf_command, excel_to_pdf_command, ppt_to_pdf_command,
    extract_images_command, extract_text_command, add_text_command,
    add_image_command, add_note_command, add_link_command, add_numbers_command,
    watermark_command, background_command, resize_pages_command,
    page_orientation_command, crop_command, split_pages_command,
    sort_pages_command, add_toc_command, edit_metadata_command,
    file_info_command, rename_command, auto_delete_command, add_pages_command,
    handle_document, handle_photo, handle_text, handle_done, cancel, button_callback
)
from admin_commands import stats_command, broadcast_command
from config import BOT_TOKEN

logger = logging.getLogger(__name__)

def create_bot():
    """Create and configure the bot with all handlers."""
    # Create the Updater instance
    updater = Updater(BOT_TOKEN)
    dispatcher = updater.dispatcher

    # Add command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("done", handle_done))
    
    # Basic PDF operations
    dispatcher.add_handler(CommandHandler("merge", merge_command))
    dispatcher.add_handler(CommandHandler("split", split_command))
    dispatcher.add_handler(CommandHandler("add_pages", add_pages_command))
    dispatcher.add_handler(CommandHandler("delete_pages", delete_pages_command))
    dispatcher.add_handler(CommandHandler("reorder", reorder_command))
    dispatcher.add_handler(CommandHandler("rotate", rotate_command))
    
    # Conversion operations
    dispatcher.add_handler(CommandHandler("photo_to_pdf", photo_to_pdf_command))
    dispatcher.add_handler(CommandHandler("pdf_to_images", pdf_to_images_command))
    dispatcher.add_handler(CommandHandler("pdf_to_word", pdf_to_word_command))
    dispatcher.add_handler(CommandHandler("pdf_to_excel", pdf_to_excel_command))
    dispatcher.add_handler(CommandHandler("pdf_to_ppt", pdf_to_ppt_command))
    dispatcher.add_handler(CommandHandler("word_to_pdf", word_to_pdf_command))
    dispatcher.add_handler(CommandHandler("excel_to_pdf", excel_to_pdf_command))
    dispatcher.add_handler(CommandHandler("ppt_to_pdf", ppt_to_pdf_command))
    
    # Content extraction
    dispatcher.add_handler(CommandHandler("extract_images", extract_images_command))
    dispatcher.add_handler(CommandHandler("extract_text", extract_text_command))
    
    # File editing
    dispatcher.add_handler(CommandHandler("add_text", add_text_command))
    dispatcher.add_handler(CommandHandler("add_image", add_image_command))
    dispatcher.add_handler(CommandHandler("add_note", add_note_command))
    dispatcher.add_handler(CommandHandler("add_link", add_link_command))
    dispatcher.add_handler(CommandHandler("add_numbers", add_numbers_command))
    dispatcher.add_handler(CommandHandler("watermark", watermark_command))
    dispatcher.add_handler(CommandHandler("background", background_command))
    
    # Page formatting
    dispatcher.add_handler(CommandHandler("resize_pages", resize_pages_command))
    dispatcher.add_handler(CommandHandler("page_orientation", page_orientation_command))
    dispatcher.add_handler(CommandHandler("crop", crop_command))
    dispatcher.add_handler(CommandHandler("split_pages", split_pages_command))
    dispatcher.add_handler(CommandHandler("sort_pages", sort_pages_command))
    dispatcher.add_handler(CommandHandler("add_toc", add_toc_command))
    
    # File information and settings
    dispatcher.add_handler(CommandHandler("edit_metadata", edit_metadata_command))
    dispatcher.add_handler(CommandHandler("file_info", file_info_command))
    dispatcher.add_handler(CommandHandler("rename", rename_command))
    dispatcher.add_handler(CommandHandler("auto_delete", auto_delete_command))
    dispatcher.add_handler(CommandHandler("cancel", cancel))
    
    # أوامر المدير
    dispatcher.add_handler(CommandHandler("stats", stats_command))
    dispatcher.add_handler(CommandHandler("broadcast", broadcast_command, pass_args=True))
    
    # Add callback query handler for button presses
    dispatcher.add_handler(CallbackQueryHandler(button_callback))
    
    # Add message handlers for documents, photos, and text
    dispatcher.add_handler(MessageHandler(Filters.photo, handle_photo))
    dispatcher.add_handler(MessageHandler(Filters.document, handle_document))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))
    
    # Start the Bot
    updater.start_polling()
    
    # Keep the bot running until interrupted
    updater.idle()
    
    return updater
