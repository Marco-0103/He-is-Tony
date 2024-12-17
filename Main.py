import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

# Create intents
intents = discord.Intents.default()
intents.messages = True  # Enable message intents
intents.guilds = True    # Enable guild intents
intents.message_content = True  # Enable message content intent

# Create bot instance
bot = commands.Bot(command_prefix='/', intents=intents)

# Event triggered when the bot is ready
@bot.event
async def on_ready():
    await bot.tree.sync()  # Sync the application commands (slash commands) with Discord
    print(f'Logged in as {bot.user.name}')

async def load_extensions():
    await bot.load_extension("music_cog")

@bot.event
async def setup_hook():
    await load_extensions()

@bot.command()
async def sleep(ctx):
    await ctx.send("I am now in sleep mode and will back ASAP!")

@bot.command()
async def intro(ctx):
    await ctx.send('My name is Huang Jun Jing(Marco''s son)')

# Slash command
@bot.tree.command(name="hello")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message("大家好我係黃俊景")

@bot.tree.command(name="intro")
async def intro(interaction: discord.Interaction ):
    await interaction.response.send_message("My name is Huang Jun Jing Tony(Marco''s son)")

#@bot.tree.command(name="love")
#async def love(interaction: discord.Interaction ):
#   await interaction.response.send_message("2018-2023: O2\nNow: 他是")

@bot.tree.command(name="smile")
async def smile(interaction: discord.Interaction ):
    await interaction.response.send_message("黃俊景哈哈哈")

@bot.tree.command(name="gn")
async def smile(interaction: discord.Interaction ):
    await interaction.response.send_message("gn b:heart:")

@bot.event
async def on_disconnect():
    print("Bot has been disconnected.")


# Run the bot with your token
bot.run(os.getenv("DISCORD_TOKEN"))