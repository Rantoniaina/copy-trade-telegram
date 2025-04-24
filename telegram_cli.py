#!/usr/bin/env python3
import os
import click
import getpass
import asyncio
from dotenv import load_dotenv
from telethon import TelegramClient

def get_env_or_input(env_var, prompt, is_secret=False):
    """Get value from environment variable or prompt user for input"""
    value = os.getenv(env_var)
    if not value:
        if is_secret:
            value = getpass.getpass(prompt)
        else:
            value = input(prompt)
    return value

@click.group()
def cli():
    """Telegram CLI application"""
    # Load environment variables from .env file
    load_dotenv()

@cli.command()
@click.option('--api-id', help='Telegram API ID')
@click.option('--api-hash', help='Telegram API Hash')
@click.option('--phone', help='Phone number (with country code)')
def connect(api_id, api_hash, phone):
    """Connect to Telegram API"""
    # Use provided command line args, or .env values, or prompt
    api_id = api_id or get_env_or_input('TELEGRAM_API_ID', 'Enter Telegram API ID: ')
    api_hash = api_hash or get_env_or_input('TELEGRAM_API_HASH', 'Enter Telegram API Hash: ', is_secret=True)
    phone = phone or get_env_or_input('TELEGRAM_PHONE', 'Enter phone number (with country code): ')
    
    click.echo(f"Connecting to Telegram with phone: {phone}...")
    
    # Run the async function using asyncio
    asyncio.run(connect_telegram(api_id, api_hash, phone))

async def connect_telegram(api_id, api_hash, phone):
    """Async function to connect to Telegram"""
    # Initialize Telegram client
    client = TelegramClient('session_name', api_id, api_hash)
    
    # Start the client and connect
    try:
        # Connect to the client
        await client.connect()
        
        # Ensure we're authorized
        if not await client.is_user_authorized():
            click.echo("First time authentication needed.")
            await client.send_code_request(phone)
            code = input('Enter the code you received: ')
            await client.sign_in(phone, code)
        
        # Get client information
        me = await client.get_me()
        click.echo(f"Successfully connected as {me.first_name} (@{me.username})")
        
        # Keep the client running
        click.echo("Client is now running (Press Ctrl+C to exit)")
        await client.run_until_disconnected()
        
    except Exception as e:
        click.echo(f"Failed to connect to Telegram: {e}")
    finally:
        click.echo("Disconnecting from Telegram...")
        if client.is_connected():
            await client.disconnect()

if __name__ == '__main__':
    cli() 