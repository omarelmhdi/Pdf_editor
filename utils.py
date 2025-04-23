import os
import json
import shutil
import logging
import tempfile
from PyPDF2 import PdfReader

logger = logging.getLogger(__name__)

# Directory to store temporary user data
TEMP_DIR = os.path.join(tempfile.gettempdir(), "telegram_pdf_bot")
USER_DATA_DIR = os.path.join(TEMP_DIR, "user_data")

def create_temp_dir(user_id):
    """Create a temporary directory for a user."""
    user_dir = os.path.join(TEMP_DIR, str(user_id))
    os.makedirs(user_dir, exist_ok=True)
    return user_dir

def clean_temp_files(user_id):
    """Clean up temporary files for a user."""
    user_dir = os.path.join(TEMP_DIR, str(user_id))
    
    # Check if automatic deletion is enabled for the user
    settings = get_user_data(user_id, 'settings', {})
    auto_delete = settings.get('auto_delete', True)
    
    if auto_delete and os.path.exists(user_dir):
        shutil.rmtree(user_dir)

def save_user_data(user_id, key, data):
    """Save user data to disk."""
    os.makedirs(USER_DATA_DIR, exist_ok=True)
    
    user_data_file = os.path.join(USER_DATA_DIR, f"{user_id}.json")
    
    # Load existing data if any
    if os.path.exists(user_data_file):
        with open(user_data_file, 'r') as f:
            try:
                all_data = json.load(f)
            except json.JSONDecodeError:
                all_data = {}
    else:
        all_data = {}
    
    # Update data
    all_data[key] = data
    
    # Save back to disk
    with open(user_data_file, 'w') as f:
        json.dump(all_data, f)

def get_user_data(user_id, key, default=None):
    """Get user data from disk."""
    user_data_file = os.path.join(USER_DATA_DIR, f"{user_id}.json")
    
    if not os.path.exists(user_data_file):
        return default
    
    with open(user_data_file, 'r') as f:
        try:
            all_data = json.load(f)
            return all_data.get(key, default)
        except json.JSONDecodeError:
            return default

def get_file_info(file_path):
    """Get information about a file."""
    file_size = os.path.getsize(file_path)
    file_name = os.path.basename(file_path)
    file_ext = os.path.splitext(file_name)[1].lower()
    
    info = f"📄 معلومات الملف:\n"
    info += f"الاسم: {file_name}\n"
    info += f"الحجم: {format_size(file_size)}\n"
    
    # Get PDF-specific information
    if file_ext == '.pdf':
        try:
            reader = PdfReader(file_path)
            num_pages = len(reader.pages)
            
            info += f"عدد الصفحات: {num_pages}\n"
            
            # Get metadata
            metadata = reader.metadata
            if metadata:
                info += "\nبيانات وصفية:\n"
                
                if metadata.title:
                    info += f"العنوان: {metadata.title}\n"
                if metadata.author:
                    info += f"المؤلف: {metadata.author}\n"
                if metadata.subject:
                    info += f"الموضوع: {metadata.subject}\n"
                if metadata.creator:
                    info += f"المنشئ: {metadata.creator}\n"
                if metadata.producer:
                    info += f"البرنامج: {metadata.producer}\n"
        except Exception as e:
            info += f"\nفشل في قراءة معلومات PDF: {str(e)}\n"
    
    return info

def format_size(size_bytes):
    """Format file size in a human-readable format."""
    for unit in ['بايت', 'كيلوبايت', 'ميجابايت', 'جيجابايت']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} تيرابايت"

async def download_file(context, file_id, dest_path):
    """Download a file from Telegram."""
    try:
        telegram_file = await context.bot.get_file(file_id)
        await telegram_file.download_to_drive(dest_path)
        return dest_path
    except Exception as e:
        logger.error(f"Error downloading file: {str(e)}")
        raise Exception(f"فشل في تنزيل الملف: {str(e)}")
