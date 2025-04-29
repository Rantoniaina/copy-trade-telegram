from typing import Dict, Any, Optional, Set, List, Tuple
from src.models.mapping import Mapping
from src.models.configuration import Configuration


class TradeService:
    def __init__(self, configuration: Configuration):
        self.configuration = configuration
        # Pre-compute lowercase conditions for faster matching
        self.buy_conditions_lower = {condition.lower() for condition in configuration.buy_conditions}
        self.sell_conditions_lower = {condition.lower() for condition in configuration.sell_conditions}
        
        # Pre-compute lowercase mappings for faster lookups
        self.pair_mapping_table: List[Tuple[str, str]] = []
        for mapping in configuration.pair_mappings:
            for from_text in mapping.from_message:
                self.pair_mapping_table.append((from_text.lower(), mapping.mapping))
        
        # Pre-compute SL and TP mappings if available
        self.sl_mapping_table: List[Tuple[str, str, str]] = []
        if configuration.sl_mappings:
            for mapping in configuration.sl_mappings:
                for from_text in mapping.from_message:
                    self.sl_mapping_table.append((from_text.lower(), mapping.mapping, mapping.sl_position))
        
        self.tp_mapping_table: List[Tuple[str, str, str]] = []
        if configuration.tp_mappings:
            for mapping in configuration.tp_mappings:
                for from_text in mapping.from_message:
                    self.tp_mapping_table.append((from_text.lower(), mapping.mapping, mapping.tp_position))
    
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
        mapped_symbol = self._apply_pair_mappings(message_text)
        
        # Extract stop loss and take profit if configured
        stop_loss = None
        take_profit = None
        
        if self.configuration.position_sl.name == "SIGNAL_SL":
            stop_loss = self._extract_stop_loss(message_text)
        
        if self.configuration.position_tp.name == "SIGNAL_TP":
            take_profit = self._extract_take_profit(message_text)
        
        signal = {
            'action': action,
            'symbol': mapped_symbol,
            'raw_message': message_text,
            'timestamp': message_data.get('time'),
            'source': f"{message_data.get('channel')} - {message_data.get('sender')}"
        }
        
        # Add stop loss and take profit if found
        if stop_loss:
            signal['stop_loss'] = stop_loss
        
        if take_profit:
            if isinstance(take_profit, list):
                signal['take_profit_levels'] = take_profit
            else:
                signal['take_profit'] = take_profit
        
        return signal
    
    def _apply_pair_mappings(self, message_text: str) -> str:
        """Apply pair mappings to extract or transform symbols"""
        message_lower = message_text.lower()
        
        # Use pre-computed lowercase mappings
        for from_text_lower, mapping in self.pair_mapping_table:
            if from_text_lower in message_lower:
                return mapping
        
        # Return original text if no mapping found
        return message_text
    
    def _extract_stop_loss(self, message_text: str) -> Optional[str]:
        """Extract stop loss value from message based on mappings"""
        message_lower = message_text.lower()
        
        for keyword, mapping, position in self.sl_mapping_table:
            if keyword in message_lower:
                # TODO: Implement logic to extract stop loss value
                # This would require parsing the message to find the actual value
                # based on the keyword position (before or after)
                return None  # Placeholder for actual implementation
        
        return None
    
    def _extract_take_profit(self, message_text: str) -> Optional[str]:
        """Extract take profit value(s) from message based on mappings"""
        message_lower = message_text.lower()
        
        for keyword, mapping, position in self.tp_mapping_table:
            if keyword in message_lower:
                # TODO: Implement logic to extract take profit value(s)
                # This would require parsing the message to find the actual value(s)
                # based on the keyword position (before or after)
                return None  # Placeholder for actual implementation
        
        return None 