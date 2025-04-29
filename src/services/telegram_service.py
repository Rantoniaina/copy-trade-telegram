import click
from telethon import TelegramClient
from telethon import events
from typing import Dict, Callable, Any


class TelegramService:
    def __init__(self, session_name: str = 'session_name'):
        self.client = None
        self.session_name = session_name
    
    async def connect(self, api_id: str, api_hash: str, phone: str) -> bool:
        """Connect to Telegram API and authenticate if needed"""
        # Initialize Telegram client
        self.client = TelegramClient(self.session_name, api_id, api_hash)
        
        try:
            # Connect to the client
            await self.client.connect()
            
            # Ensure we're authorized
            if not await self.client.is_user_authorized():
                click.echo("🔐 First time authentication needed.")
                await self.client.send_code_request(phone)
                code = input('🔢 Enter the code you received: ')
                await self.client.sign_in(phone, code)
            
            # Get client information
            me = await self.client.get_me()
            click.echo("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            click.echo(f"✅ Successfully connected as {me.first_name} (@{me.username})")
            click.echo("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            return True
            
        except Exception as e:
            click.echo("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            click.echo(f"❌ Failed to connect to Telegram: {e}")
            click.echo("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            return False
    
    def add_message_handler(self, channel: str, message_handler: Callable[[Dict[str, Any]], None], configuration=None):
        """Add event handler for new messages in the specified channel
        
        Parameters:
            channel: Channel to listen to
            message_handler: Callback for handling messages
            configuration: Optional Configuration object with buy_conditions and sell_conditions for filtering
        """
        if not self.client:
            raise Exception("Client not connected. Call connect() first.")
        
        # Pre-compute lowercase conditions for faster matching
        buy_conditions_lower = set()
        sell_conditions_lower = set()
        all_conditions_lower = set()
        
        if configuration and hasattr(configuration, 'buy_conditions') and hasattr(configuration, 'sell_conditions'):
            buy_conditions_lower = {condition.lower() for condition in configuration.buy_conditions}
            sell_conditions_lower = {condition.lower() for condition in configuration.sell_conditions}
            all_conditions_lower = buy_conditions_lower.union(sell_conditions_lower)
        
        @self.client.on(events.NewMessage(chats=channel))
        async def handler(event):
            sender = await event.get_sender()
            sender_name = getattr(sender, 'first_name', '') or getattr(sender, 'title', 'Unknown')
            
            # Format message data
            message_time = event.date.strftime('%Y-%m-%d %H:%M:%S')
            message_text = event.text
            message_data = {
                'channel': channel,
                'sender': sender_name,
                'time': message_time,
                'text': message_text
            }
            
            # Fast path: if no configuration or no conditions to check, process all messages
            should_process = True
            
            # Only do filtering if configuration and conditions exist
            if configuration and all_conditions_lower:
                should_process = False
                message_lower = message_text.lower()
                
                # Performance optimization: single pass through conditions
                # This is faster than separate loops for buy and sell conditions
                for condition in all_conditions_lower:
                    if condition in message_lower:
                        should_process = True
                        break
            
            if should_process:
                # Print message info first
                click.echo("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                click.echo(f"📩 New message from {channel}")
                click.echo(f"👤 Sender: {sender_name}")
                click.echo(f"⏰ Time: {message_time}")
                click.echo(f"💬 Message: {message_text}")
                click.echo("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                
                # Call the provided message handler to process trade signals
                if message_handler:
                    message_handler(message_data)
    
    async def run(self):
        """Run the client until disconnected"""
        if not self.client:
            raise Exception("Client not connected. Call connect() first.")
        
        click.echo("🚀 Client is now running and listening to channels")
        click.echo("📣 Waiting for new messages...")
        click.echo("⚠️  Press Ctrl+C to exit")
        await self.client.run_until_disconnected()
    
    async def disconnect(self):
        """Disconnect from Telegram"""
        if self.client and self.client.is_connected():
            click.echo("🔌 Disconnecting from Telegram...")
            await self.client.disconnect() 