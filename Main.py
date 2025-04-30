import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import threading
import asyncio
import sys

load_dotenv()  #Load all environmental variables from .env

# Create intents
intents = discord.Intents.default()
intents.messages = True  # Enable message intents
intents.guilds = True    # Enable guild intents
intents.message_content = True  # Enable message content intent

# Create bot instance
bot = commands.Bot(command_prefix='/', intents=intents)

def check_shutdown():
    while True:
        cmd = input("> ")
        if cmd.lower() == "logout":
            print("Logging out...")
            #safey close the bot
            # Schedule shutdown and wait for completion
            future = asyncio.run_coroutine_threadsafe(bot.close(), bot.loop)
            future.add_done_callback(lambda _: os._exit(0))
            break

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await bot.tree.sync()# Sync the application commands (slash commands) with Discord
    # Start the shutdown listener thread
    threading.Thread(target=check_shutdown, daemon=True).start()

async def load_extensions():
    await bot.load_extension("music_cog")
    await bot.load_extension("Conversation_cog")
    await bot.load_extension("connect4_cog")

@bot.event
async def setup_hook():
    await load_extensions()

@bot.event
async def on_disconnect():
    print("Bot disconnected successfully")
    sys.stdout.flush()
    # You could add reconnection logic here if needed

bot.run(os.getenv("DISCORD_TOKEN")) #Run the bot with discord token



