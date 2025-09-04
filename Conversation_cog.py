import discord
from discord.ext import commands

async def setup(bot):
    bot.add_command(sleep)
    bot.tree.add_command(intro)
    bot.tree.add_command(bath)
    bot.tree.add_command(smile)
    bot.tree.add_command(gn)
    bot.tree.add_command(love)
    bot.tree.add_command(p)
    bot.tree.add_command(o2)
    bot.tree.add_command(bardog)
    bot.tree.add_command(心碎)

@commands.command()
async def sleep(ctx):
    await ctx.send("mua~ gn :heart: ")

# Slash command
@discord.app_commands.command(name="intro",description="Introduction to 他是Tony")
async def intro(interaction: discord.Interaction ):
    await interaction.response.send_message("My name is Huang Jun Jing Tony(Marco''s son)")

@discord.app_commands.command(name="bath")
async def bath(interaction: discord.Interaction):
    await interaction.response.send_message("Bath")

@discord.app_commands.command(name="smile",description="Smile Tony")
async def smile(interaction: discord.Interaction ):
    await interaction.response.send_message("黃俊景哈哈哈")

@discord.app_commands.command(name="gn",description="Say good night to 他是")
async def gn(interaction: discord.Interaction ):
    await interaction.response.send_message("gn 他是:heart:")

@discord.app_commands.command(name="love",description="Tony愛情史")
async def love(interaction: discord.Interaction ):
    await interaction.response.send_message("2018-2023: O2\n2024-2025: 他是\nnow: Nathan")

@discord.app_commands.command(name="p",description="Who play?")
async def p(interaction: discord.Interaction):
    await interaction.response.send_message("Who play?")

@discord.app_commands.command(name="o2",description="Tony heartbroken史")
async def o2(interaction: discord.Interaction):
    await interaction.response.send_message("I love O2 !!!")

@discord.app_commands.command(name="bardog",description="巴狗")
async def bardog(interaction: discord.Interaction):
    await interaction.response.send_message("巴狗萬歲")

@discord.app_commands.command(name="心碎",description="💔")
async def 心碎(interaction: discord.Interaction):
    await interaction.response.send_message("我失戀了💔")
