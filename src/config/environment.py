import os
import json
import getpass
from dotenv import load_dotenv, set_key
from src.models.setup import Setup
from src.models.mapping import Mapping
from src.models.configuration import Configuration

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

def load_setup_config():
    """Load setup configuration from environment variable"""
    setup_json = os.getenv('SETUP_CONFIG')
    if not setup_json:
        return None
    
    try:
        setup_dict = json.loads(setup_json)
        
        # Create and return Setup object
        return Setup(
            buy_conditions=setup_dict.get('buy_conditions', []),
            sell_conditions=setup_dict.get('sell_conditions', [])
        )
    except json.JSONDecodeError:
        print("❌ Error: Invalid JSON in SETUP_CONFIG environment variable")
        return None
    except Exception as e:
        print(f"❌ Error loading setup configuration: {e}")
        return None

def load_configuration():
    """Load configuration from environment variable"""
    config_json = os.getenv('CONFIGURATION')
    if not config_json:
        return None
    
    try:
        config_dict = json.loads(config_json)
        
        # Create Mapping objects
        mappings = []
        for mapping_dict in config_dict.get('mappings', []):
            mappings.append(Mapping(
                from_message=mapping_dict.get('from_message', []),
                mapping=mapping_dict.get('mapping', '')
            ))
        
        # Create and return Configuration object
        return Configuration(mappings=mappings)
    except json.JSONDecodeError:
        print("❌ Error: Invalid JSON in CONFIGURATION environment variable")
        return None
    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
        return None

def save_setup_config(setup: Setup) -> bool:
    """Save setup configuration to environment variable and .env file"""
    try:
        # Convert Setup object to dictionary
        setup_dict = {
            'buy_conditions': setup.buy_conditions,
            'sell_conditions': setup.sell_conditions
        }
        
        # Convert to JSON string
        setup_json = json.dumps(setup_dict)
        
        # Set environment variable
        os.environ['SETUP_CONFIG'] = setup_json
        
        # Try to save to .env file if it exists
        env_file = '.env'
        if os.path.exists(env_file):
            set_key(env_file, 'SETUP_CONFIG', setup_json)
            print(f"✅ Setup configuration saved to {env_file}")
        else:
            print("✅ Setup configuration saved to environment variable only")
            print("ℹ️  To persist configuration, create a .env file")
        
        return True
    except Exception as e:
        print(f"❌ Error saving setup configuration: {e}")
        return False

def save_configuration(config: Configuration) -> bool:
    """Save configuration to environment variable and .env file"""
    try:
        # Convert Configuration object to dictionary
        config_dict = {
            'mappings': [
                {
                    'from_message': m.from_message,
                    'mapping': m.mapping
                } for m in config.mappings
            ]
        }
        
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