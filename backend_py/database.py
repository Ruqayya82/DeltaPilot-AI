from sqlalchemy import create_engine, Column, String, Boolean, DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import uuid
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./deltapilot.db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class Signal(Base):
    __tablename__ = "signals"
    id = Column(String, primary_key=True, default=str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"))
    symbol = Column(String(20), nullable=False)
    signal = Column(String(10), nullable=False)
    price = Column(Float)
    confidence = Column(Float, default=0.5)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class Trade(Base):
    __tablename__ = "trades"
    id = Column(String, primary_key=True, default=str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"))
    symbol = Column(String(20), nullable=False)
    side = Column(String(10), nullable=False)
    entry_price = Column(Float, nullable=False)
    stop_loss = Column(Float)
    take_profit = Column(Float)
    size = Column(Float)
    status = Column(String(20), default="OPEN")
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    closed_at = Column(DateTime(timezone=True))

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

