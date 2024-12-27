import discord
from discord.ext import commands

async def setup(bot):
    bot.add_command(sleep)
    bot.tree.add_command(intro)
    bot.tree.add_command(hello)
    bot.tree.add_command(smile)
    bot.tree.add_command(gn)
    bot.tree.add_command(love)

@commands.command()
async def sleep(ctx):
    await ctx.send("mua~ gn :heart: ")

# Slash command
@discord.app_commands.command(name="intro")
async def intro(interaction: discord.Interaction ):
    await interaction.response.send_message("My name is Huang Jun Jing Tony(Marco''s son)")

@discord.app_commands.command(name="hello")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message("大家好我係黃俊景")

@discord.app_commands.command(name="smile")
async def smile(interaction: discord.Interaction ):
    await interaction.response.send_message("黃俊景哈哈哈")

@discord.app_commands.command(name="gn")
async def gn(interaction: discord.Interaction ):
    await interaction.response.send_message("gn b:heart:")

@discord.app_commands.command(name="love")
async def love(interaction: discord.Interaction ):
    await interaction.response.send_message("2018-2023: O2\nNow: 他是")