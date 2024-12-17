import discord
from discord.ext import commands
from discord import ButtonStyle, Interaction, app_commands, PCMVolumeTransformer
from discord.ui import View, Button
from yt_dlp import YoutubeDL
from asyncio import Queue

class Music(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.music_queues = {}   # A dictionary to store queues for each guild
        self.YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'} # Set up YoutubeDL options
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

    # Play command using app_commands
    @app_commands.command(name="play", description="Play a YouTube video in voice channel")
    async def play(self, interaction: discord.Interaction, url: str):
        ctx = await self.bot.get_context(interaction)

        if not interaction.user.voice:
            await interaction.response.send_message("❌ You need to be in a voice channel to use this command.")
            return

        # Acknowledge the interaction immediately
        await interaction.response.defer()

        voice_channel = interaction.user.voice.channel
        if ctx.voice_client is None:
            await voice_channel.connect()
        elif ctx.voice_client.channel != voice_channel:
            await ctx.voice_client.move_to(voice_channel)

        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                url2 = info['url']
                title = info['title']
            except Exception:
                await interaction.followup.send("❌ Invalid YouTube link. Please provide a valid video URL.")
                return

        if interaction.guild.id not in self.music_queues:
            self.music_queues[interaction.guild.id] = Queue()

        await self.music_queues[interaction.guild.id].put((url2, title))
        await interaction.followup.send(f"✅ Added **{title}** to the queue!")

        if not ctx.voice_client.is_playing():
            await self.play_next(ctx)
            await interaction.channel.send(view=MusicControls(ctx, self))


    # Modified play_next function to handle errors better
    async def play_next(self, ctx):
        try:
            queue = self.music_queues.get(ctx.guild.id)
            if queue and not queue.empty():
                url, title = await queue.get()
                audio_source = discord.FFmpegPCMAudio(url, **self.FFMPEG_OPTIONS)
                transformed_source = PCMVolumeTransformer(audio_source, volume=1.0)

                if ctx.voice_client and ctx.voice_client.is_connected():
                    ctx.voice_client.play(transformed_source,
                                          after=lambda e: self.bot.loop.create_task(self.play_next(ctx)))
                    await ctx.channel.send(f"🎶 Now playing: **{title}**")
                else:
                    print("Voice client is not connected")
            else:
                if ctx.voice_client and ctx.voice_client.is_connected():
                    await ctx.voice_client.disconnect()
                if ctx.guild.id in self.music_queues:
                    del self.music_queues[ctx.guild.id]
        except Exception as e:
            print(f"Error in play_next: {str(e)}")
            await ctx.channel.send("❌ An error occurred while playing the song.")

    # Volume command using app_commands
    @app_commands.command(name="volume", description="Adjust the volume (0-200)")
    async def volume(self, interaction: discord.Interaction, newvolume: int):
        ctx = await self.bot.get_context(interaction)

        if not ctx.voice_client:
            await interaction.response.send_message("❌ I'm not connected to a voice channel.")
            return
        if not ctx.voice_client.source:
            await interaction.response.send_message("❌ I'm not playing anything.")
            return
        if 0 <= newvolume <= 200:
            ctx.voice_client.source.volume = newvolume / 100
            await interaction.response.send_message(f"🔊 Set the volume to {newvolume}%")
        else:
            await interaction.response.send_message("❌ Volume must be between 0 and 200.")


# Music Controls (Interactive Buttons)
class MusicControls(View):
    def __init__(self, ctx,music_cog):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.music_cog = music_cog

    @discord.ui.button(label="Skip", style=ButtonStyle.primary)
    async def skip_button(self, interaction: Interaction, button: Button):
        if not self.ctx.voice_client or not self.ctx.voice_client.is_playing():
            await interaction.response.send_message("❌ No music is currently playing.", ephemeral=True)
            return
        self.ctx.voice_client.stop()
        await interaction.response.send_message("⏭ Skipped the current song!")

    @discord.ui.button(label="Stop", style=ButtonStyle.danger)
    async def stop_button(self, interaction: Interaction, button: Button):
        if not self.ctx.voice_client:
            await interaction.response.send_message("❌ The bot is not connected to a voice channel.", ephemeral=True)
            return
        if self.ctx.guild.id in self.music_queues:
            del self.music_queues[self.ctx.guild.id]
        await self.ctx.voice_client.disconnect()
        await interaction.response.send_message("🛑 Music stopped and the bot has left the voice channel.")

    @discord.ui.button(label="Show Queue", style=ButtonStyle.secondary)
    async def queue_button(self, interaction: Interaction, button: Button):
        queue = self.music_queues.get(self.ctx.guild.id)
        if queue and not queue.empty():
            queue_list = list(queue._queue)
            queue_str = "\n".join([f"**{i + 1}. {item[1]}**" for i, item in enumerate(queue_list)])
            await interaction.response.send_message(f"🎵 **Music Queue:**\n{queue_str}", ephemeral=True)
        else:
            await interaction.response.send_message("🎵 The queue is currently empty.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Music(bot))



