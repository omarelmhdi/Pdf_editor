from models import Session, User
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from config import ADMIN_ID

def get_or_create_user(user):
    """
    الحصول على مستخدم من قاعدة البيانات أو إنشاء مستخدم جديد إذا لم يكن موجوداً
    """
    session = Session()
    try:
        # البحث عن المستخدم باستخدام معرف المستخدم
        db_user = session.query(User).filter(User.user_id == user.id).first()
        
        if db_user:
            # تحديث وقت آخر نشاط
            db_user.last_activity = datetime.utcnow()
            if user.username:
                db_user.username = user.username
            if user.first_name:
                db_user.first_name = user.first_name
            if user.last_name:
                db_user.last_name = user.last_name
            if user.language_code:
                db_user.language_code = user.language_code
            
            session.commit()
            return False  # ليس مستخدمًا جديدًا
        else:
            # إنشاء مستخدم جديد
            new_user = User(
                user_id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                language_code=user.language_code,
                is_bot=user.is_bot,
                join_date=datetime.utcnow(),
                last_activity=datetime.utcnow()
            )
            session.add(new_user)
            session.commit()
            return True  # مستخدم جديد
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Database error: {e}")
        return False
    finally:
        session.close()

def get_total_users_count():
    """
    الحصول على إجمالي عدد المستخدمين
    """
    session = Session()
    try:
        count = session.query(User).count()
        return count
    except SQLAlchemyError as e:
        print(f"Database error: {e}")
        return 0
    finally:
        session.close()
        
def get_all_users():
    """
    الحصول على جميع المستخدمين
    """
    session = Session()
    try:
        users = session.query(User).all()
        return users
    except SQLAlchemyError as e:
        print(f"Database error: {e}")
        return []
    finally:
        session.close()

def notify_admin_new_user(bot, user):
    """
    إشعار المدير بمستخدم جديد
    """
    try:
        user_info = f"""
مستخدم جديد قام بتشغيل البوت! 🎉

معلومات المستخدم:
🆔 المعرف: {user.id}
👤 اسم المستخدم: {user.username or 'غير متوفر'}
📝 الاسم: {user.first_name or ''} {user.last_name or ''}
🌐 رمز اللغة: {user.language_code or 'غير متوفر'}

إجمالي عدد المستخدمين: {get_total_users_count()} 👥
"""
        bot.send_message(chat_id=ADMIN_ID, text=user_info)
    except Exception as e:
        print(f"Error notifying admin: {e}")