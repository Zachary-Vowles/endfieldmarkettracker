"""
Database models for Endfield Market Tracker
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, scoped_session
import os
from appdirs import user_data_dir

Base = declarative_base()

# Global scoped session factory - thread-safe
SessionFactory = None

class Product(Base):
    """Represents a tradeable good in the game"""
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    region = Column(String, nullable=False)  # 'wuling' or 'valley'
    icon_path = Column(String, nullable=True)
    first_seen = Column(DateTime, default=datetime.utcnow)
    highest_difference_ever = Column(Integer, default=0)
    highest_difference_date = Column(DateTime, nullable=True)
    
    # Relationship to price readings
    readings = relationship("PriceReading", back_populates="product", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Product(name='{self.name}', region='{self.region}')>"

class PriceReading(Base):
    """A single price capture event"""
    __tablename__ = 'price_readings'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    session_id = Column(Integer, ForeignKey('capture_sessions.id'), nullable=True)
    
    # Product info
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    product = relationship("Product", back_populates="readings")
    
    # Region
    region = Column(String, nullable=False)
    
    # Prices
    local_price = Column(Integer, nullable=False)  # Current market price
    average_cost = Column(Integer, nullable=True)   # User's average cost if owned
    friend_price = Column(Integer, nullable=True)   # Highest friend price
    quantity_owned = Column(Integer, default=0)
    
    # Calculated differences
    vs_local_percent = Column(Float, nullable=True)
    vs_owned_percent = Column(Float, nullable=True)
    absolute_difference = Column(Integer, nullable=True)  # Friend - Local
    
    # Debug
    screenshot_path = Column(String, nullable=True)
    ocr_confidence = Column(Float, nullable=True)
    
    def __repr__(self):
        return f"<PriceReading(product='{self.product.name}', local={self.local_price}, friend={self.friend_price})>"
    
    @property
    def profit_potential(self) -> Optional[int]:
        """Calculate absolute profit potential"""
        if self.friend_price and self.local_price:
            return self.friend_price - self.local_price
        return None

class CaptureSession(Base):
    """Tracks a single capture session"""
    __tablename__ = 'capture_sessions'
    
    id = Column(Integer, primary_key=True)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    region = Column(String, nullable=True)
    goods_captured = Column(Integer, default=0)
    status = Column(String, default='active')  # 'active', 'completed', 'error'
    error_message = Column(String, nullable=True)
    
    readings = relationship("PriceReading", backref="session")
    
    def __repr__(self):
        return f"<CaptureSession(id={self.id}, status='{self.status}', goods={self.goods_captured})>"
    
    @property
    def duration_seconds(self) -> Optional[float]:
        """Calculate session duration"""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None

# Database initialization
def get_db_path():
    """Get the database file path"""
    app_dir = user_data_dir("EndfieldMarketTracker", "EndfieldMarketTracker")
    os.makedirs(app_dir, exist_ok=True)
    return os.path.join(app_dir, "prices.db")

def init_database():
    """Initialize the database and create tables"""
    global SessionFactory
    db_path = get_db_path()
    engine = create_engine(f'sqlite:///{db_path}')
    Base.metadata.create_all(engine)
    
    # Initialize thread-safe scoped session
    SessionFactory = scoped_session(sessionmaker(bind=engine))
    
    return engine

def get_session():
    """Get a thread-safe database session"""
    if SessionFactory is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    return SessionFactory()