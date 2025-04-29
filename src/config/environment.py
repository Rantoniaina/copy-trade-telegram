import os
import json
import getpass
from dotenv import load_dotenv, set_key
from src.models.mapping import Mapping
from src.models.configuration import Configuration, PositionType, PositionSL, PositionTP
from decimal import Decimal

def load_environment():
    """Load environment variables from .env file"""
    load_dotenv()

def get_env_or_input(env_var, prompt, is_secret=False):
    """Get value from environment variable or prompt user for input"""
    value = os.getenv(env_var)
    if not value:
        if is_secret:
            value = getpass.getpass(prompt)
        else:
            value = input(prompt)
    return value

def get_telegram_credentials():
    """Get Telegram API credentials either from env or by prompting user"""
    api_id = get_env_or_input('TELEGRAM_API_ID', '🆔 Enter Telegram API ID: ')
    api_hash = get_env_or_input('TELEGRAM_API_HASH', '🔑 Enter Telegram API Hash: ', is_secret=True)
    phone = get_env_or_input('TELEGRAM_PHONE', '📱 Enter phone number (with country code): ')
    channel = get_env_or_input('TELEGRAM_CHANNEL_TO_LISTEN', '📢 Enter Telegram channel to listen to: ')
    
    return {
        'api_id': api_id,
        'api_hash': api_hash,
        'phone': phone,
        'channel': channel
    }

def load_configuration():
    """Load configuration from environment variable"""
    config_json = os.getenv('CONFIGURATION')
    if not config_json:
        return None
    
    try:
        config_dict = json.loads(config_json)
        
        # Get buy and sell conditions
        buy_conditions = config_dict.get('buy_conditions', [])
        sell_conditions = config_dict.get('sell_conditions', [])
        
        # Create pair mapping objects
        pair_mappings = []
        for mapping_dict in config_dict.get('pair_mappings', []):
            pair_mappings.append(Mapping(
                from_message=mapping_dict.get('from_message', []),
                mapping=mapping_dict.get('mapping', '')
            ))
        
        # Create SL mapping objects
        sl_mappings = []
        for mapping_dict in config_dict.get('sl_mappings', []):
            sl_mappings.append(Mapping(
                from_message=mapping_dict.get('from_message', []),
                mapping=mapping_dict.get('mapping', ''),
                sl_position=mapping_dict.get('sl_position', 'after')
            ))
        
        # Create TP mapping objects
        tp_mappings = []
        for mapping_dict in config_dict.get('tp_mappings', []):
            tp_mappings.append(Mapping(
                from_message=mapping_dict.get('from_message', []),
                mapping=mapping_dict.get('mapping', ''),
                tp_position=mapping_dict.get('tp_position', 'after')
            ))
        
        # Get position type and interval
        position_type_str = config_dict.get('position_type', 'once')
        
        # Convert string to enum
        position_type = PositionType.ONCE
        if position_type_str.lower() == 'each':
            position_type = PositionType.EACH
        elif position_type_str.lower() == 'tp_length':
            position_type = PositionType.TP_LENGTH
        
        interval_minutes = config_dict.get('interval_minutes', 0)
        
        # Handle position SL
        position_sl_str = config_dict.get('position_sl', 'no_sl')
        position_sl = PositionSL.NO_SL
        
        if position_sl_str.lower() == 'signal_sl':
            position_sl = PositionSL.SIGNAL_SL
        elif position_sl_str.lower() == 'user_sl':
            position_sl = PositionSL.USER_SL
        
        # Handle position TP
        position_tp_str = config_dict.get('position_tp', 'no_tp')
        position_tp = PositionTP.NO_TP
        
        if position_tp_str.lower() == 'signal_tp':
            position_tp = PositionTP.SIGNAL_TP
        elif position_tp_str.lower() == 'user_tp':
            position_tp = PositionTP.USER_TP
        elif position_tp_str.lower() == 'alternate':
            position_tp = PositionTP.ALTERNATE
        
        # Handle stop loss and take profit
        stop_loss = None
        if position_sl == PositionSL.USER_SL and 'stop_loss' in config_dict:
            try:
                stop_loss = Decimal(str(config_dict.get('stop_loss')))
            except Exception as e:
                print(f"❌ Error parsing stop_loss value: {e}")
        
        take_profit = None
        if position_tp == PositionTP.USER_TP and 'take_profit' in config_dict:
            try:
                take_profit = Decimal(str(config_dict.get('take_profit')))
            except Exception as e:
                print(f"❌ Error parsing take_profit value: {e}")
        
        # Create and return Configuration object
        return Configuration(
            buy_conditions=buy_conditions,
            sell_conditions=sell_conditions,
            pair_mappings=pair_mappings,
            sl_mappings=sl_mappings,
            tp_mappings=tp_mappings,
            position_type=position_type,
            interval_minutes=interval_minutes,
            position_sl=position_sl,
            position_tp=position_tp,
            stop_loss=stop_loss,
            take_profit=take_profit
        )
    except json.JSONDecodeError:
        print("❌ Error: Invalid JSON in CONFIGURATION environment variable")
        return None
    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
        return None

def save_configuration(config: Configuration) -> bool:
    """Save configuration to environment variable and .env file"""
    try:
        # Convert Configuration object to dictionary
        config_dict = {
            'buy_conditions': config.buy_conditions,
            'sell_conditions': config.sell_conditions,
            'pair_mappings': [
                {
                    'from_message': m.from_message,
                    'mapping': m.mapping
                } for m in config.pair_mappings
            ],
            'sl_mappings': [
                {
                    'from_message': m.from_message,
                    'mapping': m.mapping,
                    'sl_position': m.sl_position
                } for m in config.sl_mappings
            ] if config.sl_mappings else [],
            'tp_mappings': [
                {
                    'from_message': m.from_message,
                    'mapping': m.mapping,
                    'tp_position': m.tp_position
                } for m in config.tp_mappings
            ] if config.tp_mappings else [],
            'position_type': config.position_type.value,
            'interval_minutes': config.interval_minutes,
            'position_sl': config.position_sl.value,
            'position_tp': config.position_tp.value
        }
        
        # Add stop_loss if it's set and position_sl is USER_SL
        if config.position_sl == PositionSL.USER_SL and config.stop_loss is not None:
            config_dict['stop_loss'] = float(config.stop_loss)
        
        # Add take_profit if it's set and position_tp is USER_TP
        if config.position_tp == PositionTP.USER_TP and config.take_profit is not None:
            config_dict['take_profit'] = float(config.take_profit)
        
        # Convert to JSON string
        config_json = json.dumps(config_dict)
        
        # Set environment variable
        os.environ['CONFIGURATION'] = config_json
        
        # Try to save to .env file if it exists
        env_file = '.env'
        if os.path.exists(env_file):
            set_key(env_file, 'CONFIGURATION', config_json)
            print(f"✅ Configuration saved to {env_file}")
        else:
            print("✅ Configuration saved to environment variable only")
            print("ℹ️  To persist configuration, create a .env file")
        
        return True
    except Exception as e:
        print(f"❌ Error saving configuration: {e}")
        return False 