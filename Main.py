import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()  #Load all environmental variables from .env

# Create intents
intents = discord.Intents.default()
intents.messages = True  # Enable message intents
intents.guilds = True    # Enable guild intents
intents.message_content = True  # Enable message content intent

# Create bot instance
bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()  # Sync the application commands (slash commands) with Discord
    print(f'Logged in as {bot.user.name}')

async def load_extensions():
    await bot.load_extension("music_cog")
    await bot.load_extension("Conversation_cog")
    await bot.load_extension("connect4_cog")

@bot.event
async def setup_hook():
    await load_extensions()

@bot.event
async def on_disconnect():
    print("Bot has been disconnected.")

bot.run(os.getenv("DISCORD_TOKEN"))  #Run the bot with discord token



