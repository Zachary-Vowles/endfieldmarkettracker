"""
Database operations manager - Thread-safe version
"""

from typing import List, Optional, Dict
from datetime import datetime, timedelta
from sqlalchemy import func, desc
from sqlalchemy.orm import joinedload
from src.database.models import (
    init_database, get_session, Product, PriceReading, CaptureSession
)

class DatabaseManager:
    """Manages all database operations - Thread-safe"""
    
    def __init__(self):
        self.engine = init_database()
    
    def close(self):
        """Close database connection"""
        pass
    
    def _get_session(self):
        """Get a new session for current thread"""
        return get_session()
    
    def get_all_products(self) -> List[Product]:
        """Get all tracked products"""
        session = self._get_session()
        try:
            return session.query(Product).all()
        finally:
            session.close()
    
    def start_session(self, region: str = None) -> int:
        """Start a new capture session, returns session ID"""
        session = self._get_session()
        try:
            capture_session = CaptureSession(region=region, status='active')
            session.add(capture_session)
            session.commit()
            return capture_session.id
        finally:
            session.close()
    
    def end_session(self, session_id: int, status: str = 'completed', error_msg: str = None):
        """End a capture session"""
        session = self._get_session()
        try:
            capture_session = session.query(CaptureSession).get(session_id)
            if capture_session:
                capture_session.end_time = datetime.utcnow()
                capture_session.status = status
                if error_msg:
                    capture_session.error_message = error_msg
                session.commit()
        finally:
            session.close()
    
    def increment_session_goods(self, session_id: int):
        """Increment the goods captured counter"""
        session = self._get_session()
        try:
            capture_session = session.query(CaptureSession).get(session_id)
            if capture_session:
                capture_session.goods_captured += 1
                session.commit()
        finally:
            session.close()
    
    def save_price_reading(self, 
                          product_name: str,
                          region: str,
                          local_price: int,
                          friend_price: int = None,
                          average_cost: int = None,
                          quantity_owned: int = 0,
                          vs_local_percent: float = None,
                          vs_owned_percent: float = None,
                          session_id: int = None,
                          screenshot_path: str = None,
                          ocr_confidence: float = None) -> PriceReading:
        """Save a new price reading - Single Session Fix"""
        session = self._get_session()
        try:
            # Inline get_or_create to keep it in the same active session
            product = session.query(Product).filter_by(name=product_name).first()
            if not product:
                product = Product(name=product_name, region=region)
                session.add(product)
                session.flush() # Assigns an ID without committing yet
            
            absolute_diff = None
            if friend_price and local_price:
                absolute_diff = friend_price - local_price
                
                if absolute_diff > product.highest_difference_ever:
                    product.highest_difference_ever = absolute_diff
                    product.highest_difference_date = datetime.utcnow()
            
            reading = PriceReading(
                product_id=product.id,
                session_id=session_id,
                region=region,
                local_price=local_price,
                friend_price=friend_price,
                average_cost=average_cost,
                quantity_owned=quantity_owned,
                vs_local_percent=vs_local_percent,
                vs_owned_percent=vs_owned_percent,
                absolute_difference=absolute_diff,
                screenshot_path=screenshot_path,
                ocr_confidence=ocr_confidence
            )
            
            session.add(reading)
            session.commit()
            
            if session_id:
                # Manual increment to avoid opening a secondary session
                capture_session = session.query(CaptureSession).get(session_id)
                if capture_session:
                    capture_session.goods_captured += 1
                    session.commit()
            
            return reading
        finally:
            session.close()
    
    def get_latest_readings(self, limit: int = 50) -> List[PriceReading]:
        session = self._get_session()
        try:
            return session.query(PriceReading)\
                .options(joinedload(PriceReading.product))\
                .order_by(desc(PriceReading.timestamp))\
                .limit(limit)\
                .all()
        finally:
            session.close()
    
    def get_todays_readings(self) -> List[PriceReading]:
        session = self._get_session()
        try:
            today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            return session.query(PriceReading)\
                .options(joinedload(PriceReading.product))\
                .filter(PriceReading.timestamp >= today)\
                .order_by(desc(PriceReading.timestamp))\
                .all()
        finally:
            session.close()
    
    def get_best_opportunities_today(self) -> List[PriceReading]:
        session = self._get_session()
        try:
            today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            
            subquery = session.query(
                PriceReading.product_id,
                func.max(PriceReading.timestamp).label('max_time')
            ).filter(PriceReading.timestamp >= today)\
             .group_by(PriceReading.product_id)\
             .subquery()
            
            readings = session.query(PriceReading)\
                .options(joinedload(PriceReading.product))\
                .join(subquery, 
                      (PriceReading.product_id == subquery.c.product_id) & 
                      (PriceReading.timestamp == subquery.c.max_time))\
                .order_by(desc(PriceReading.absolute_difference))\
                .all()
            
            return readings
        finally:
            session.close()
    
    def get_product_history(self, product_name: str, days: int = 30) -> List[PriceReading]:
        session = self._get_session()
        try:
            since = datetime.utcnow() - timedelta(days=days)
            return session.query(PriceReading)\
                .options(joinedload(PriceReading.product))\
                .join(Product)\
                .filter(Product.name == product_name)\
                .filter(PriceReading.timestamp >= since)\
                .order_by(PriceReading.timestamp)\
                .all()
        finally:
            session.close()
    
    def get_price_stats(self, product_name: str) -> Dict:
        session = self._get_session()
        try:
            readings = session.query(PriceReading)\
                .join(Product)\
                .filter(Product.name == product_name)\
                .all()
            
            if not readings:
                return {}
            
            local_prices = [r.local_price for r in readings if r.local_price]
            friend_prices = [r.friend_price for r in readings if r.friend_price]
            differences = [r.absolute_difference for r in readings if r.absolute_difference]
            
            return {
                'total_readings': len(readings),
                'avg_local_price': sum(local_prices) / len(local_prices) if local_prices else 0,
                'avg_friend_price': sum(friend_prices) / len(friend_prices) if friend_prices else 0,
                'max_difference': max(differences) if differences else 0,
                'min_difference': min(differences) if differences else 0,
                'avg_difference': sum(differences) / len(differences) if differences else 0,
            }
        finally:
            session.close()