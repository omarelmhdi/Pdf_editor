import os
from sqlalchemy import Column, Integer, BigInteger, String, Boolean, DateTime, create_engine, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DATABASE_URL = os.environ.get('DATABASE_URL')

engine = create_engine(DATABASE_URL)
Base = declarative_base()
Session = sessionmaker(bind=engine)

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, unique=True, nullable=False)  # تغيير إلى BigInteger للتعامل مع معرفات Telegram الكبيرة
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    language_code = Column(String, nullable=True)
    is_bot = Column(Boolean, default=False)
    join_date = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<User(id={self.user_id}, username={self.username})>"

# فحص إذا كان الجدول موجود قبل محاولة إنشائه
inspector = inspect(engine)
if not inspector.has_table('users'):
    # إنشاء الجداول في قاعدة البيانات
    Base.metadata.create_all(engine)