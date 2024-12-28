import discord
from discord.ext import commands
from discord import ButtonStyle, Interaction, app_commands, PCMVolumeTransformer
from discord.ui import View, Button
from pyexpat.errors import messages
from yt_dlp import YoutubeDL
from asyncio import Queue


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.music_queues = {}
        self.YDL_OPTIONS = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False
        }
        self.FFMPEG_OPTIONS = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn'
        }

    @app_commands.command(name="play", description="Play a YouTube video in voice channel")
    async def play(self, interaction: discord.Interaction, url: str):
        print(f"Received Youtube URL: {url}")
        ctx = await self.bot.get_context(interaction)
        if not interaction.user.voice:
            await interaction.response.send_message("❌ You need to be in a voice channel to use this command.")
            return

        await interaction.response.defer()

        try:
            voice_channel = interaction.user.voice.channel
            if interaction.guild.id not in self.music_queues:
                self.music_queues[interaction.guild.id] = Queue()

            ctx = await self.bot.get_context(interaction)
            voice_client = ctx.voice_client

            if voice_client is None:
                voice_client = await voice_channel.connect()
            elif voice_client.channel != voice_channel:
                await voice_client.move_to(voice_channel)

            with YoutubeDL(self.YDL_OPTIONS) as ydl:
                try:
                    info = ydl.extract_info(url, download=False)
                    url2 = info['url']
                    title = info['title']
                except Exception as e:
                    await interaction.followup.send(f"❌ Error extracting video info: {str(e)}")
                    return

            await self.music_queues[interaction.guild.id].put((url2, title))
            await interaction.followup.send(f"✅ Added **{title}** to the queue!")

            if not voice_client.is_playing():
                await self.play_next(ctx)
                controls = MusicControls(ctx,self)
                message = await interaction.channel.send(view=controls)
                await controls.set_message(message)

        except Exception as e:
            await interaction.followup.send(f"❌ An error occurred: {str(e)}")

    async def play_next(self, ctx):
        try:
            if ctx.guild.id not in self.music_queues:
                return

            queue = self.music_queues[ctx.guild.id]
            if queue.empty():
                if ctx.voice_client:
                    await ctx.voice_client.disconnect()
                del self.music_queues[ctx.guild.id]
                return

            url, title = await queue.get()

            if not ctx.voice_client or not ctx.voice_client.is_connected():
                return

            audio_source = discord.FFmpegPCMAudio(url, **self.FFMPEG_OPTIONS)
            transformed_source = PCMVolumeTransformer(audio_source, volume=1.0)

            def after_playing(error):
                if error:
                    print(f"Error in playback: {error}")
                self.bot.loop.create_task(self.play_next(ctx))

            ctx.voice_client.play(transformed_source, after=after_playing)
            await ctx.channel.send(f"🎶 Now playing: **{title}**")

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
            await interaction.response.send_message(f"黃俊景(景b)🔊 Set the volume to {newvolume}%")
        else:
            await interaction.response.send_message("❌ Volume must be between 0 and 200.")


# Music Controls (Interactive Buttons)
class MusicControls(View):
    def __init__(self, ctx,music_cog):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.music_cog = music_cog
        self.message = None
        self.is_paused = False

    async def set_message(self,message):
        self.message = message

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
        if self.ctx.guild.id in self.music_cog.music_queues:
            del self.music_cog.music_queues[self.ctx.guild.id]
        await self.ctx.voice_client.disconnect()
        await interaction.response.send_message("🛑 Music stopped and the bot has left the voice channel.")

    @discord.ui.button(label="Show Queue", style=ButtonStyle.secondary)
    async def queue_button(self, interaction: Interaction, button: Button):
        queue = self.music_cog. music_queues.get(self.ctx.guild.id)
        if queue and not queue.empty():
            queue_list = list(queue._queue)
            queue_str = "\n".join([f"**{i + 1}. {item[1]}**" for i, item in enumerate(queue_list)])
            await interaction.response.send_message(f"🎵 **Music Queue:**\n{queue_str}", ephemeral=True)
        else:
            await interaction.response.send_message("🎵 The queue is currently empty.", ephemeral=True)


    #additional functions added on 27/12/24
    @discord.ui.button(label="Pause", style=ButtonStyle.primary)
    async def pause_resume_button(self, interaction: Interaction, button: Button):
        if not self.ctx.voice_client:
            await interaction.response.send_message("❌ Not playing any music. Tony mad😡 ", ephemeral=True)
            return

        if not self.is_paused:  #Music is playing, pause it.
            if self.ctx.voice_client.is_playing():
                self.ctx.voice_client.pause()
                button.label = "Resume"
                button.style = ButtonStyle.success
                self.is_paused = True
                await interaction.response.send_message("⏸ Music paused. Happy Tony😊")
                if self.message:
                    await self.message.edit(view=self)
            else:
                await interaction.response.send_message("❌ Music is not playing. Tony mad😡", ephemeral=True)
        else: #Music is paused, resume it
            if self.ctx.voice_client.is_paused():
                self.ctx.voice_client.resume()
                button.label = "Pause"
                button.style = ButtonStyle.secondary
                self.is_paused = False
                await interaction.response.send_message("▶ Music resumed. Happy tony😊")
                if self.message:
                    await self.message.edit(view=self)
            else:
                await interaction.response.send_message("❌ Music is not paused. Tony mad😡", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Music(bot))




