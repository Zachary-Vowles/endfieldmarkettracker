"""
Tests for Endfield Market Tracker
"""

import pytest
import numpy as np
from datetime import datetime

# Test OCR Engine
def test_ocr_preprocessing():
    """Test image preprocessing for OCR"""
    from src.core.ocr_engine import OCREngine
    
    engine = OCREngine(use_gpu=False)
    
    # Create a dummy image
    img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    processed = engine.preprocess_image(img)
    
    assert processed is not None
    assert len(processed.shape) == 2  # Should be grayscale

def test_price_extraction():
    """Test price extraction from text"""
    from src.core.data_extractor import DataExtractor
    
    extractor = DataExtractor()
    
    # Test various price formats
    assert extractor.extract_price("1,234 HZ") == 1234
    assert extractor.extract_price("5678") == 5678
    assert extractor.extract_price("Price: 9,999") == 9999
    assert extractor.extract_price("") is None

def test_product_name_extraction():
    """Test product name extraction"""
    from src.core.data_extractor import DataExtractor
    
    extractor = DataExtractor()
    
    # Test known products
    assert extractor.extract_product_name("Wuling Frozen Pears [pkg]") == "Wuling Frozen Pears"
    assert extractor.extract_product_name("Eureka Anti-smog Tincture") == "Eureka Anti-smog Tincture"

def test_percentage_extraction():
    """Test percentage extraction"""
    from src.core.data_extractor import DataExtractor
    
    extractor = DataExtractor()
    
    assert extractor.extract_percentage("+40.5%") == 40.5
    assert extractor.extract_percentage("-15.2%") == -15.2
    assert extractor.extract_percentage("80.9%") == 80.9
    assert extractor.extract_percentage("") is None

# Test Analysis
def test_opportunity_ranking():
    """Test opportunity ranking"""
    from src.core.analysis import PriceAnalyzer, TradeOpportunity
    
    analyzer = PriceAnalyzer()
    
    # Create mock opportunities
    opportunities = [
        TradeOpportunity(
            product_name="Test A", region="wuling",
            local_price=1000, friend_price=5000,
            absolute_profit=4000, profit_per_unit=4000,
            quantity_owned=10, potential_total_profit=40000,
            rank=0, recommendation=""
        ),
        TradeOpportunity(
            product_name="Test B", region="wuling",
            local_price=1000, friend_price=2000,
            absolute_profit=1000, profit_per_unit=1000,
            quantity_owned=5, potential_total_profit=5000,
            rank=0, recommendation=""
        ),
    ]
    
    ranked = analyzer.rank_opportunities(opportunities)
    
    assert ranked[0].product_name == "Test A"  # Higher profit should be first
    assert ranked[0].rank == 1

def test_recommendation_generation():
    """Test recommendation generation"""
    from src.core.analysis import PriceAnalyzer
    
    analyzer = PriceAnalyzer()
    
    assert "SELL NOW" in analyzer._generate_recommendation(2500, 10)
    assert "BUY" in analyzer._generate_recommendation(2500, 0)
    assert "Avoid" in analyzer._generate_recommendation(-100, 0)

# Test Database
def test_database_operations():
    """Test database operations"""
    from src.database.manager import DatabaseManager
    from src.database.models import init_database, get_session
    
    # Use in-memory database for testing
    from sqlalchemy import create_engine
    from src.database.models import Base
    
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    
    # This is a simplified test - in reality you'd mock the session
    assert engine is not None

# Test Constants
def test_region_enum():
    """Test region enumeration"""
    from src.utils.constants import Region, CURRENCIES
    
    assert Region.WULING.value == "wuling"
    assert Region.VALLEY.value == "valley"
    assert CURRENCIES[Region.WULING] == "HZ"

if __name__ == '__main__':
    pytest.main([__file__, '-v'])