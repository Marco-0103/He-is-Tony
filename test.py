from discord import FFmpegPCMAudio

# Define a sample audio file URL (or use a local file path)
sample_audio_url = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"

# Attempt to create an FFmpeg audio object
try:
    audio_source = FFmpegPCMAudio(sample_audio_url)
    print("FFmpeg is working correctly!")
except Exception as e:
    print(f"Error: {e}")