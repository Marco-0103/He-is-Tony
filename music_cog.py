import discord
from discord.ext import commands
from yt_dlp import YoutubeDL
from discord import FFmpegOpusAudio
import asyncio

class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queues = {}
        self.FFMPEG_OPTIONS = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn -c:a libopus -b:a 96k -ar 48000 -ac 2'
        }
        
        self.YDL_OPTIONS = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True,
            'extractaudio': True,
            'audioformat': 'opus',
            'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
        }

    def get_queue(self, ctx):
        guild_id = ctx.guild.id
        if guild_id not in self.queues:
            self.queues[guild_id] = []
        return self.queues[guild_id]

    async def play_next(self, ctx):
        queue = self.get_queue(ctx)
        if len(queue) > 0:
            url = queue.pop(0)
            try:
                player = await self.get_player(url)
                if player:
                    ctx.voice_client.play(player, after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.bot.loop))
                    await self.send_now_playing(ctx, url)
            except Exception as e:
                print(f"Error playing next song: {e}")
                await self.play_next(ctx)

    async def get_player(self, url):
        try:
            with YoutubeDL(self.YDL_OPTIONS) as ydl:
                info = ydl.extract_info(url, download=False)
                url2 = info['url']
                return FFmpegOpusAudio(url2, **self.FFMPEG_OPTIONS)
        except Exception as e:
            print(f"Error getting player: {e}")
            return None

    async def send_now_playing(self, ctx, url):
        try:
            with YoutubeDL(self.YDL_OPTIONS) as ydl:
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'Unknown Title')
                duration = info.get('duration', 0)
            
            embed = discord.Embed(
                title="Now Playing",
                description=f"[{title}]({url})",
                color=discord.Color.blue()
            )
            embed.add_field(name="Duration", value=self.format_duration(duration))
            await ctx.send(embed=embed)
        except Exception as e:
            print(f"Error sending now playing embed: {e}")

    def format_duration(self, seconds):
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        return f"{minutes}:{seconds:02d}"

    @commands.hybrid_command(name="play", description="Play music from YouTube")
    async def play(self, ctx, url: str):
        """Play music from a YouTube URL"""
        try:
            # Defer the response first to prevent interaction timeout
            if ctx.interaction:
                await ctx.interaction.response.defer()
            
            if ctx.voice_client is None:
                if ctx.author.voice:
                    await ctx.author.voice.channel.connect()
                else:
                    await ctx.send("You are not connected to a voice channel.")
                    return

            if ctx.voice_client.is_playing():
                queue = self.get_queue(ctx)
                queue.append(url)
                
                with YoutubeDL(self.YDL_OPTIONS) as ydl:
                    info = ydl.extract_info(url, download=False)
                    title = info.get('title', 'Unknown Title')
                
                embed = discord.Embed(
                    title="Added to Queue",
                    description=f"[{title}]({url})",
                    color=discord.Color.green()
                )
                embed.add_field(name="Position in queue", value=f"{len(queue)}")
                await ctx.send(embed=embed)
            else:
                player = await self.get_player(url)
                if player:
                    ctx.voice_client.play(player, after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.bot.loop))
                    await self.send_now_playing(ctx, url)
        except Exception as e:
            print(f"Error in play command: {e}")
            await ctx.send("An error occurred while processing your request.")

    @commands.hybrid_command(name="pause", description="Pause the current song")
    async def pause(self, ctx):
        """Pause the currently playing song"""
        if ctx.voice_client is None:
            await ctx.send("I'm not connected to a voice channel.")
            return
        
        if ctx.voice_client.is_paused():
            await ctx.send("Already paused.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send("⏸ Paused")
        else:
            await ctx.send("Nothing is playing.")

    @commands.hybrid_command(name="resume", description="Resume the current song")
    async def resume(self, ctx):
        """Resume the paused song"""
        if ctx.voice_client is None:
            await ctx.send("I'm not connected to a voice channel.")
            return
        
        if ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send("▶ Resumed")
        elif ctx.voice_client.is_playing():
            await ctx.send("Already playing.")
        else:
            await ctx.send("Nothing to resume.")

    @commands.hybrid_command(name="stop", description="Stop the current song and clear the queue")
    async def stop(self, ctx):
        """Stop playback and clear the queue"""
        if ctx.voice_client is None:
            await ctx.send("I'm not connected to a voice channel.")
            return
        
        ctx.voice_client.stop()
        self.get_queue(ctx).clear()
        await ctx.send("⏹ Stopped and cleared queue.")

    @commands.hybrid_command(name="skip", description="Skip the current song")
    async def skip(self, ctx):
        """Skip the currently playing song"""
        if ctx.voice_client is None:
            await ctx.send("I'm not connected to a voice channel.")
            return
        
        if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
            ctx.voice_client.stop()
            await ctx.send("⏭ Skipped")
            await self.play_next(ctx)
        else:
            await ctx.send("Nothing is playing.")

    @commands.hybrid_command(name="queue", description="Show the current queue")
    async def show_queue(self, ctx):
        """Show the current music queue"""
        try:
            # Defer the response immediately for slash commands
            if ctx.interaction:
                await ctx.interaction.response.defer()
            
            queue = self.get_queue(ctx)
            if len(queue) == 0:
                await ctx.send("The queue is empty.")
                return
            
            embed = discord.Embed(title="Music Queue", color=discord.Color.gold())
            
            # Process first item immediately to show something quickly
            if len(queue) > 0:
                try:
                    with YoutubeDL(self.YDL_OPTIONS) as ydl:
                        info = ydl.extract_info(queue[0], download=False)
                        title = info.get('title', 'Unknown Title')
                        duration = info.get('duration', 0)
                        embed.add_field(
                            name=f"1. {title}",
                            value=f"Duration: {self.format_duration(duration)}",
                            inline=False
                        )
                except:
                    embed.add_field(
                        name="1. [Unable to get info]",
                        value=queue[0],
                        inline=False
                    )
            
            # Process remaining items (if any)
            if len(queue) > 1:
                # Create a task to process the rest of the queue
                async def process_remaining():
                    for i, url in enumerate(queue[1:10], 2):  # Show first 10 items
                        try:
                            with YoutubeDL(self.YDL_OPTIONS) as ydl:
                                info = ydl.extract_info(url, download=False)
                                title = info.get('title', 'Unknown Title')
                                duration = info.get('duration', 0)
                                embed.add_field(
                                    name=f"{i}. {title}",
                                    value=f"Duration: {self.format_duration(duration)}",
                                    inline=False
                                )
                        except:
                            embed.add_field(
                                name=f"{i}. [Unable to get info]",
                                value=url,
                                inline=False
                            )
                    
                    if len(queue) > 10:
                        embed.set_footer(text=f"And {len(queue) - 10} more...")
                    
                    # Edit the original message with complete embed
                    try:
                        await ctx.edit(embed=embed)
                    except:
                        await ctx.send(embed=embed)
                
                # Start processing without waiting
                asyncio.create_task(process_remaining())
            
            # Send initial embed immediately
            await ctx.send(embed=embed)
            
        except Exception as e:
            print(f"Error showing queue: {e}")
            await ctx.send("An error occurred while processing the queue.")

    @play.before_invoke
    @pause.before_invoke
    @resume.before_invoke
    @stop.before_invoke
    @skip.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")

async def setup(bot):
    await bot.add_cog(MusicCog(bot))