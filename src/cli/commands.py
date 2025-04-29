import click
import asyncio
import json
import os
from src.config.environment import (
    load_environment, 
    get_telegram_credentials,
    load_configuration,
    save_configuration
)
from src.services.telegram_service import TelegramService
from src.services.trade_service import TradeService
from src.models.mapping import Mapping
from src.models.configuration import Configuration, PositionType, PositionSL, PositionTP
from decimal import Decimal


@click.group()
def cli():
    """🤖 Telegram Copy Trade CLI application"""
    # Load environment variables from .env file
    load_environment()


@cli.command()
@click.option('--api-id', help='Telegram API ID')
@click.option('--api-hash', help='Telegram API Hash')
@click.option('--phone', help='Phone number (with country code)')
@click.option('--channel', help='Telegram channel to listen to')
def connect(api_id, api_hash, phone, channel):
    """🔌 Connect to Telegram API and start listening for trade signals"""
    # Get credentials
    credentials = get_telegram_credentials()
    
    # Override with command line args if provided
    if api_id:
        credentials['api_id'] = api_id
    if api_hash:
        credentials['api_hash'] = api_hash
    if phone:
        credentials['phone'] = phone
    if channel:
        credentials['channel'] = channel
    
    # Load configuration
    configuration = load_configuration()
    
    if not configuration:
        click.echo("⚙️ No configuration found. Let's configure it now.")
        configuration = configure_setup()
        if not configuration:
            click.echo("❌ Setup configuration cancelled.")
            return
    
    click.echo("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    click.echo(f"📲 Connecting to Telegram with phone: {credentials['phone']}...")
    click.echo(f"👂 Listening to channel: {credentials['channel']}")
    click.echo("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    # Run the async function using asyncio
    asyncio.run(connect_and_listen(credentials, configuration))


@cli.command()
def setup():
    """⚙️ Configure trading setup parameters"""
    configuration = configure_setup()
    if configuration:
        click.echo("✅ Setup configuration completed successfully!")
    else:
        click.echo("❌ Setup configuration cancelled.")


def configure_setup() -> Configuration:
    """Interactive configuration of trading setup and configuration"""
    click.echo("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    click.echo("⚙️ TRADING SETUP CONFIGURATION")
    click.echo("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    # Configure buy conditions
    click.echo("\n📈 Buy Conditions Configuration")
    click.echo("Enter keywords that indicate buy signals (comma-separated):")
    buy_input = input("Buy conditions (default: buy,long,bullish): ")
    buy_conditions = [s.strip() for s in buy_input.split(",")] if buy_input else ["buy", "long", "bullish"]
    
    # Configure sell conditions
    click.echo("\n📉 Sell Conditions Configuration")
    click.echo("Enter keywords that indicate sell signals (comma-separated):")
    sell_input = input("Sell conditions (default: sell,short,bearish): ")
    sell_conditions = [s.strip() for s in sell_input.split(",")] if sell_input else ["sell", "short", "bearish"]
    
    # Configure mappings
    pair_mappings = []
    click.echo("\n🔄 Symbol Mappings Configuration")
    click.echo("Let's configure how to map text in messages to trading symbols")
    
    add_more = True
    while add_more:
        click.echo("\nAdd a new mapping:")
        from_text = input("Keywords to look for (comma-separated): ")
        if not from_text:
            break
        
        mapping_value = input("Symbol to map to: ")
        if not mapping_value:
            break
        
        from_list = [s.strip() for s in from_text.split(",")]
        pair_mappings.append(Mapping(from_message=from_list, mapping=mapping_value))
        
        add_more_input = input("Add another mapping? (y/n): ")
        add_more = add_more_input.lower() == 'y'
    
    # If no mappings were added, add some defaults
    if not pair_mappings:
        click.echo("\nAdding default mappings for BTC and ETH...")
        pair_mappings = [
            Mapping(from_message=["BTC", "Bitcoin"], mapping="BTCUSDT"),
            Mapping(from_message=["ETH", "Ethereum"], mapping="ETHUSDT")
        ]
    
    # Configure stop loss mappings
    sl_mappings = []
    click.echo("\n🛑 Stop Loss Mappings Configuration")
    click.echo("Configure how to identify stop loss levels in messages")
    
    add_sl = input("Do you want to configure stop loss mappings? (y/n): ")
    if add_sl.lower() == 'y':
        add_more = True
        while add_more:
            click.echo("\nAdd a new stop loss mapping:")
            from_text = input("Keywords that indicate stop loss (comma-separated): ")
            if not from_text:
                break
            
            sl_position = input("Is the stop loss value before or after the keyword? (before/after, default: after): ")
            if sl_position.lower() not in ['before', 'after']:
                sl_position = 'after'
            
            from_list = [s.strip() for s in from_text.split(",")]
            sl_mappings.append(Mapping(
                from_message=from_list, 
                mapping="sl", 
                sl_position=sl_position
            ))
            
            add_more_input = input("Add another stop loss mapping? (y/n): ")
            add_more = add_more_input.lower() == 'y'
    
    # Configure take profit mappings
    tp_mappings = []
    click.echo("\n💰 Take Profit Mappings Configuration")
    click.echo("Configure how to identify take profit levels in messages")
    
    add_tp = input("Do you want to configure take profit mappings? (y/n): ")
    if add_tp.lower() == 'y':
        add_more = True
        while add_more:
            click.echo("\nAdd a new take profit mapping:")
            from_text = input("Keywords that indicate take profit (comma-separated): ")
            if not from_text:
                break
            
            tp_position = input("Is the take profit value before or after the keyword? (before/after, default: after): ")
            if tp_position.lower() not in ['before', 'after']:
                tp_position = 'after'
            
            from_list = [s.strip() for s in from_text.split(",")]
            tp_mappings.append(Mapping(
                from_message=from_list, 
                mapping="tp", 
                tp_position=tp_position
            ))
            
            add_more_input = input("Add another take profit mapping? (y/n): ")
            add_more = add_more_input.lower() == 'y'
    
    # Configure position type
    click.echo("\n⏱️ Position Timing Configuration")
    click.echo("Select position trigger type:")
    click.echo("1. ONCE - Trigger a position only once per signal")
    click.echo("2. EACH - Trigger a position each X minutes")
    click.echo("3. TP_LENGTH - Create as many positions as there are take profit levels")
    position_choice = input("Enter your choice (1, 2, or 3, default: 1): ")
    
    position_type = PositionType.ONCE
    interval_minutes = 0
    
    if position_choice == "2":
        position_type = PositionType.EACH
        interval_input = input("Enter interval in minutes (e.g., 5): ")
        try:
            interval_minutes = int(interval_input) if interval_input else 5
        except ValueError:
            click.echo("⚠️ Invalid interval value, using default of 5 minutes")
            interval_minutes = 5
    elif position_choice == "3":
        position_type = PositionType.TP_LENGTH
    
    # Configure stop loss
    click.echo("\n🛑 Stop Loss Configuration")
    click.echo("Select stop loss mode:")
    click.echo("1. NO_SL - No stop loss will be set")
    click.echo("2. SIGNAL_SL - Stop loss will be set based on the signal")
    click.echo("3. USER_SL - Stop loss will be set based on user configuration")
    sl_choice = input("Enter your choice (1, 2, or 3, default: 1): ")
    
    position_sl = PositionSL.NO_SL
    stop_loss = None
    
    if sl_choice == "2":
        position_sl = PositionSL.SIGNAL_SL
    elif sl_choice == "3":
        position_sl = PositionSL.USER_SL
        
        # Get stop loss percentage from user
        click.echo("\nEnter stop loss percentage (e.g., 5 for 5%)")
        sl_input = input("Stop loss percentage: ")
        try:
            stop_loss = Decimal(sl_input)
            if stop_loss <= 0:
                click.echo("⚠️ Stop loss must be greater than 0, using default of 5%")
                stop_loss = Decimal('5')
        except:
            click.echo("⚠️ Invalid stop loss value, using default of 5%")
            stop_loss = Decimal('5')
    
    # Configure take profit
    click.echo("\n💰 Take Profit Configuration")
    click.echo("Select take profit mode:")
    click.echo("1. NO_TP - No take profit will be set")
    click.echo("2. SIGNAL_TP - Take profit will be set based on the signal")
    click.echo("3. USER_TP - Take profit will be set based on user configuration")
    if position_type == PositionType.EACH:
        click.echo("4. ALTERNATE - Alternate between take profit levels for each position")
    
    tp_choice = input(f"Enter your choice (1, 2, 3{', or 4' if position_type == PositionType.EACH else ''}, default: 1): ")
    
    position_tp = PositionTP.NO_TP
    take_profit = None
    
    if tp_choice == "2":
        position_tp = PositionTP.SIGNAL_TP
    elif tp_choice == "3":
        position_tp = PositionTP.USER_TP
        
        # Get take profit percentage from user
        click.echo("\nEnter take profit percentage (e.g., 10 for 10%)")
        tp_input = input("Take profit percentage: ")
        try:
            take_profit = Decimal(tp_input)
            if take_profit <= 0:
                click.echo("⚠️ Take profit must be greater than 0, using default of 10%")
                take_profit = Decimal('10')
        except:
            click.echo("⚠️ Invalid take profit value, using default of 10%")
            take_profit = Decimal('10')
    elif tp_choice == "4" and position_type == PositionType.EACH:
        position_tp = PositionTP.ALTERNATE
    
    # Create the configuration
    configuration = Configuration(
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
    
    # Preview the configuration
    click.echo("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    click.echo("📋 CONFIGURATION SUMMARY")
    click.echo("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    click.echo(f"📈 Buy conditions: {', '.join(configuration.buy_conditions)}")
    click.echo(f"📉 Sell conditions: {', '.join(configuration.sell_conditions)}")
    click.echo("🔄 Pair Mappings:")
    for m in configuration.pair_mappings:
        click.echo(f"  - {', '.join(m.from_message)} → {m.mapping}")
    
    if configuration.sl_mappings:
        click.echo("🛑 Stop Loss Mappings:")
        for m in configuration.sl_mappings:
            click.echo(f"  - {', '.join(m.from_message)} ({m.sl_position})")
    
    if configuration.tp_mappings:
        click.echo("💰 Take Profit Mappings:")
        for m in configuration.tp_mappings:
            click.echo(f"  - {', '.join(m.from_message)} ({m.tp_position})")
    
    click.echo(f"⏱️ Position type: {position_type.value.upper()}")
    if position_type == PositionType.EACH:
        click.echo(f"⏱️ Interval: {interval_minutes} minutes")
    
    click.echo(f"🛑 Stop loss mode: {position_sl.value.upper()}")
    if position_sl == PositionSL.USER_SL and stop_loss is not None:
        click.echo(f"🛑 Stop loss percentage: {stop_loss}%")
    
    click.echo(f"💰 Take profit mode: {position_tp.value.upper()}")
    if position_tp == PositionTP.USER_TP and take_profit is not None:
        click.echo(f"💰 Take profit percentage: {take_profit}%")
    
    # Confirm and save
    confirm = input("\nSave this configuration? (y/n): ")
    if confirm.lower() == 'y':
        save_configuration(configuration)
        return configuration
    
    return None


async def connect_and_listen(credentials, configuration):
    """Connect to Telegram and listen for messages"""
    # Initialize services
    telegram_service = TelegramService()
    trade_service = TradeService(configuration)
    
    # Connect to Telegram
    connected = await telegram_service.connect(
        credentials['api_id'],
        credentials['api_hash'],
        credentials['phone']
    )
    
    if not connected:
        return
    
    # Define message handler
    def handle_message(message_data):
        # Process message for trade signals
        trade_signal = trade_service.process_message(message_data)
        if trade_signal:
            click.echo("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            click.echo(f"🔔 TRADE SIGNAL DETECTED: {trade_signal['action']} {trade_signal['symbol']}")
            click.echo(f"📊 Source: {trade_signal['source']}")
            click.echo(f"⏰ Time: {trade_signal['timestamp']}")
            click.echo("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            
            # Display setup information if available
            if 'setup' in trade_signal:
                setup = trade_signal['setup']
                click.echo("📐 SETUP DETAILS:")
                click.echo(f"🎯 Instrument: {setup.instrument}")
                
                if setup.sl:
                    click.echo(f"🛑 Stop Loss: {setup.sl}")
                else:
                    click.echo(f"🛑 Stop Loss: None")
                
                if setup.tps:
                    tp_str = ", ".join(str(tp) for tp in setup.tps)
                    click.echo(f"💰 Take Profit{'s' if len(setup.tps) > 1 else ''}: {tp_str}")
                else:
                    click.echo(f"💰 Take Profits: None")
                
                click.echo("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    # Add message handler
    telegram_service.add_message_handler(credentials['channel'], handle_message, configuration)
    
    try:
        # Run the client
        await telegram_service.run()
    except KeyboardInterrupt:
        click.echo("\n👋 Exiting by user request.")
    finally:
        # Disconnect
        await telegram_service.disconnect() 