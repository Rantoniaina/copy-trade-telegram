from typing import Dict, Any, Optional, Set, List, Tuple, Union
from src.models.mapping import Mapping
from src.models.configuration import Configuration
from src.models.setup import Setup
from decimal import Decimal
import re


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
    
    def create_setup_from_message(self, message_text: str) -> Optional[Setup]:
        """
        Create a Setup object from message text based on configuration.
        Returns None if no valid setup could be created.
        """
        if not message_text:
            return None
            
        # Extract instrument from message
        instrument = self._apply_pair_mappings(message_text)
        if not instrument:
            return None
            
        # Extract stop loss if configured
        sl = None
        if self.configuration.position_sl.name == "SIGNAL_SL":
            sl_value = self._extract_stop_loss(message_text)
            if sl_value:
                try:
                    sl = Decimal(str(sl_value))
                except (ValueError, TypeError):
                    pass
                    
        # Extract take profit levels if configured
        tps = []
        if self.configuration.position_tp.name == "SIGNAL_TP":
            tp_values = self._extract_take_profit(message_text)
            if tp_values:
                if isinstance(tp_values, list):
                    # Convert list of values to Decimals
                    tps = [Decimal(str(tp)) for tp in tp_values if self._is_valid_decimal(tp)]
                else:
                    # Single TP value
                    try:
                        tps = [Decimal(str(tp_values))]
                    except (ValueError, TypeError):
                        pass
        
        # Create and return the Setup object
        setup = Setup(
            instrument=instrument,
            sl=sl,
            tps=tps if tps else None
        )
        
        # Print the extracted setup
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("🔍 EXTRACTED SETUP FROM MESSAGE:")
        print(f"🎯 Instrument: {setup.instrument}")
        print(f"🛑 Stop Loss: {setup.sl if setup.sl is not None else 'None'}")
        print(f"💰 Take Profits: {', '.join(str(tp) for tp in setup.tps) if setup.tps else 'None'}")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        return setup
    
    def _create_trade_signal(self, message_data: Dict[str, Any], action: str) -> Dict[str, Any]:
        """Create a trade signal from the message data"""
        message_text = message_data.get('text', '')
        
        # Create Setup object
        setup = self.create_setup_from_message(message_text)
        
        # Build signal dict
        signal = {
            'action': action,
            'symbol': setup.instrument if setup else message_text,
            'raw_message': message_text,
            'timestamp': message_data.get('time'),
            'source': f"{message_data.get('channel')} - {message_data.get('sender')}"
        }
        
        # Add setup if available
        if setup:
            signal['setup'] = setup
            
            # Also add stop loss and take profit to the main signal object for backward compatibility
            if setup.sl:
                signal['stop_loss'] = str(setup.sl)
            
            if setup.tps:
                if len(setup.tps) == 1:
                    signal['take_profit'] = str(setup.tps[0])
                else:
                    signal['take_profit_levels'] = [str(tp) for tp in setup.tps]
        
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
    
    def _extract_stop_loss(self, message_text: str) -> Optional[Union[str, float]]:
        """Extract stop loss value from message based on mappings"""
        message_lower = message_text.lower()
        
        for keyword, mapping, position in self.sl_mapping_table:
            if keyword in message_lower:
                # Find the index of the keyword
                keyword_index = message_lower.find(keyword)
                if keyword_index != -1:
                    # Extract numeric value based on position
                    if position.lower() == 'after':
                        # Look for number after the keyword
                        after_text = message_text[keyword_index + len(keyword):]
                        return self._extract_first_number(after_text)
                    elif position.lower() == 'before':
                        # Look for number before the keyword
                        before_text = message_text[:keyword_index]
                        return self._extract_last_number(before_text)
        
        return None
    
    def _extract_take_profit(self, message_text: str) -> Optional[Union[str, float, List]]:
        """Extract take profit value(s) from message based on mappings"""
        message_lower = message_text.lower()
        
        for keyword, mapping, position in self.tp_mapping_table:
            if keyword in message_lower:
                # Find the index of the keyword
                keyword_index = message_lower.find(keyword)
                if keyword_index != -1:
                    # Extract numeric value based on position
                    if position.lower() == 'after':
                        # Look for number(s) after the keyword
                        after_text = message_text[keyword_index + len(keyword):]
                        return self._extract_all_numbers(after_text)
                    elif position.lower() == 'before':
                        # Look for number before the keyword
                        before_text = message_text[:keyword_index]
                        return self._extract_last_number(before_text)
        
        return None
    
    def _extract_first_number(self, text: str) -> Optional[str]:
        """Extract the first number (integer or decimal) from text"""
        matches = re.findall(r'[-+]?\d*\.\d+|\d+', text)
        return matches[0] if matches else None
    
    def _extract_last_number(self, text: str) -> Optional[str]:
        """Extract the last number (integer or decimal) from text"""
        matches = re.findall(r'[-+]?\d*\.\d+|\d+', text)
        return matches[-1] if matches else None
    
    def _extract_all_numbers(self, text: str) -> List[str]:
        """Extract all numbers (integer or decimal) from text"""
        return re.findall(r'[-+]?\d*\.\d+|\d+', text)
    
    def _is_valid_decimal(self, value) -> bool:
        """Check if a value can be converted to Decimal"""
        try:
            Decimal(str(value))
            return True
        except (ValueError, TypeError):
            return False 