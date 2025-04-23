import os
import logging
import tempfile
from uuid import uuid4
from PIL import Image
from PyPDF2 import PdfReader
from io import BytesIO

# Try to import pytesseract for OCR if available
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

logger = logging.getLogger(__name__)

def extract_images(pdf_path, output_dir):
    """
    Extract images from a PDF file.
    
    Args:
        pdf_path: Path to the PDF file
        output_dir: Directory to save the extracted images
        
    Returns:
        List of paths to the extracted images
    """
    try:
        reader = PdfReader(pdf_path)
        image_paths = []
        
        # Counter for naming extracted images
        image_count = 0
        
        for page_num, page in enumerate(reader.pages):
            for image_file_object in page.images:
                image_count += 1
                image_name = f"image_{page_num+1}_{image_count}_{uuid4().hex}.png"
                image_path = os.path.join(output_dir, image_name)
                
                # Extract and save the image
                with open(image_path, "wb") as img_file:
                    img_file.write(image_file_object.data)
                
                image_paths.append(image_path)
        
        return image_paths
    
    except Exception as e:
        logger.error(f"Error extracting images from PDF: {str(e)}")
        raise Exception(f"فشل في استخراج الصور من PDF: {str(e)}")

def extract_text(pdf_path):
    """
    Extract text from a PDF file.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Extracted text as a string
    """
    try:
        reader = PdfReader(pdf_path)
        text = ""
        
        for page in reader.pages:
            text += page.extract_text() + "\n\n"
        
        # If no text was extracted and OCR is available, try OCR
        if not text.strip() and TESSERACT_AVAILABLE:
            try:
                # Convert PDF to images and perform OCR
                from pdf2image import convert_from_path
                
                text = ""
                images = convert_from_path(pdf_path)
                
                for image in images:
                    text += pytesseract.image_to_string(image) + "\n\n"
            except Exception as ocr_error:
                logger.error(f"OCR error: {str(ocr_error)}")
                # Continue with empty text if OCR fails
        
        return text
    
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        raise Exception(f"فشل في استخراج النص من PDF: {str(e)}")
