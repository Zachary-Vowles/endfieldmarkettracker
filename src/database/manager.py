"""
Database operations manager
"""

from typing import List, Optional, Dict
from datetime import datetime, timedelta
from sqlalchemy import func, desc
from src.database.models import (
    init_database, get_session, Product, PriceReading, CaptureSession
)

class DatabaseManager:
    """Manages all database operations"""
    
    def __init__(self):
        self.engine = init_database()
        self.session = get_session(self.engine)
    
    def close(self):
        """Close database connection"""
        self.session.close()
    
    # Product operations
    def get_or_create_product(self, name: str, region: str, icon_path: str = None) -> Product:
        """Get existing product or create new one"""
        product = self.session.query(Product).filter_by(name=name).first()
        if not product:
            product = Product(name=name, region=region, icon_path=icon_path)
            self.session.add(product)
            self.session.commit()
        return product
    
    def get_all_products(self) -> List[Product]:
        """Get all tracked products"""
        return self.session.query(Product).all()
    
    def update_product_high_difference(self, product_id: int, difference: int):
        """Update the highest difference seen for a product"""
        product = self.session.query(Product).get(product_id)
        if product and difference > product.highest_difference_ever:
            product.highest_difference_ever = difference
            product.highest_difference_date = datetime.utcnow()
            self.session.commit()
    
    # Capture session operations
    def start_session(self, region: str = None) -> CaptureSession:
        """Start a new capture session"""
        session = CaptureSession(region=region, status='active')
        self.session.add(session)
        self.session.commit()
        return session
    
    def end_session(self, session_id: int, status: str = 'completed', error_msg: str = None):
        """End a capture session"""
        session = self.session.query(CaptureSession).get(session_id)
        if session:
            session.end_time = datetime.utcnow()
            session.status = status
            if error_msg:
                session.error_message = error_msg
            self.session.commit()
    
    def increment_session_goods(self, session_id: int):
        """Increment the goods captured counter"""
        session = self.session.query(CaptureSession).get(session_id)
        if session:
            session.goods_captured += 1
            self.session.commit()
    
    # Price reading operations
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
        """Save a new price reading"""
        
        # Get or create product
        product = self.get_or_create_product(product_name, region)
        
        # Calculate absolute difference
        absolute_diff = None
        if friend_price and local_price:
            absolute_diff = friend_price - local_price
            
            # Update product's highest difference if this is a new record
            if absolute_diff > product.highest_difference_ever:
                self.update_product_high_difference(product.id, absolute_diff)
        
        # Create reading
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
        
        self.session.add(reading)
        self.session.commit()
        
        # Increment session counter if applicable
        if session_id:
            self.increment_session_goods(session_id)
        
        return reading
    
    def get_latest_readings(self, limit: int = 50) -> List[PriceReading]:
        """Get the most recent price readings"""
        return self.session.query(PriceReading)\\
            .order_by(desc(PriceReading.timestamp))\\
            .limit(limit)\\
            .all()
    
    def get_todays_readings(self) -> List[PriceReading]:
        """Get all readings from today"""
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        return self.session.query(PriceReading)\\
            .filter(PriceReading.timestamp >= today)\\
            .order_by(desc(PriceReading.timestamp))\\
            .all()
    
    def get_best_opportunities_today(self) -> List[Dict]:
        """Get today's best trading opportunities ranked by profit"""
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Get latest reading for each product today
        subquery = self.session.query(
            PriceReading.product_id,
            func.max(PriceReading.timestamp).label('max_time')
        ).filter(PriceReading.timestamp >= today)\\
         .group_by(PriceReading.product_id)\\
         .subquery()
        
        readings = self.session.query(PriceReading)\\
            .join(subquery, 
                  (PriceReading.product_id == subquery.c.product_id) & 
                  (PriceReading.timestamp == subquery.c.max_time))\\
            .order_by(desc(PriceReading.absolute_difference))\\
            .all()
        
        return readings
    
    def get_product_history(self, product_name: str, days: int = 30) -> List[PriceReading]:
        """Get price history for a specific product"""
        since = datetime.utcnow() - timedelta(days=days)
        
        return self.session.query(PriceReading)\\
            .join(Product)\\
            .filter(Product.name == product_name)\\
            .filter(PriceReading.timestamp >= since)\\
            .order_by(PriceReading.timestamp)\\
            .all()
    
    def get_price_stats(self, product_name: str) -> Dict:
        """Get statistics for a product"""
        readings = self.session.query(PriceReading)\\
            .join(Product)\\
            .filter(Product.name == product_name)\\
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
    
    def get_all_time_highs(self) -> List[Dict]:
        """Get all-time high differences for all products"""
        products = self.session.query(Product)\\
            .filter(Product.highest_difference_ever > 0)\\
            .order_by(desc(Product.highest_difference_ever))\\
            .all()
        
        return [{
            'name': p.name,
            'region': p.region,
            'highest_difference': p.highest_difference_ever,
            'date': p.highest_difference_date
        } for p in products]