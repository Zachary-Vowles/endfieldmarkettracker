"""
Analysis module for price data and trading recommendations
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

@dataclass
class TradeOpportunity:
    """A ranked trading opportunity"""
    product_name: str
    region: str
    local_price: int
    friend_price: int
    absolute_profit: int
    profit_per_unit: int
    quantity_owned: int
    potential_total_profit: int
    rank: int
    recommendation: str

@dataclass
class PricePattern:
    """Detected price pattern for a product"""
    product_name: str
    avg_price: float
    volatility: float  # Standard deviation
    trend: str  # 'rising', 'falling', 'stable'
    spike_frequency: float  # How often spikes occur
    best_time_to_buy: Optional[str] = None
    best_time_to_sell: Optional[str] = None

class PriceAnalyzer:
    """Analyzes price data and generates recommendations"""
    
    def __init__(self):
        """Initialize the analyzer"""
        self.spike_threshold = 1.5  # 150% of average is a spike
    
    def rank_opportunities(self, readings: List) -> List[TradeOpportunity]:
        """Rank trading opportunities by profit potential"""
        opportunities = []
        
        for reading in readings:
            if not reading.friend_price or not reading.local_price:
                continue
            
            profit = reading.friend_price - reading.local_price
            
            # Calculate potential total profit
            potential_total = profit * reading.quantity_owned if reading.quantity_owned > 0 else profit
            
            opp = TradeOpportunity(
                product_name=reading.product.name,
                region=reading.region,
                local_price=reading.local_price,
                friend_price=reading.friend_price,
                absolute_profit=profit,
                profit_per_unit=profit,
                quantity_owned=reading.quantity_owned,
                potential_total_profit=potential_total,
                rank=0,  # Will be set after sorting
                recommendation=self._generate_recommendation(profit, reading.quantity_owned)
            )
            
            opportunities.append(opp)
        
        # Sort by absolute profit (highest first)
        opportunities.sort(key=lambda x: x.absolute_profit, reverse=True)
        
        # Assign ranks
        for i, opp in enumerate(opportunities):
            opp.rank = i + 1
        
        return opportunities
    
    def _generate_recommendation(self, profit: int, quantity_owned: int) -> str:
        """Generate a trading recommendation"""
        if profit <= 0:
            return "Avoid - No profit opportunity"
        
        if profit > 2000:
            if quantity_owned > 0:
                return "SELL NOW - Excellent opportunity!"
            else:
                return "BUY - Exceptional profit potential"
        elif profit > 1000:
            if quantity_owned > 0:
                return "Sell - Good opportunity"
            else:
                return "Buy - Good profit potential"
        elif profit > 500:
            return "Consider - Moderate opportunity"
        else:
            return "Low priority - Small margin"
    
    def analyze_price_history(self, readings: List) -> PricePattern:
        """Analyze price history to detect patterns"""
        if not readings:
            return None
        
        product_name = readings[0].product.name
        
        # Extract prices
        local_prices = [r.local_price for r in readings if r.local_price]
        friend_prices = [r.friend_price for r in readings if r.friend_price]
        
        if not local_prices:
            return None
        
        # Calculate statistics
        avg_price = statistics.mean(local_prices)
        volatility = statistics.stdev(local_prices) if len(local_prices) > 1 else 0
        
        # Determine trend
        if len(local_prices) >= 3:
            recent = statistics.mean(local_prices[-3:])
            older = statistics.mean(local_prices[:3])
            
            if recent > older * 1.1:
                trend = 'rising'
            elif recent < older * 0.9:
                trend = 'falling'
            else:
                trend = 'stable'
        else:
            trend = 'insufficient_data'
        
        # Calculate spike frequency
        spikes = sum(1 for p in local_prices if p > avg_price * self.spike_threshold)
        spike_freq = spikes / len(local_prices) if local_prices else 0
        
        return PricePattern(
            product_name=product_name,
            avg_price=avg_price,
            volatility=volatility,
            trend=trend,
            spike_frequency=spike_freq
        )
    
    def should_hold_or_sell(self, current_reading, history: List) -> Dict:
        """Determine if user should hold or sell based on historical patterns"""
        if not history or not current_reading.friend_price:
            return {"decision": "unknown", "reason": "Insufficient data"}
        
        current_profit = current_reading.friend_price - current_reading.local_price
        
        # Get historical differences
        historical_diffs = []
        for r in history:
            if r.friend_price and r.local_price:
                historical_diffs.append(r.friend_price - r.local_price)
        
        if not historical_diffs:
            return {"decision": "unknown", "reason": "No historical price data"}
        
        avg_diff = statistics.mean(historical_diffs)
        max_diff = max(historical_diffs)
        
        # Decision logic
        if current_profit >= max_diff * 0.9:
            return {
                "decision": "sell",
                "reason": f"Near all-time high (+{current_profit:,}). Rare opportunity!",
                "confidence": "high"
            }
        elif current_profit > avg_diff * 2:
            return {
                "decision": "sell",
                "reason": f"Well above average (+{current_profit:,} vs avg +{avg_diff:.0f})",
                "confidence": "medium"
            }
        elif current_profit < avg_diff * 0.5:
            return {
                "decision": "hold",
                "reason": f"Below average (+{current_profit:,} vs avg +{avg_diff:.0f}). Wait for better price.",
                "confidence": "medium"
            }
        else:
            return {
                "decision": "neutral",
                "reason": f"Average opportunity (+{current_profit:,} close to avg +{avg_diff:.0f})",
                "confidence": "low"
            }
    
    def get_summary_stats(self, opportunities: List[TradeOpportunity]) -> Dict:
        """Get summary statistics for today's opportunities"""
        if not opportunities:
            return {
                "total_opportunities": 0,
                "best_profit": 0,
                "average_profit": 0,
                "total_potential_profit": 0
            }
        
        profits = [o.absolute_profit for o in opportunities]
        total_potential = sum(o.potential_total_profit for o in opportunities)
        
        return {
            "total_opportunities": len(opportunities),
            "best_profit": max(profits),
            "average_profit": statistics.mean(profits),
            "total_potential_profit": total_potential,
            "excellent_opportunities": sum(1 for p in profits if p > 2000),
            "good_opportunities": sum(1 for p in profits if 1000 < p <= 2000)
        }