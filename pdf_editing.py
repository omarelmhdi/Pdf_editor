import os
import logging
from uuid import uuid4
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image, ImageDraw, ImageFont
import io

logger = logging.getLogger(__name__)

def add_text_to_pdf(pdf_path, text, output_dir, page_num=0, position=(100, 100), font_size=12, color=(0, 0, 0)):
    """
    Add text to a PDF.
    
    Args:
        pdf_path: Path to the PDF file
        text: Text to add
        output_dir: Directory to save the result
        page_num: Page number to add text to (0-based)
        position: Position (x, y) to place the text
        font_size: Font size
        color: RGB color tuple
        
    Returns:
        Path to the modified PDF
    """
    try:
        # Using pdf2image to convert the page to an image
        from pdf2image import convert_from_path
        
        reader = PdfReader(pdf_path)
        writer = PdfWriter()
        
        # Check valid page number
        if page_num < 0 or page_num >= len(reader.pages):
            page_num = 0  # Default to first page if invalid
        
        # Convert that specific page to an image
        images = convert_from_path(pdf_path, first_page=page_num+1, last_page=page_num+1)
        img = images[0]
        
        # Create a drawing object
        draw = ImageDraw.Draw(img)
        
        # Add text to the image
        try:
            # Try to get a font - this might not work in all environments
            font = ImageFont.truetype("arial.ttf", font_size)
        except IOError:
            # Use default font if Arial not available
            font = ImageFont.load_default()
        
        draw.text(position, text, font=font, fill=color)
        
        # Convert image back to PDF
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PDF')
        img_byte_arr.seek(0)
        
        # Create a PdfReader from the modified page
        modified_page_reader = PdfReader(img_byte_arr)
        
        # Add all pages from the original PDF, replacing the modified page
        for i, page in enumerate(reader.pages):
            if i == page_num:
                writer.add_page(modified_page_reader.pages[0])
            else:
                writer.add_page(page)
        
        output_path = os.path.join(output_dir, f"text_added_{uuid4().hex}.pdf")
        
        with open(output_path, "wb") as output_file:
            writer.write(output_file)
        
        return output_path
    
    except Exception as e:
        logger.error(f"Error adding text to PDF: {str(e)}")
        raise Exception(f"فشل في إضافة النص إلى PDF: {str(e)}")

def add_image_to_pdf(pdf_path, image_path, output_dir, page_num=0, position=(100, 100), size=(200, 200)):
    """
    Add an image to a PDF.
    
    Args:
        pdf_path: Path to the PDF file
        image_path: Path to the image file
        output_dir: Directory to save the result
        page_num: Page number to add image to (0-based)
        position: Position (x, y) to place the image
        size: Size (width, height) for the image
        
    Returns:
        Path to the modified PDF
    """
    try:
        # Using pdf2image to convert the page to an image
        from pdf2image import convert_from_path
        
        reader = PdfReader(pdf_path)
        writer = PdfWriter()
        
        # Check valid page number
        if page_num < 0 or page_num >= len(reader.pages):
            page_num = 0  # Default to first page if invalid
        
        # Convert that specific page to an image
        images = convert_from_path(pdf_path, first_page=page_num+1, last_page=page_num+1)
        background = images[0]
        
        # Open the image to add
        overlay = Image.open(image_path)
        overlay = overlay.resize(size)
        
        # Paste the image onto the PDF page
        background.paste(overlay, position, overlay if overlay.mode == 'RGBA' else None)
        
        # Convert image back to PDF
        img_byte_arr = io.BytesIO()
        background.save(img_byte_arr, format='PDF')
        img_byte_arr.seek(0)
        
        # Create a PdfReader from the modified page
        modified_page_reader = PdfReader(img_byte_arr)
        
        # Add all pages from the original PDF, replacing the modified page
        for i, page in enumerate(reader.pages):
            if i == page_num:
                writer.add_page(modified_page_reader.pages[0])
            else:
                writer.add_page(page)
        
        output_path = os.path.join(output_dir, f"image_added_{uuid4().hex}.pdf")
        
        with open(output_path, "wb") as output_file:
            writer.write(output_file)
        
        return output_path
    
    except Exception as e:
        logger.error(f"Error adding image to PDF: {str(e)}")
        raise Exception(f"فشل في إضافة الصورة إلى PDF: {str(e)}")

def add_note_to_pdf(pdf_path, note_text, output_dir, page_num=0, position=(100, 100)):
    """
    Add a note to a PDF.
    
    Args:
        pdf_path: Path to the PDF file
        note_text: Text of the note
        output_dir: Directory to save the result
        page_num: Page number to add note to (0-based)
        position: Position (x, y) to place the note
        
    Returns:
        Path to the modified PDF
    """
    try:
        reader = PdfReader(pdf_path)
        writer = PdfWriter()
        
        # Check valid page number
        if page_num < 0 or page_num >= len(reader.pages):
            page_num = 0  # Default to first page if invalid
        
        # Copy all pages
        for i, page in enumerate(reader.pages):
            writer.add_page(page)
            
            # Add annotation to the specified page
            if i == page_num:
                # Note: This is a simplified version. For more advanced annotations,
                # a library like pikepdf might be needed
                writer.add_annotation(
                    page_number=i,
                    annotation={
                        '/Subtype': '/Text',
                        '/Contents': note_text,
                        '/Rect': [position[0], position[1], position[0] + 20, position[1] + 20],
                        '/Open': True
                    }
                )
        
        output_path = os.path.join(output_dir, f"note_added_{uuid4().hex}.pdf")
        
        with open(output_path, "wb") as output_file:
            writer.write(output_file)
        
        return output_path
    
    except Exception as e:
        logger.error(f"Error adding note to PDF: {str(e)}")
        raise Exception(f"فشل في إضافة ملاحظة إلى PDF: {str(e)}")

def add_link_to_pdf(pdf_path, link_data, output_dir):
    """
    Add a link to a PDF.
    
    Args:
        pdf_path: Path to the PDF file
        link_data: Dictionary with 'text', 'url', and 'page' keys
        output_dir: Directory to save the result
        
    Returns:
        Path to the modified PDF
    """
    try:
        # Extract link data
        text = link_data.get('text', 'Link')
        url = link_data.get('url', 'https://www.example.com')
        page_num = int(link_data.get('page', 0))
        
        reader = PdfReader(pdf_path)
        writer = PdfWriter()
        
        # Check valid page number
        if page_num < 0 or page_num >= len(reader.pages):
            page_num = 0  # Default to first page if invalid
        
        # Copy all pages
        for i, page in enumerate(reader.pages):
            writer.add_page(page)
            
            # Add link to the specified page
            if i == page_num:
                # Note: This is a simplified version. For more advanced linking,
                # a library like pikepdf might be needed
                writer.add_annotation(
                    page_number=i,
                    annotation={
                        '/Subtype': '/Link',
                        '/A': {
                            '/S': '/URI',
                            '/URI': url
                        },
                        '/Rect': [100, 100, 300, 120],  # Position of the link
                        '/Border': [0, 0, 0]
                    }
                )
        
        output_path = os.path.join(output_dir, f"link_added_{uuid4().hex}.pdf")
        
        with open(output_path, "wb") as output_file:
            writer.write(output_file)
        
        return output_path
    
    except Exception as e:
        logger.error(f"Error adding link to PDF: {str(e)}")
        raise Exception(f"فشل في إضافة رابط إلى PDF: {str(e)}")

def add_page_numbers(pdf_path, output_dir, position='bottom'):
    """
    Add page numbers to a PDF.
    
    Args:
        pdf_path: Path to the PDF file
        output_dir: Directory to save the result
        position: Position of page numbers ('bottom', 'top', 'bottom-right', etc.)
        
    Returns:
        Path to the modified PDF
    """
    try:
        # Using pdf2image to convert pages to images
        from pdf2image import convert_from_path
        
        reader = PdfReader(pdf_path)
        writer = PdfWriter()
        
        # Convert PDF to images
        images = convert_from_path(pdf_path)
        
        # Position mapping
        positions = {
            'bottom': lambda w, h, i: (w // 2, 30),
            'top': lambda w, h, i: (w // 2, h - 30),
            'bottom-right': lambda w, h, i: (w - 50, 30),
            'bottom-left': lambda w, h, i: (50, 30),
            'top-right': lambda w, h, i: (w - 50, h - 30),
            'top-left': lambda w, h, i: (50, h - 30)
        }
        
        # Default to bottom if position not recognized
        pos_func = positions.get(position, positions['bottom'])
        
        # Add page numbers to each image
        for i, img in enumerate(images):
            width, height = img.size
            draw = ImageDraw.Draw(img)
            
            try:
                font = ImageFont.truetype("arial.ttf", 14)
            except IOError:
                font = ImageFont.load_default()
            
            # Get position for this page
            pos = pos_func(width, height, i)
            
            # Draw page number
            draw.text(pos, str(i + 1), font=font, fill=(0, 0, 0))
            
            # Convert image to PDF
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PDF')
            img_byte_arr.seek(0)
            
            # Add to writer
            page_reader = PdfReader(img_byte_arr)
            writer.add_page(page_reader.pages[0])
        
        output_path = os.path.join(output_dir, f"numbered_{uuid4().hex}.pdf")
        
        with open(output_path, "wb") as output_file:
            writer.write(output_file)
        
        return output_path
    
    except Exception as e:
        logger.error(f"Error adding page numbers to PDF: {str(e)}")
        raise Exception(f"فشل في إضافة أرقام الصفحات إلى PDF: {str(e)}")

def add_watermark(pdf_path, watermark_text, output_dir, opacity=0.3):
    """
    Add a watermark to a PDF.
    
    Args:
        pdf_path: Path to the PDF file
        watermark_text: Text for the watermark
        output_dir: Directory to save the result
        opacity: Opacity of the watermark (0-1)
        
    Returns:
        Path to the modified PDF
    """
    try:
        # Using pdf2image to convert pages to images
        from pdf2image import convert_from_path
        
        reader = PdfReader(pdf_path)
        writer = PdfWriter()
        
        # Convert PDF to images
        images = convert_from_path(pdf_path)
        
        for img in images:
            # Create a transparent layer for the watermark
            watermark = Image.new('RGBA', img.size, (255, 255, 255, 0))
            draw = ImageDraw.Draw(watermark)
            
            try:
                # Use a larger font for the watermark
                font = ImageFont.truetype("arial.ttf", 40)
            except IOError:
                font = ImageFont.load_default()
            
            # Get text size
            text_width, text_height = draw.textsize(watermark_text, font=font)
            
            # Calculate position to place the text in the center
            x = (img.width - text_width) // 2
            y = (img.height - text_height) // 2
            
            # Draw the watermark text
            draw.text((x, y), watermark_text, font=font, fill=(0, 0, 0, int(255 * opacity)))
            
            # Apply the watermark to the image
            img = Image.alpha_composite(img.convert('RGBA'), watermark)
            img = img.convert('RGB')  # Convert back to RGB for PDF
            
            # Convert image to PDF
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PDF')
            img_byte_arr.seek(0)
            
            # Add to writer
            page_reader = PdfReader(img_byte_arr)
            writer.add_page(page_reader.pages[0])
        
        output_path = os.path.join(output_dir, f"watermarked_{uuid4().hex}.pdf")
        
        with open(output_path, "wb") as output_file:
            writer.write(output_file)
        
        return output_path
    
    except Exception as e:
        logger.error(f"Error adding watermark to PDF: {str(e)}")
        raise Exception(f"فشل في إضافة علامة مائية إلى PDF: {str(e)}")

def change_background(pdf_path, background_path, output_dir):
    """
    Change the background of a PDF.
    
    Args:
        pdf_path: Path to the PDF file
        background_path: Path to the background image
        output_dir: Directory to save the result
        
    Returns:
        Path to the modified PDF
    """
    try:
        # Using pdf2image to convert pages to images
        from pdf2image import convert_from_path
        
        reader = PdfReader(pdf_path)
        writer = PdfWriter()
        
        # Convert PDF to images
        images = convert_from_path(pdf_path)
        
        # Open background image
        background = Image.open(background_path)
        
        for img in images:
            # Resize background to match page size
            bg = background.resize(img.size)
            
            # Create a new image with the background
            new_img = Image.new('RGB', img.size)
            new_img.paste(bg)
            
            # Paste the PDF content on top
            new_img.paste(img, mask=img)
            
            # Convert image to PDF
            img_byte_arr = io.BytesIO()
            new_img.save(img_byte_arr, format='PDF')
            img_byte_arr.seek(0)
            
            # Add to writer
            page_reader = PdfReader(img_byte_arr)
            writer.add_page(page_reader.pages[0])
        
        output_path = os.path.join(output_dir, f"background_changed_{uuid4().hex}.pdf")
        
        with open(output_path, "wb") as output_file:
            writer.write(output_file)
        
        return output_path
    
    except Exception as e:
        logger.error(f"Error changing background of PDF: {str(e)}")
        raise Exception(f"فشل في تغيير خلفية PDF: {str(e)}")

def resize_pdf_pages(pdf_path, size, output_dir):
    """
    Resize pages in a PDF.
    
    Args:
        pdf_path: Path to the PDF file
        size: Tuple of (width, height) for the new size
        output_dir: Directory to save the result
        
    Returns:
        Path to the modified PDF
    """
    try:
        # Using pdf2image to convert pages to images
        from pdf2image import convert_from_path
        
        # Convert PDF to images
        images = convert_from_path(pdf_path)
        
        writer = PdfWriter()
        
        for img in images:
            # Resize the image
            resized_img = img.resize(size)
            
            # Convert image to PDF
            img_byte_arr = io.BytesIO()
            resized_img.save(img_byte_arr, format='PDF')
            img_byte_arr.seek(0)
            
            # Add to writer
            page_reader = PdfReader(img_byte_arr)
            writer.add_page(page_reader.pages[0])
        
        output_path = os.path.join(output_dir, f"resized_{uuid4().hex}.pdf")
        
        with open(output_path, "wb") as output_file:
            writer.write(output_file)
        
        return output_path
    
    except Exception as e:
        logger.error(f"Error resizing PDF pages: {str(e)}")
        raise Exception(f"فشل في تغيير حجم صفحات PDF: {str(e)}")

def change_page_orientation(pdf_path, output_dir):
    """
    Change page orientation in a PDF (portrait <-> landscape).
    
    Args:
        pdf_path: Path to the PDF file
        output_dir: Directory to save the result
        
    Returns:
        Path to the modified PDF
    """
    try:
        # Using pdf2image to convert pages to images
        from pdf2image import convert_from_path
        
        # Convert PDF to images
        images = convert_from_path(pdf_path)
        
        writer = PdfWriter()
        
        for img in images:
            # Rotate image by 90 degrees to change orientation
            rotated_img = img.transpose(Image.ROTATE_90)
            
            # Convert image to PDF
            img_byte_arr = io.BytesIO()
            rotated_img.save(img_byte_arr, format='PDF')
            img_byte_arr.seek(0)
            
            # Add to writer
            page_reader = PdfReader(img_byte_arr)
            writer.add_page(page_reader.pages[0])
        
        output_path = os.path.join(output_dir, f"orientation_changed_{uuid4().hex}.pdf")
        
        with open(output_path, "wb") as output_file:
            writer.write(output_file)
        
        return output_path
    
    except Exception as e:
        logger.error(f"Error changing page orientation: {str(e)}")
        raise Exception(f"فشل في تغيير اتجاه الصفحات: {str(e)}")

def crop_pages(pdf_path, crop_box, output_dir):
    """
    Crop pages in a PDF.
    
    Args:
        pdf_path: Path to the PDF file
        crop_box: Tuple of (left, top, right, bottom) for the crop area
        output_dir: Directory to save the result
        
    Returns:
        Path to the modified PDF
    """
    try:
        # Using pdf2image to convert pages to images
        from pdf2image import convert_from_path
        
        # Convert PDF to images
        images = convert_from_path(pdf_path)
        
        writer = PdfWriter()
        
        for img in images:
            # Crop the image
            cropped_img = img.crop(crop_box)
            
            # Convert image to PDF
            img_byte_arr = io.BytesIO()
            cropped_img.save(img_byte_arr, format='PDF')
            img_byte_arr.seek(0)
            
            # Add to writer
            page_reader = PdfReader(img_byte_arr)
            writer.add_page(page_reader.pages[0])
        
        output_path = os.path.join(output_dir, f"cropped_{uuid4().hex}.pdf")
        
        with open(output_path, "wb") as output_file:
            writer.write(output_file)
        
        return output_path
    
    except Exception as e:
        logger.error(f"Error cropping PDF pages: {str(e)}")
        raise Exception(f"فشل في قص صفحات PDF: {str(e)}")

def split_pages_to_files(pdf_path, output_dir):
    """
    Split each page of a PDF into a separate file.
    
    Args:
        pdf_path: Path to the PDF file
        output_dir: Directory to save the results
        
    Returns:
        List of paths to the generated PDF files
    """
    try:
        reader = PdfReader(pdf_path)
        result_paths = []
        
        for i, page in enumerate(reader.pages):
            writer = PdfWriter()
            writer.add_page(page)
            
            output_path = os.path.join(output_dir, f"page_{i+1}_{uuid4().hex}.pdf")
            
            with open(output_path, "wb") as output_file:
                writer.write(output_file)
            
            result_paths.append(output_path)
        
        return result_paths
    
    except Exception as e:
        logger.error(f"Error splitting PDF pages to files: {str(e)}")
        raise Exception(f"فشل في تقسيم صفحات PDF إلى ملفات: {str(e)}")

def sort_pdf_pages(pdf_path, output_dir):
    """
    Sort pages in a PDF alphabetically based on content.
    
    Args:
        pdf_path: Path to the PDF file
        output_dir: Directory to save the result
        
    Returns:
        Path to the sorted PDF
    """
    try:
        reader = PdfReader(pdf_path)
        writer = PdfWriter()
        
        # Extract text from each page
        pages_with_text = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            pages_with_text.append((i, text, page))
        
        # Sort pages by text content
        sorted_pages = sorted(pages_with_text, key=lambda x: x[1])
        
        # Add pages in sorted order
        for _, _, page in sorted_pages:
            writer.add_page(page)
        
        output_path = os.path.join(output_dir, f"sorted_{uuid4().hex}.pdf")
        
        with open(output_path, "wb") as output_file:
            writer.write(output_file)
        
        return output_path
    
    except Exception as e:
        logger.error(f"Error sorting PDF pages: {str(e)}")
        raise Exception(f"فشل في فرز صفحات PDF: {str(e)}")

def add_table_of_contents(pdf_path, output_dir):
    """
    Add a table of contents to a PDF based on text analysis.
    
    Args:
        pdf_path: Path to the PDF file
        output_dir: Directory to save the result
        
    Returns:
        Path to the modified PDF
    """
    try:
        reader = PdfReader(pdf_path)
        writer = PdfWriter()
        
        # Extract potential headings from each page
        headings = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            lines = text.split('\n')
            
            # Simple heuristic: consider short lines (less than 50 chars) that don't end with punctuation as headings
            for line in lines:
                line = line.strip()
                if line and len(line) < 50 and not line[-1] in '.,:;?!)':
                    headings.append((line, i + 1))  # Store heading and page number
        
        # Create TOC page
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        toc_path = os.path.join(output_dir, "temp_toc.pdf")
        c = canvas.Canvas(toc_path, pagesize=letter)
        
        # Add title
        c.setFont("Helvetica-Bold", 16)
        c.drawString(100, 750, "Table of Contents")
        
        # Add headings
        y = 720
        c.setFont("Helvetica", 12)
        
        for heading, page_num in headings:
            if y < 100:  # Check if we need a new page
                c.showPage()
                y = 750
            
            c.drawString(100, y, f"{heading} .......................... {page_num}")
            y -= 20
        
        c.save()
        
        # Add TOC to the beginning of the PDF
        toc_reader = PdfReader(toc_path)
        
        # Add TOC pages
        for page in toc_reader.pages:
            writer.add_page(page)
        
        # Add original pages
        for page in reader.pages:
            writer.add_page(page)
        
        output_path = os.path.join(output_dir, f"with_toc_{uuid4().hex}.pdf")
        
        with open(output_path, "wb") as output_file:
            writer.write(output_file)
        
        # Clean up
        os.remove(toc_path)
        
        return output_path
    
    except Exception as e:
        logger.error(f"Error adding table of contents to PDF: {str(e)}")
        raise Exception(f"فشل في إضافة فهرس إلى PDF: {str(e)}")

def edit_pdf_metadata(pdf_path, metadata, output_dir):
    """
    Edit metadata in a PDF.
    
    Args:
        pdf_path: Path to the PDF file
        metadata: Dictionary with metadata fields
        output_dir: Directory to save the result
        
    Returns:
        Path to the modified PDF
    """
    try:
        reader = PdfReader(pdf_path)
        writer = PdfWriter()
        
        # Copy all pages
        for page in reader.pages:
            writer.add_page(page)
        
        # Update metadata
        writer.add_metadata(metadata)
        
        output_path = os.path.join(output_dir, f"metadata_edited_{uuid4().hex}.pdf")
        
        with open(output_path, "wb") as output_file:
            writer.write(output_file)
        
        return output_path
    
    except Exception as e:
        logger.error(f"Error editing PDF metadata: {str(e)}")
        raise Exception(f"فشل في تعديل بيانات الوصف للملف: {str(e)}")
