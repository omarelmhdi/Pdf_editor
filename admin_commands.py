from telegram import Update, ParseMode
from telegram.ext import CallbackContext
from user_tracking import get_total_users_count
from config import ADMIN_ID

def stats_command(update: Update, context: CallbackContext):
    """
    عرض إحصائيات المستخدمين (فقط للمدير)
    """
    user_id = update.effective_user.id
    
    # التحقق من أن المستخدم هو المدير
    if user_id != ADMIN_ID:
        update.message.reply_text('هذا الأمر متاح فقط للمدير.')
        return
    
    # إحصائيات المستخدمين
    total_users = get_total_users_count()
    
    stats_text = f"""
📊 *إحصائيات البوت*

👥 *إجمالي المستخدمين:* {total_users}
    """
    
    update.message.reply_text(
        stats_text,
        parse_mode=ParseMode.MARKDOWN
    )

def broadcast_command(update: Update, context: CallbackContext):
    """
    إرسال رسالة جماعية إلى جميع المستخدمين (فقط للمدير)
    """
    user_id = update.effective_user.id
    
    # التحقق من أن المستخدم هو المدير
    if user_id != ADMIN_ID:
        update.message.reply_text('هذا الأمر متاح فقط للمدير.')
        return
    
    # تحقق من وجود نص للإرسال
    if not context.args:
        update.message.reply_text('الرجاء إدخال نص الرسالة التي تريد إرسالها للمستخدمين.\n'
                                 'مثال: /broadcast مرحباً بالجميع! هناك تحديث جديد للبوت.')
        return
    
    # إعداد نص الرسالة الجماعية
    broadcast_text = ' '.join(context.args)
    
    # إرسال رسالة للمدير بأن العملية بدأت
    update.message.reply_text('تم بدء الإرسال الجماعي. سيتم إعلامك عند الانتهاء.')
    
    # الحصول على جميع المستخدمين
    from user_tracking import get_all_users
    users = get_all_users()
    
    # عداد المستخدمين الذين تم إرسال الرسالة لهم بنجاح وعدد الحالات الفاشلة
    success_count = 0
    failed_count = 0
    
    # إرسال الرسالة لكل مستخدم
    for user in users:
        try:
            context.bot.send_message(chat_id=user.user_id, text=broadcast_text)
            success_count += 1
        except Exception as e:
            print(f"Failed to send message to user {user.user_id}: {e}")
            failed_count += 1
    
    # إرسال تقرير إلى المدير عن حالة الإرسال الجماعي
    report = f"""
📨 تم اكتمال الإرسال الجماعي

✅ نجح: {success_count} مستخدم
❌ فشل: {failed_count} مستخدم
📝 إجمالي: {len(users)} مستخدم

الرسالة:
"{broadcast_text}"
"""
    update.message.reply_text(report)