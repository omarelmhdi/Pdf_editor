import os
import logging
from uuid import uuid4
from PyPDF2 import PdfReader, PdfWriter

logger = logging.getLogger(__name__)

def merge_pdfs(pdf_files, output_dir):
    """
    Merge multiple PDF files into one.
    
    Args:
        pdf_files: List of paths to PDF files
        output_dir: Directory to save the result
        
    Returns:
        Path to the merged PDF
    """
    try:
        merger = PdfWriter()
        
        for pdf in pdf_files:
            merger.append(pdf)
        
        output_path = os.path.join(output_dir, f"merged_{uuid4().hex}.pdf")
        
        with open(output_path, "wb") as output_file:
            merger.write(output_file)
        
        return output_path
    
    except Exception as e:
        logger.error(f"Error merging PDFs: {str(e)}")
        raise Exception(f"فشل في دمج ملفات PDF: {str(e)}")

def split_pdf(pdf_path, split_points, output_dir):
    """
    Split a PDF file at specified page numbers.
    
    Args:
        pdf_path: Path to the PDF file
        split_points: List of page numbers where to split
        output_dir: Directory to save the results
        
    Returns:
        List of paths to the split PDFs
    """
    try:
        reader = PdfReader(pdf_path)
        total_pages = len(reader.pages)
        
        # Convert page numbers to 0-based indices and sort
        split_points = sorted([int(p) - 1 for p in split_points if 0 < int(p) <= total_pages])
        
        # Add start and end points
        split_ranges = []
        start_page = 0
        
        for end_page in split_points:
            split_ranges.append((start_page, end_page))
            start_page = end_page
        
        # Add the last range
        if start_page < total_pages:
            split_ranges.append((start_page, total_pages - 1))
        
        result_paths = []
        
        for i, (start, end) in enumerate(split_ranges):
            writer = PdfWriter()
            
            for page_num in range(start, end + 1):
                writer.add_page(reader.pages[page_num])
            
            output_path = os.path.join(output_dir, f"split_{i + 1}_{uuid4().hex}.pdf")
            
            with open(output_path, "wb") as output_file:
                writer.write(output_file)
            
            result_paths.append(output_path)
        
        return result_paths
    
    except Exception as e:
        logger.error(f"Error splitting PDF: {str(e)}")
        raise Exception(f"فشل في تقسيم ملف PDF: {str(e)}")

def delete_pages(pdf_path, pages_to_delete, output_dir):
    """
    Delete specified pages from a PDF.
    
    Args:
        pdf_path: Path to the PDF file
        pages_to_delete: List of page numbers to delete (1-based)
        output_dir: Directory to save the result
        
    Returns:
        Path to the resulting PDF
    """
    try:
        reader = PdfReader(pdf_path)
        writer = PdfWriter()
        
        # Convert to 0-based page indices
        pages_to_delete = [int(p) - 1 for p in pages_to_delete]
        
        for i, page in enumerate(reader.pages):
            if i not in pages_to_delete:
                writer.add_page(page)
        
        output_path = os.path.join(output_dir, f"pages_deleted_{uuid4().hex}.pdf")
        
        with open(output_path, "wb") as output_file:
            writer.write(output_file)
        
        return output_path
    
    except Exception as e:
        logger.error(f"Error deleting pages: {str(e)}")
        raise Exception(f"فشل في حذف الصفحات: {str(e)}")

def reorder_pages(pdf_path, new_order, output_dir):
    """
    Reorder pages in a PDF.
    
    Args:
        pdf_path: Path to the PDF file
        new_order: List of page numbers in the desired order (1-based)
        output_dir: Directory to save the result
        
    Returns:
        Path to the reordered PDF
    """
    try:
        reader = PdfReader(pdf_path)
        writer = PdfWriter()
        
        # Convert to 0-based page indices
        new_order = [int(p) - 1 for p in new_order]
        
        # Validate page numbers
        total_pages = len(reader.pages)
        for page_num in new_order:
            if page_num < 0 or page_num >= total_pages:
                raise ValueError(f"رقم الصفحة {page_num + 1} خارج النطاق. الملف يحتوي على {total_pages} صفحة فقط.")
        
        for page_num in new_order:
            writer.add_page(reader.pages[page_num])
        
        output_path = os.path.join(output_dir, f"reordered_{uuid4().hex}.pdf")
        
        with open(output_path, "wb") as output_file:
            writer.write(output_file)
        
        return output_path
    
    except Exception as e:
        logger.error(f"Error reordering pages: {str(e)}")
        raise Exception(f"فشل في إعادة ترتيب الصفحات: {str(e)}")

def rotate_pages(pdf_path, angle, pages_to_rotate, output_dir):
    """
    Rotate pages in a PDF.
    
    Args:
        pdf_path: Path to the PDF file
        angle: Rotation angle (90, 180, 270)
        pages_to_rotate: List of page numbers to rotate (1-based) or 'all'
        output_dir: Directory to save the result
        
    Returns:
        Path to the rotated PDF
    """
    try:
        reader = PdfReader(pdf_path)
        writer = PdfWriter()
        
        total_pages = len(reader.pages)
        
        # Handle 'all' case
        if pages_to_rotate == 'all':
            pages_to_rotate = list(range(1, total_pages + 1))
        
        # Convert to 0-based page indices
        pages_to_rotate = [int(p) - 1 for p in pages_to_rotate]
        
        for i, page in enumerate(reader.pages):
            if i in pages_to_rotate:
                page.rotate(angle)
            writer.add_page(page)
        
        output_path = os.path.join(output_dir, f"rotated_{uuid4().hex}.pdf")
        
        with open(output_path, "wb") as output_file:
            writer.write(output_file)
        
        return output_path
    
    except Exception as e:
        logger.error(f"Error rotating pages: {str(e)}")
        raise Exception(f"فشل في تدوير الصفحات: {str(e)}")

def add_pages_to_pdf(original_pdf_path, pages_pdf_path, output_dir, position='end'):
    """
    Add pages from one PDF to another PDF.
    
    Args:
        original_pdf_path: Path to the original PDF file
        pages_pdf_path: Path to the PDF file with pages to add
        output_dir: Directory to save the result
        position: Where to add the pages ('start', 'end', or specific page number as integer)
        
    Returns:
        Path to the modified PDF
    """
    try:
        # قراءة ملفات PDF
        original_pdf = PdfReader(original_pdf_path)
        pages_pdf = PdfReader(pages_pdf_path)
        
        writer = PdfWriter()
        
        # تحويل موضع الإدراج (position) إلى النوع المناسب
        position_type = type(position)
        
        if position == 'start':
            # إضافة الصفحات الجديدة أولاً
            for page in pages_pdf.pages:
                writer.add_page(page)
            # ثم إضافة صفحات الملف الأصلي
            for page in original_pdf.pages:
                writer.add_page(page)
        
        elif position == 'end':
            # إضافة صفحات الملف الأصلي أولاً
            for page in original_pdf.pages:
                writer.add_page(page)
            # ثم إضافة الصفحات الجديدة
            for page in pages_pdf.pages:
                writer.add_page(page)
        
        else:
            # تحويل النص إلى رقم إذا لزم الأمر
            if isinstance(position, str) and position.isdigit():
                position = int(position)
            
            # التحقق من المدى
            if isinstance(position, int) and (position < 0 or position > len(original_pdf.pages)):
                # إذا كان الموضع خارج النطاق، نضيف الصفحات في النهاية
                for page in original_pdf.pages:
                    writer.add_page(page)
                for page in pages_pdf.pages:
                    writer.add_page(page)
            else:
                # إضافة صفحات الملف الأصلي حتى موضع الإدراج (مع اعتبار أن position هو الآن int)
                pos = int(position)  # تحويل مؤكد للرقم
                for i in range(pos):
                    writer.add_page(original_pdf.pages[i])
                
                # إضافة الصفحات الجديدة
                for page in pages_pdf.pages:
                    writer.add_page(page)
                
                # إضافة باقي صفحات الملف الأصلي
                for i in range(pos, len(original_pdf.pages)):
                    writer.add_page(original_pdf.pages[i])
        
        # حفظ النتيجة
        output_path = os.path.join(output_dir, f"added_pages_{uuid4().hex}.pdf")
        
        with open(output_path, "wb") as output_file:
            writer.write(output_file)
        
        return output_path
        
    except Exception as e:
        logger.error(f"Error adding pages to PDF: {str(e)}")
        raise Exception(f"فشل في إضافة صفحات إلى الملف: {str(e)}")
