"""
Data extractor - processes OCR results into structured data
"""

import re
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from src.utils.constants import KNOWN_PRODUCTS, Region

@dataclass
class ProductData:
    """Structured product data from game"""
    name: str
    region: str
    local_price: int
    friend_price: Optional[int] = None
    average_cost: Optional[int] = None
    quantity_owned: int = 0
    vs_local_percent: Optional[float] = None
    vs_owned_percent: Optional[float] = None
    reading_id: Optional[int] = None

class DataExtractor:
    """Extracts structured data from OCR text"""
    
    def __init__(self):
        """Initialize the extractor"""
        self.product_patterns = self._compile_product_patterns()
    
    def _compile_product_patterns(self) -> Dict:
        """Compile regex patterns for known products"""
        patterns = {}
        for product in KNOWN_PRODUCTS:
            # Create fuzzy matching pattern
            escaped = re.escape(product.lower())
            patterns[product] = re.compile(escaped, re.IGNORECASE)
        return patterns
    
    def extract_product_name(self, text: str) -> Optional[str]:
        """Extract product name from OCR text"""
        text_lower = text.lower()
        
        # Check against known products
        for product, pattern in self.product_patterns.items():
            if pattern.search(text_lower):
                return product
        
        # If no match, return the text cleaned up
        cleaned = text.strip().replace("[pkg]", "").strip()
        return cleaned if cleaned else None
    
    def extract_price(self, text: str) -> Optional[int]:
        """Extract price value from text"""
        if not text:
            return None
        
        # Remove currency symbols and non-digit characters
        cleaned = re.sub(r'[^\\d]', '', text)
        
        try:
            return int(cleaned) if cleaned else None
        except ValueError:
            return None
    
    def extract_percentage(self, text: str) -> Optional[float]:
        """Extract percentage value from text"""
        if not text:
            return None
        
        # Match patterns like +40.5%, -15.2%, 80.9%
        match = re.search(r'([+-]?\\d+\\.?\\d*)%', text)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                return None
        return None
    
    def extract_quantity(self, text: str) -> int:
        """Extract quantity owned from text"""
        if not text:
            return 0
        
        # Look for "Owned: X" or just a number
        match = re.search(r'Owned[:\\s]*(\\d+)', text, re.IGNORECASE)
        if match:
            return int(match.group(1))
        
        # Try to find any number
        numbers = re.findall(r'\\d+', text)
        if numbers:
            return int(numbers[0])
        
        return 0
    
    def determine_region(self, text: str) -> str:
        """Determine region from text (Wuling or Valley)"""
        text_lower = text.lower()
        
        if 'wuling' in text_lower or 'hz' in text_lower:
            return Region.WULING.value
        elif 'valley' in text_lower:
            return Region.VALLEY.value
        
        # Default to Wuling if can't determine
        return Region.WULING.value
    
    def process_ocr_results(self, ocr_results: Dict) -> Optional[ProductData]:
        """Process raw OCR results into structured product data"""
        try:
            # Extract product name
            name = self.extract_product_name(
                ocr_results.get('product_name', '')
            )
            
            if not name:
                return None
            
            # Determine region
            region = self.determine_region(
                ocr_results.get('product_name', '')
            )
            
            # Extract prices
            local_price = self.extract_price(
                ocr_results.get('local_price', '')
            )
            
            friend_price = self.extract_price(
                ocr_results.get('friend_price', '')
            )
            
            average_cost = self.extract_price(
                ocr_results.get('average_cost', '')
            )
            
            # Extract quantity
            quantity = self.extract_quantity(
                ocr_results.get('quantity_owned', '')
            )
            
            # Extract percentages
            vs_local = self.extract_percentage(
                ocr_results.get('vs_local', '')
            )
            
            vs_owned = self.extract_percentage(
                ocr_results.get('vs_owned', '')
            )
            
            # Validate minimum required data
            if not local_price:
                return None
            
            return ProductData(
                name=name,
                region=region,
                local_price=local_price,
                friend_price=friend_price,
                average_cost=average_cost,
                quantity_owned=quantity,
                vs_local_percent=vs_local,
                vs_owned_percent=vs_owned
            )
            
        except Exception as e:
            print(f"Error processing OCR results: {e}")
            return None
    
    def calculate_profit_potential(self, data: ProductData) -> Optional[int]:
        """Calculate absolute profit potential"""
        if data.friend_price and data.local_price:
            return data.friend_price - data.local_price
        return None
    
    def is_valid_reading(self, data: ProductData) -> bool:
        """Validate that the reading makes sense"""
        # Basic sanity checks
        if not data.name or len(data.name) < 3:
            return False
        
        if data.local_price and (data.local_price < 0 or data.local_price > 1000000):
            return False
        
        if data.friend_price and (data.friend_price < 0 or data.friend_price > 1000000):
            return False
        
        return True