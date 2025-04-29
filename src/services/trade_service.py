from typing import Dict, Any, Optional, Set, List, Tuple
from src.models.setup import Setup
from src.models.mapping import Mapping
from src.models.configuration import Configuration


class TradeService:
    def __init__(self, setup: Setup, configuration: Configuration):
        self.setup = setup
        self.configuration = configuration
        # Pre-compute lowercase conditions for faster matching
        self.buy_conditions_lower = {condition.lower() for condition in setup.buy_conditions}
        self.sell_conditions_lower = {condition.lower() for condition in setup.sell_conditions}
        
        # Pre-compute lowercase mappings for faster lookups
        self.mapping_table: List[Tuple[str, str]] = []
        for mapping in configuration.mappings:
            for from_text in mapping.from_message:
                self.mapping_table.append((from_text.lower(), mapping.mapping))
    
    def process_message(self, message_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process a message and determine if it matches any trading conditions"""
        message_text = message_data.get('text', '')
        if not message_text:
            return None
        
        # Convert message text to lowercase for case-insensitive matching
        message_lower = message_text.lower()
        
        # Check for buy conditions with efficient set lookups
        if any(cond in message_lower for cond in self.buy_conditions_lower):
            return self._create_trade_signal(message_data, 'BUY')
        
        # Check for sell conditions with efficient set lookups
        if any(cond in message_lower for cond in self.sell_conditions_lower):
            return self._create_trade_signal(message_data, 'SELL')
        
        return None
    
    def _create_trade_signal(self, message_data: Dict[str, Any], action: str) -> Dict[str, Any]:
        """Create a trade signal from the message data"""
        message_text = message_data.get('text', '')
        
        # Apply mappings
        mapped_symbol = self._apply_mappings(message_text)
        
        return {
            'action': action,
            'symbol': mapped_symbol,
            'raw_message': message_text,
            'timestamp': message_data.get('time'),
            'source': f"{message_data.get('channel')} - {message_data.get('sender')}"
        }
    
    def _apply_mappings(self, message_text: str) -> str:
        """Apply message mappings to extract or transform symbols"""
        message_lower = message_text.lower()
        
        # Use pre-computed lowercase mappings
        for from_text_lower, mapping in self.mapping_table:
            if from_text_lower in message_lower:
                return mapping
        
        # Return original text if no mapping found
        return message_text 