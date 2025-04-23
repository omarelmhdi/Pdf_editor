from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
import os
import re
from PyPDF2 import PdfReader, PdfWriter
from utils import create_temp_dir, clean_temp_files
from config import MAX_FILE_SIZE

def start(update: Update, context: CallbackContext):
    """Send a message when the command /start is issued."""
    # تتبع المستخدمين وإشعار المدير بالمستخدمين الجدد
    from user_tracking import get_or_create_user, notify_admin_new_user
    
    user = update.effective_user
    is_new_user = get_or_create_user(user)
    
    # إرسال إشعار للمدير إذا كان المستخدم جديد
    if is_new_user:
        notify_admin_new_user(context.bot, user)
    
    keyboard = [
        [
            InlineKeyboardButton("حساب المطور", url='t.me/mavdiii'),
            InlineKeyboardButton("قناة المطور", url='t.me/pivloo')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        'مساء الفل 🥰\n'
        'لو كنت بتدور على بوت بيعدل ملفات PDF بجميع الميزات الإحترافية وبشكل مجاني تماما فإنت فالمكان الصح\n'
        '📌 يمكنك :\n'
        ' – دمج أو تقسيم ملفات\n'
        '– حذف أو ترتيب الصفحات\n'
        '– تحويل PDF إلى صور أو Word\n'
        '_ تحويل ال PDF إلى صور\n'
        '– إضافة توقيع، نصوص، أو ترقيم الصفحات\n'
        '– واختيارات أخرى كتيرة ومفيدة اكتشفها بنفسك\n\n'
        'استخدم الأمر /help لعرض جميع الأدوات المتاحة وطريقة استخدامها.',
        reply_markup=reply_markup
    )

def help_command(update: Update, context: CallbackContext):
    """Send a message when the command /help is issued."""
    keyboard = [
        [InlineKeyboardButton("العمليات الأساسية 🧩", callback_data='help_basic'), 
         InlineKeyboardButton("عمليات التحويل 🔄", callback_data='help_convert')],
        [InlineKeyboardButton("🤖 استخراج المحتوى", callback_data='help_extract'), 
         InlineKeyboardButton("تعديل الملف 📂", callback_data='help_edit')],
        [InlineKeyboardButton("التنسيق والصفحات 📐", callback_data='help_format'), 
         InlineKeyboardButton("📄 إعدادات ومعلومات", callback_data='help_settings')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        'اختر القسم الذي تريد عرض الأوامر المتاحة فيه:',
        reply_markup=reply_markup
    )

def merge_command(update: Update, context: CallbackContext):
    """Handle PDF merge command"""
    context.user_data['current_operation'] = 'merge'
    update.message.reply_text('أرسل ملفات PDF للدمج. عندما تنتهي، أرسل /done')

def split_command(update: Update, context: CallbackContext):
    """Handle PDF split command"""
    context.user_data['current_operation'] = 'split'
    update.message.reply_text('أرسل ملف PDF للتقسيم')

def handle_document(update: Update, context: CallbackContext):
    """Handle received documents"""
    file = update.message.document

    if file.file_size > MAX_FILE_SIZE:
        update.message.reply_text('عذراً، حجم الملف كبير جداً. الحد الأقصى هو 20 ميجابايت.')
        return

    user_id = update.effective_user.id
    user_dir = create_temp_dir(user_id)
    file_path = os.path.join(user_dir, file.file_name)

    # Download file
    doc_file = context.bot.get_file(file.file_id)
    doc_file.download(custom_path=file_path)

    update.message.reply_text('تم استلام الملف بنجاح! جاري المعالجة...')

    current_operation = context.user_data.get('current_operation')
    
    # عمليات دمج الملفات (تتطلب ملفات متعددة)
    if current_operation == 'merge':
        if not 'merge_files' in context.user_data:
            context.user_data['merge_files'] = []
        context.user_data['merge_files'].append(file_path)
        update.message.reply_text('تم إضافة الملف. أرسل المزيد من الملفات أو أرسل /done للدمج')
    
    # تحويل PDF إلى صور
    elif current_operation == 'pdf_to_images':
        try:
            from file_conversions import pdf_to_images
            output_dir = create_temp_dir(user_id)
            image_paths = pdf_to_images(file_path, output_dir)
            
            # إرسال جميع الصور بغض النظر عن عددها
            update.message.reply_text(f'الملف يحتوي على {len(image_paths)} صفحة. جاري إرسال الصور...')
            # نرسل كل الصور كملفات منفصلة
            for i, img_path in enumerate(image_paths):
                with open(img_path, 'rb') as img_file:
                    update.message.reply_document(
                        document=img_file,
                        filename=f'page_{i+1}.png',
                        caption=f'صفحة {i+1} من {len(image_paths)}'
                    )
            
            update.message.reply_text('تم تحويل ملف PDF إلى صور بنجاح!')
        except Exception as e:
            update.message.reply_text(f'حدث خطأ أثناء تحويل PDF إلى صور: {str(e)}')
    
    # تحويل PDF إلى Word
    elif current_operation == 'pdf_to_word':
        try:
            from file_conversions import pdf_to_word
            output_dir = create_temp_dir(user_id)
            output_path = pdf_to_word(file_path, output_dir)
            
            with open(output_path, 'rb') as doc_file:
                update.message.reply_document(
                    document=doc_file,
                    filename=os.path.basename(output_path),
                    caption='تم تحويل ملف PDF إلى Word بنجاح'
                )
        except Exception as e:
            update.message.reply_text(f'حدث خطأ أثناء تحويل PDF إلى Word: {str(e)}')
    
    # تحويل PDF إلى Excel
    elif current_operation == 'pdf_to_excel':
        try:
            from file_conversions import pdf_to_excel
            output_dir = create_temp_dir(user_id)
            output_path = pdf_to_excel(file_path, output_dir)
            
            with open(output_path, 'rb') as excel_file:
                update.message.reply_document(
                    document=excel_file,
                    filename=os.path.basename(output_path),
                    caption='تم تحويل ملف PDF إلى Excel بنجاح'
                )
        except Exception as e:
            update.message.reply_text(f'حدث خطأ أثناء تحويل PDF إلى Excel: {str(e)}')
    
    # تحويل PDF إلى PowerPoint
    elif current_operation == 'pdf_to_ppt':
        try:
            from file_conversions import pdf_to_ppt
            output_dir = create_temp_dir(user_id)
            output_path = pdf_to_ppt(file_path, output_dir)
            
            with open(output_path, 'rb') as ppt_file:
                update.message.reply_document(
                    document=ppt_file,
                    filename=os.path.basename(output_path),
                    caption='تم تحويل ملف PDF إلى PowerPoint بنجاح'
                )
        except Exception as e:
            update.message.reply_text(f'حدث خطأ أثناء تحويل PDF إلى PowerPoint: {str(e)}')
    
    # تحويل Word إلى PDF
    elif current_operation == 'word_to_pdf':
        try:
            from file_conversions import word_to_pdf
            output_dir = create_temp_dir(user_id)
            output_path = word_to_pdf(file_path, output_dir)
            
            with open(output_path, 'rb') as pdf_file:
                update.message.reply_document(
                    document=pdf_file,
                    filename=os.path.basename(output_path),
                    caption='تم تحويل ملف Word إلى PDF بنجاح'
                )
        except Exception as e:
            update.message.reply_text(f'حدث خطأ أثناء تحويل Word إلى PDF: {str(e)}')
            
    # استخراج النص من PDF
    elif current_operation == 'extract_text':
        try:
            from content_extraction import extract_text
            text = extract_text(file_path)
            
            # إذا كان النص طويلاً، نقسمه إلى أجزاء
            if len(text) > 4000:
                chunks = [text[i:i+4000] for i in range(0, len(text), 4000)]
                for i, chunk in enumerate(chunks):
                    update.message.reply_text(f'جزء {i+1} من {len(chunks)}:\n\n{chunk}')
            else:
                update.message.reply_text(f'النص المستخرج:\n\n{text}')
        except Exception as e:
            update.message.reply_text(f'حدث خطأ أثناء استخراج النص: {str(e)}')
            
    # حذف صفحات من PDF
    elif current_operation == 'delete_pages':
        try:
            # قراءة عدد صفحات الملف
            with open(file_path, 'rb') as pdf_file:
                pdf_reader = PdfReader(pdf_file)
                num_pages = len(pdf_reader.pages)
            
            update.message.reply_text(f'تم استلام ملف PDF مكون من {num_pages} صفحة')
            
            # نخزن مسار الملف للمعالجة اللاحقة
            context.user_data['delete_file'] = file_path
            context.user_data['pdf_num_pages'] = num_pages
            
            # نسأل المستخدم عن الصفحات التي يريد حذفها
            update.message.reply_text('أدخل أرقام الصفحات التي تريد حذفها، مفصولة بفواصل (مثال: 1,3,5)')
            context.user_data['awaiting_delete_pages'] = True
        except Exception as e:
            update.message.reply_text(f'حدث خطأ أثناء تحضير الملف لحذف الصفحات: {str(e)}')
            
    # إضافة صفحات إلى ملف PDF
    elif current_operation == 'add_pages':
        try:
            # تحقق من خطوة العملية
            add_pages_step = context.user_data.get('add_pages_step')
            
            if add_pages_step == 'original_pdf':
                # قراءة عدد صفحات الملف الأصلي
                with open(file_path, 'rb') as pdf_file:
                    pdf_reader = PdfReader(pdf_file)
                    num_pages = len(pdf_reader.pages)
                
                update.message.reply_text(f'تم استلام الملف الأصلي المكون من {num_pages} صفحة')
                
                # حفظ مسار الملف الأصلي وعدد صفحاته
                context.user_data['original_pdf'] = file_path
                context.user_data['original_pdf_pages'] = num_pages
                
                # تغيير الخطوة للحصول على صورة للإضافة
                context.user_data['add_pages_step'] = 'pages_pdf'
                update.message.reply_text('الآن أرسل صورة تريد إضافتها إلى الملف كصفحة جديدة')
            
            elif add_pages_step == 'pages_pdf':
                # في هذه الخطوة نطلب صورة بدلاً من ملف PDF
                # نغير الرسالة لإعلام المستخدم أن عليه إرسال صورة
                update.message.reply_text('الآن أرسل صورة تريد إضافتها إلى الملف')
            
        except Exception as e:
            update.message.reply_text(f'حدث خطأ أثناء تحضير الملفات لإضافة الصفحات: {str(e)}')
    
    # تقسيم ملف PDF
    elif current_operation == 'split':
        try:
            # قراءة عدد صفحات الملف
            with open(file_path, 'rb') as pdf_file:
                pdf_reader = PdfReader(pdf_file)
                num_pages = len(pdf_reader.pages)
            
            update.message.reply_text(f'تم استلام ملف PDF مكون من {num_pages} صفحة')
            
            # نخزن مسار الملف للمعالجة اللاحقة
            context.user_data['split_file'] = file_path
            context.user_data['pdf_num_pages'] = num_pages
            
            # نسأل المستخدم عن نقاط التقسيم
            # على سبيل المثال: 1,3,5 لتقسيم الملف بعد الصفحات 1 و3 و5
            update.message.reply_text('أدخل أرقام الصفحات التي تريد التقسيم عندها، مفصولة بفواصل (مثال: 1,3,5)')
            context.user_data['awaiting_split_points'] = True
        except Exception as e:
            update.message.reply_text(f'حدث خطأ أثناء تحضير الملف للتقسيم: {str(e)}')

def handle_photo(update: Update, context: CallbackContext):
    """Handle received photos"""
    photo = update.message.photo[-1]  # أكبر حجم متاح للصورة
    user_id = update.effective_user.id
    user_dir = create_temp_dir(user_id)
    
    # تنزيل الصورة
    photo_file = context.bot.get_file(photo.file_id)
    photo_path = os.path.join(user_dir, f'photo_{photo.file_id}.jpg')
    photo_file.download(custom_path=photo_path)
    
    current_operation = context.user_data.get('current_operation')
    if current_operation == 'photo_to_pdf':
        if 'photos' not in context.user_data:
            context.user_data['photos'] = []
        context.user_data['photos'].append(photo_path)
        update.message.reply_text('تم استلام الصورة. أرسل المزيد من الصور أو أرسل /done للتحويل إلى PDF')
    
    # معالجة إضافة صفحات (صور) إلى ملف PDF
    elif current_operation == 'add_pages':
        add_pages_step = context.user_data.get('add_pages_step')
        
        if add_pages_step == 'pages_pdf':
            # تحويل الصورة إلى PDF
            from file_conversions import photos_to_pdf
            output_dir = create_temp_dir(user_id)
            
            # نستخدم الصورة الواحدة لإنشاء ملف PDF
            temp_photos = [photo_path]
            temp_pdf_path = photos_to_pdf(temp_photos, output_dir)
            
            # نخزن مسار ملف PDF الذي تم إنشاؤه من الصورة
            context.user_data['pages_pdf'] = temp_pdf_path
            
            # نسأل المستخدم عن موضع إضافة الصورة
            original_pdf_pages = context.user_data.get('original_pdf_pages', 0)
            update.message.reply_text(f'تم استلام الصورة بنجاح. الملف الأصلي يحتوي على {original_pdf_pages} صفحة.')
            
            # أزرار للاختيار بين البداية أو النهاية أو موضع محدد
            keyboard = [
                [InlineKeyboardButton("في بداية الملف", callback_data='add_pages_start')],
                [InlineKeyboardButton("في نهاية الملف", callback_data='add_pages_end')],
                [InlineKeyboardButton("في موضع محدد", callback_data='add_pages_position')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text('أين تريد إضافة هذه الصورة؟', reply_markup=reply_markup)
        else:
            # إذا لم يتم تحديد خطوة أو كانت الخطوة خاطئة
            update.message.reply_text('يرجى إرسال ملف PDF الأصلي أولاً باستخدام الأمر /add_pages')
        
    else:
        update.message.reply_text('تم استلام الصورة. سيتم تحويلها إلى PDF قريباً...')

def handle_text(update: Update, context: CallbackContext):
    """Handle text messages"""
    text = update.message.text
    
    # إذا كان المستخدم في مرحلة انتظار موضع إضافة الصفحات
    if context.user_data.get('add_pages_awaiting_position'):
        try:
            # التحقق من صحة الرقم المدخل
            if not text.isdigit():
                update.message.reply_text('الرجاء إدخال رقم صفحة صالح.')
                return
            
            position = int(text)
            
            # استخراج مسارات الملفات من بيانات المستخدم
            original_pdf = context.user_data.get('original_pdf')
            pages_pdf = context.user_data.get('pages_pdf')
            original_pdf_pages = context.user_data.get('original_pdf_pages', 0)
            
            if not original_pdf or not pages_pdf:
                update.message.reply_text('يبدو أن هناك خطأ. يرجى بدء العملية من جديد باستخدام الأمر /add_pages')
                context.user_data.clear()
                return
            
            # التحقق من صحة رقم الصفحة
            if position < 0 or position > original_pdf_pages:
                update.message.reply_text(f'رقم الصفحة غير صالح. يجب أن يكون بين 0 و {original_pdf_pages}')
                return
            
            # إضافة الصفحات في الموضع المحدد
            from pdf_operations import add_pages_to_pdf
            output_dir = create_temp_dir(update.effective_user.id)
            
            update.message.reply_text(f'جاري إضافة الصفحات بعد الصفحة رقم {position}...')
            output_path = add_pages_to_pdf(original_pdf, pages_pdf, output_dir, position=position)
            
            # إرسال الملف النهائي
            with open(output_path, 'rb') as file:
                update.message.reply_document(
                    document=file,
                    filename='document_with_added_image.pdf',
                    caption=f'تم إضافة الصورة بعد الصفحة رقم {position} بنجاح'
                )
            
            # تنظيف البيانات
            context.user_data.clear()
            
        except Exception as e:
            update.message.reply_text(f'حدث خطأ أثناء إضافة الصفحات: {str(e)}')
            context.user_data.clear()
    
    # إذا كان المستخدم في مرحلة انتظار الصفحات المراد حذفها
    elif context.user_data.get('awaiting_delete_pages'):
        try:
            # معالجة أرقام الصفحات المدخلة (مثل "1,3,5")
            pages_to_delete = []
            for page in text.split(','):
                page = page.strip()
                if page.isdigit():
                    pages_to_delete.append(int(page))
            
            if not pages_to_delete:
                update.message.reply_text('لم يتم إدخال أرقام صفحات صالحة. الرجاء إدخال أرقام مفصولة بفواصل.')
                return
            
            # التحقق من أن أرقام الصفحات ضمن نطاق صفحات الملف
            num_pages = context.user_data.get('pdf_num_pages', 0)
            valid_pages = [p for p in pages_to_delete if 1 <= p <= num_pages]
            
            if not valid_pages:
                update.message.reply_text(f'أرقام الصفحات يجب أن تكون بين 1 و {num_pages}.')
                return
            
            update.message.reply_text(f'تم استلام أرقام الصفحات: {valid_pages}. جاري حذف الصفحات...')
            
            # إجراء الحذف الفعلي
            from pdf_operations import delete_pages
            file_path = context.user_data.get('delete_file')
            output_dir = create_temp_dir(update.effective_user.id)
            
            result_file = delete_pages(file_path, valid_pages, output_dir)
            
            # إرسال الملف النهائي
            with open(result_file, 'rb') as file:
                update.message.reply_document(
                    document=file,
                    filename='document_with_deleted_pages.pdf',
                    caption=f'تم حذف {len(valid_pages)} صفحة/صفحات بنجاح'
                )
            
            # تنظيف البيانات
            context.user_data.clear()
            
        except Exception as e:
            update.message.reply_text(f'حدث خطأ أثناء حذف الصفحات: {str(e)}')
            context.user_data.clear()
    
    # إذا كان المستخدم في مرحلة انتظار نقاط التقسيم
    elif context.user_data.get('awaiting_split_points'):
        try:
            # معالجة نقاط التقسيم المدخلة (مثل "1,3,5")
            split_points = []
            for point in text.split(','):
                point = point.strip()
                if point.isdigit():
                    split_points.append(int(point))
            
            if not split_points:
                update.message.reply_text('لم يتم إدخال أرقام صفحات صالحة. الرجاء إدخال أرقام مفصولة بفواصل.')
                return
            
            # التحقق من أن نقاط التقسيم ضمن نطاق صفحات الملف
            num_pages = context.user_data.get('pdf_num_pages', 0)
            valid_points = [p for p in split_points if 1 <= p < num_pages]
            
            if not valid_points:
                update.message.reply_text(f'نقاط التقسيم يجب أن تكون بين 1 و {num_pages-1}.')
                return
            
            update.message.reply_text(f'تم استلام نقاط التقسيم: {valid_points}. جاري تقسيم الملف...')
            
            # إجراء التقسيم الفعلي
            from pdf_operations import split_pdf
            file_path = context.user_data.get('split_file')
            output_dir = create_temp_dir(update.effective_user.id)
            
            result_files = split_pdf(file_path, valid_points, output_dir)
            
            # إرسال الملفات المقسمة
            update.message.reply_text(f'تم تقسيم الملف إلى {len(result_files)} أجزاء. جاري إرسال الأجزاء...')
            
            for i, path in enumerate(result_files):
                with open(path, 'rb') as file:
                    update.message.reply_document(
                        document=file,
                        filename=f'part_{i+1}.pdf',
                        caption=f'الجزء {i+1} من {len(result_files)}'
                    )
            
            # تنظيف البيانات
            context.user_data.clear()
            
        except Exception as e:
            update.message.reply_text(f'حدث خطأ أثناء تقسيم الملف: {str(e)}')
            context.user_data.clear()
    
    # إذا لم يكن المستخدم في مرحلة انتظار أي إدخال خاص
    else:
        update.message.reply_text('لا أفهم هذه الرسالة. استخدم /help لمعرفة الأوامر المتاحة.')

def handle_done(update: Update, context: CallbackContext):
    """Handle completion of multi-file operations"""
    user_id = update.effective_user.id
    current_operation = context.user_data.get('current_operation')
    
    if current_operation == 'merge' and 'merge_files' in context.user_data:
        merge_files = context.user_data['merge_files']
        if len(merge_files) > 1:
            from pdf_operations import merge_pdfs
            output_dir = create_temp_dir(user_id)
            output_path = merge_pdfs(merge_files, output_dir)
            
            # إرسال الملف المدمج
            with open(output_path, 'rb') as file:
                update.message.reply_document(
                    document=file,
                    filename='merged_document.pdf',
                    caption='تم دمج ملفات PDF بنجاح'
                )
        else:
            update.message.reply_text('يجب إرسال ملفين على الأقل للدمج.')
    elif current_operation == 'photo_to_pdf' and 'photos' in context.user_data:
        photos = context.user_data['photos']
        if len(photos) > 0:
            from file_conversions import photos_to_pdf
            output_dir = create_temp_dir(user_id)
            output_path = photos_to_pdf(photos, output_dir)
            
            # إرسال ملف PDF المنشأ من الصور
            with open(output_path, 'rb') as file:
                update.message.reply_document(
                    document=file,
                    filename='photos_to_pdf.pdf',
                    caption='تم تحويل الصور إلى PDF بنجاح'
                )
        else:
            update.message.reply_text('لم يتم استلام أي صور للتحويل.')
    else:
        update.message.reply_text('تم إكمال العملية!')
    
    # تنظيف البيانات والملفات المؤقتة
    context.user_data.clear()
    clean_temp_files(user_id)

def cancel(update: Update, context: CallbackContext):
    """Cancel current operation"""
    context.user_data.clear()
    update.message.reply_text('تم إلغاء العملية الحالية')
    clean_temp_files(update.effective_user.id)

def button_callback(update: Update, context: CallbackContext):
    """Handle button presses"""
    query = update.callback_query
    query.answer()

    # معالجة أزرار القائمة الرئيسية
    if query.data == 'convert_pdf':
        query.message.reply_text('أرسل الملف الذي تريد تحويله')
    elif query.data == 'merge_pdf':
        merge_command(query, context)
    elif query.data == 'split_pdf':
        split_command(query, context)
    elif query.data == 'compress_pdf':
        query.message.reply_text('أرسل ملف PDF للضغط')
    
    # معالجة أزرار إضافة الصفحات
    elif query.data == 'add_pages_start':
        try:
            # استخراج مسارات الملفات من بيانات المستخدم
            original_pdf = context.user_data.get('original_pdf')
            pages_pdf = context.user_data.get('pages_pdf')
            
            if not original_pdf or not pages_pdf:
                query.message.reply_text('يبدو أن هناك خطأ. يرجى بدء العملية من جديد باستخدام الأمر /add_pages')
                context.user_data.clear()
                return
            
            # إضافة الصفحات في بداية الملف
            from pdf_operations import add_pages_to_pdf
            output_dir = create_temp_dir(query.from_user.id)
            
            query.message.reply_text('جاري إضافة الصفحات في بداية الملف...')
            output_path = add_pages_to_pdf(original_pdf, pages_pdf, output_dir, position='start')
            
            # إرسال الملف النهائي
            with open(output_path, 'rb') as file:
                query.message.reply_document(
                    document=file,
                    filename='document_with_added_pages.pdf',
                    caption='تم إضافة الصفحات في بداية الملف بنجاح'
                )
            
            # تنظيف البيانات
            context.user_data.clear()
            
        except Exception as e:
            query.message.reply_text(f'حدث خطأ أثناء إضافة الصفحات: {str(e)}')
            context.user_data.clear()
    
    elif query.data == 'add_pages_end':
        try:
            # استخراج مسارات الملفات من بيانات المستخدم
            original_pdf = context.user_data.get('original_pdf')
            pages_pdf = context.user_data.get('pages_pdf')
            
            if not original_pdf or not pages_pdf:
                query.message.reply_text('يبدو أن هناك خطأ. يرجى بدء العملية من جديد باستخدام الأمر /add_pages')
                context.user_data.clear()
                return
            
            # إضافة الصفحات في نهاية الملف
            from pdf_operations import add_pages_to_pdf
            output_dir = create_temp_dir(query.from_user.id)
            
            query.message.reply_text('جاري إضافة الصفحات في نهاية الملف...')
            output_path = add_pages_to_pdf(original_pdf, pages_pdf, output_dir, position='end')
            
            # إرسال الملف النهائي
            with open(output_path, 'rb') as file:
                query.message.reply_document(
                    document=file,
                    filename='document_with_added_pages.pdf',
                    caption='تم إضافة الصفحات في نهاية الملف بنجاح'
                )
            
            # تنظيف البيانات
            context.user_data.clear()
            
        except Exception as e:
            query.message.reply_text(f'حدث خطأ أثناء إضافة الصفحات: {str(e)}')
            context.user_data.clear()
    
    elif query.data == 'add_pages_position':
        # سؤال المستخدم عن رقم الصفحة المحددة
        context.user_data['add_pages_awaiting_position'] = True
        query.message.reply_text('أدخل رقم الصفحة التي تريد إضافة الصفحات بعدها:')
    
    # معالجة أزرار المساعدة
    elif query.data == 'help_basic':
        help_text = (
            "*🧩 العمليات الأساسية*\n\n"
            "`/merge` \- دمج كذا ملفات فى ملف واحد \n"
            "`/split` \-  تقسيم الملف إلى صفحات أو أجزاء زي ما تحب \n"
            "`/add_pages` \- إضافة صفحات إلى الملف \n"
            "`/delete_pages` \- حذف صفحات معينة من الملف\n"
            "`/reorder` \- إعادة ترتيب الصفحات يدويًا\n"
            "`/rotate` \- تدوير صفحة أو مجموعة صفحات وتغيير الزوايا\n"
        )
        query.message.reply_text(help_text, parse_mode='MarkdownV2')
    
    elif query.data == 'help_convert':
        help_text = (
            "*عمليات التحويل 🔄*\n\n"
            "`/photo_to_pdf` \- تحويل الصور إلى PDF  \n"
            "`/pdf_to_images` \- تحويل PDF إلى صور \n"
            "`/pdf_to_word` \- تحويل PDF إلى Word\n"
            "`/pdf_to_excel` \- تحويل PDF إلى Excel\n"
            "`/pdf_to_ppt` \- تحويل PDF إلى PowerPoint\n"
            "`/word_to_pdf` \- تحويل Word إلى PDF\n"
            "`/excel_to_pdf` \- تحويل Excel إلى PDF\n"
            "`/ppt_to_pdf` \- تحويل PowerPoint إلى PDF\n"
        )
        query.message.reply_text(help_text, parse_mode='MarkdownV2')
    
    elif query.data == 'help_extract':
        help_text = (
            "*🤖 استخراج المحتوى*\n\n"
            "`/extract_images` \- استخراج الصور من PDF\n"
            "`/extract_text` \- استخراج النصوص من PDF\n"
        )
        query.message.reply_text(help_text, parse_mode='MarkdownV2')
    
    elif query.data == 'help_edit':
        help_text = (
            "*أوامر تعديل الملف 📂*\n\n"
            "`/add_text` \- إضافة نص داخل الصفحة\n"
            "`/add_image` \- إضافة صورة مثل التوقيع\n"
            "`/add_note` \- إضافة تعليق أو ملاحظة\n"
            "`/add_link` \- إضافة رابط إلى نص أو صورة\n"
            "`/add_numbers` \- ترقيم صفحات الملف\n"
            "`/watermark` \- إضافة علامة مائية\n"
            "`/background` \- تعيين خلفية للصفحات\n"
        )
        query.message.reply_text(help_text, parse_mode='MarkdownV2')
    
    elif query.data == 'help_format':
        help_text = (
            "*📐 التنسيق والصفحات*\n\n"
            "`/resize_pages` \- تغيير حجم الصفحات\n"
            "`/page_orientation` \- تغيير اتجاه الصفحات\n"
            "`/crop` \- قص حواف الصفحات\n"
            "`/split_pages` \- تحويل كل صفحة إلى ملف مستقل\n"
            "`/sort_pages` \- فرز الصفحات حسب الترتيب\n"
            "`/add_toc` \- إنشاء فهرس \\(جدول محتويات\\)\n"
        )
        query.message.reply_text(help_text, parse_mode='MarkdownV2')
    
    elif query.data == 'help_settings':
        help_text = (
            "*📄 إعدادات ومعلومات*\n\n"
            "`/edit_metadata` \- تعديل معلومات الملف \\(عنوان، مؤلف\\.\\.\\.\\)\n"
            "`/file_info` \- عرض تفاصيل الملف\n"
            "`/rename` \- تغيير اسم الملف النهائي\n"
            "`/auto_delete` \- تفعيل حذف الملفات بعد فترة\n"
            "`/cancel` \\- إلغاء العملية الحالية\n"
        )
        query.message.reply_text(help_text, parse_mode='MarkdownV2')

# Basic PDF operations
def add_pages_command(update: Update, context: CallbackContext):
    """Handler for adding pages to PDF"""
    context.user_data['current_operation'] = 'add_pages'
    context.user_data['add_pages_step'] = 'original_pdf'
    update.message.reply_text('أرسل ملف PDF الأصلي الذي تريد إضافة صفحات إليه')

def delete_pages_command(update: Update, context: CallbackContext):
    """Handler for deleting pages from PDF"""
    context.user_data['current_operation'] = 'delete_pages'
    update.message.reply_text('أرسل ملف PDF لحذف صفحات منه')

def reorder_command(update: Update, context: CallbackContext):
    """Handler for reordering pages in PDF"""
    context.user_data['current_operation'] = 'reorder'
    update.message.reply_text('أرسل ملف PDF لإعادة ترتيب صفحاته')

def rotate_command(update: Update, context: CallbackContext):
    """Handler for rotating pages in PDF"""
    context.user_data['current_operation'] = 'rotate'
    update.message.reply_text('أرسل ملف PDF لتدوير صفحاته')

# Conversion operations
def photo_to_pdf_command(update: Update, context: CallbackContext):
    """Handler for converting photos to PDF"""
    context.user_data['current_operation'] = 'photo_to_pdf'
    update.message.reply_text('أرسل الصور التي تريد تحويلها إلى PDF. عندما تنتهي، أرسل /done')

def pdf_to_images_command(update: Update, context: CallbackContext):
    """Handler for converting PDF to images"""
    context.user_data['current_operation'] = 'pdf_to_images'
    update.message.reply_text('أرسل ملف PDF لتحويله إلى صور')

def pdf_to_word_command(update: Update, context: CallbackContext):
    """Handler for converting PDF to Word"""
    context.user_data['current_operation'] = 'pdf_to_word'
    update.message.reply_text('أرسل ملف PDF لتحويله إلى ملف Word. سيتم معالجة الملف فور استلامه.')

def pdf_to_excel_command(update: Update, context: CallbackContext):
    """Handler for converting PDF to Excel"""
    context.user_data['current_operation'] = 'pdf_to_excel'
    update.message.reply_text('أرسل ملف PDF لتحويله إلى ملف Excel')

def pdf_to_ppt_command(update: Update, context: CallbackContext):
    """Handler for converting PDF to PowerPoint"""
    context.user_data['current_operation'] = 'pdf_to_ppt'
    update.message.reply_text('أرسل ملف PDF لتحويله إلى عرض تقديمي PowerPoint')

def word_to_pdf_command(update: Update, context: CallbackContext):
    """Handler for converting Word to PDF"""
    context.user_data['current_operation'] = 'word_to_pdf'
    update.message.reply_text('أرسل ملف Word لتحويله إلى PDF')

def excel_to_pdf_command(update: Update, context: CallbackContext):
    """Handler for converting Excel to PDF"""
    context.user_data['current_operation'] = 'excel_to_pdf'
    update.message.reply_text('أرسل ملف Excel لتحويله إلى PDF')

def ppt_to_pdf_command(update: Update, context: CallbackContext):
    """Handler for converting PowerPoint to PDF"""
    context.user_data['current_operation'] = 'ppt_to_pdf'
    update.message.reply_text('أرسل عرض تقديمي PowerPoint لتحويله إلى PDF')

# Content extraction
def extract_images_command(update: Update, context: CallbackContext):
    """Handler for extracting images from PDF"""
    context.user_data['current_operation'] = 'extract_images'
    update.message.reply_text('أرسل ملف PDF لاستخراج الصور منه')

def extract_text_command(update: Update, context: CallbackContext):
    """Handler for extracting text from PDF"""
    context.user_data['current_operation'] = 'extract_text'
    update.message.reply_text('أرسل ملف PDF لاستخراج النص منه')

# File editing
def add_text_command(update: Update, context: CallbackContext):
    """Handler for adding text to PDF"""
    context.user_data['current_operation'] = 'add_text'
    update.message.reply_text('أرسل ملف PDF لإضافة نص إليه')

def add_image_command(update: Update, context: CallbackContext):
    """Handler for adding image to PDF"""
    context.user_data['current_operation'] = 'add_image'
    update.message.reply_text('أرسل ملف PDF لإضافة صورة إليه')

def add_note_command(update: Update, context: CallbackContext):
    """Handler for adding note to PDF"""
    context.user_data['current_operation'] = 'add_note'
    update.message.reply_text('أرسل ملف PDF لإضافة ملاحظة إليه')

def add_link_command(update: Update, context: CallbackContext):
    """Handler for adding link to PDF"""
    context.user_data['current_operation'] = 'add_link'
    update.message.reply_text('أرسل ملف PDF لإضافة رابط إليه')

def add_numbers_command(update: Update, context: CallbackContext):
    """Handler for adding page numbers to PDF"""
    context.user_data['current_operation'] = 'add_numbers'
    update.message.reply_text('أرسل ملف PDF لإضافة أرقام الصفحات إليه')

def watermark_command(update: Update, context: CallbackContext):
    """Handler for adding watermark to PDF"""
    context.user_data['current_operation'] = 'watermark'
    update.message.reply_text('أرسل ملف PDF لإضافة علامة مائية إليه')

def background_command(update: Update, context: CallbackContext):
    """Handler for changing PDF background"""
    context.user_data['current_operation'] = 'background'
    update.message.reply_text('أرسل ملف PDF لتغيير خلفيته')

# Page formatting
def resize_pages_command(update: Update, context: CallbackContext):
    """Handler for resizing PDF pages"""
    context.user_data['current_operation'] = 'resize_pages'
    update.message.reply_text('أرسل ملف PDF لتغيير حجم صفحاته')

def page_orientation_command(update: Update, context: CallbackContext):
    """Handler for changing page orientation in PDF"""
    context.user_data['current_operation'] = 'page_orientation'
    update.message.reply_text('أرسل ملف PDF لتغيير اتجاه صفحاته')

def crop_command(update: Update, context: CallbackContext):
    """Handler for cropping PDF pages"""
    context.user_data['current_operation'] = 'crop'
    update.message.reply_text('أرسل ملف PDF لقص صفحاته')

def split_pages_command(update: Update, context: CallbackContext):
    """Handler for splitting PDF into individual pages"""
    context.user_data['current_operation'] = 'split_pages'
    update.message.reply_text('أرسل ملف PDF لتقسيمه إلى صفحات منفصلة')

def sort_pages_command(update: Update, context: CallbackContext):
    """Handler for sorting PDF pages"""
    context.user_data['current_operation'] = 'sort_pages'
    update.message.reply_text('أرسل ملف PDF لترتيب صفحاته')

def add_toc_command(update: Update, context: CallbackContext):
    """Handler for adding table of contents to PDF"""
    context.user_data['current_operation'] = 'add_toc'
    update.message.reply_text('أرسل ملف PDF لإضافة فهرس محتويات إليه')

# File information and settings
def edit_metadata_command(update: Update, context: CallbackContext):
    """Handler for editing PDF metadata"""
    context.user_data['current_operation'] = 'edit_metadata'
    update.message.reply_text('أرسل ملف PDF لتعديل البيانات الوصفية له')

def file_info_command(update: Update, context: CallbackContext):
    """Handler for showing file information"""
    context.user_data['current_operation'] = 'file_info'
    update.message.reply_text('أرسل ملف للحصول على معلوماته')

def rename_command(update: Update, context: CallbackContext):
    """Handler for renaming files"""
    context.user_data['current_operation'] = 'rename'
    update.message.reply_text('أرسل الملف الذي تريد إعادة تسميته')

def auto_delete_command(update: Update, context: CallbackContext):
    """Handler for setting auto-delete settings"""
    context.user_data['current_operation'] = 'auto_delete'
    update.message.reply_text('تفعيل/تعطيل حذف الملفات تلقائياً. أدخل "تفعيل" أو "تعطيل"')