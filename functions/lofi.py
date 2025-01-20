import disnake
from init import bot
import yt_dlp
import asyncio
from disnake import opus
from variables import opus_path

try:
    opus.load_opus(opus_path)
    # print(f"Opus загружен из: {opus_path}")
except Exception as e:
    print(f"Ошибка загрузки Opus: {e}")
    raise RuntimeError("Не удалось загрузить библиотеку Opus.")
    
lofi_streams = {
    'jazz': "https://www.youtube.com/watch?v=HuFYqnbVbzY",
    'christmas': "https://www.youtube.com/watch?v=pfiCNAc2AgU",
    'classic': "https://www.youtube.com/watch?v=jfKfPfyJRdk"
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 2',
    'options': '-vn -bufsize 65536k'
}


class YTDLSource(disnake.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        ytdl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'extract-audio': True,
            'audio-format': 'mp3',
            'default_search': 'auto',
            'quiet': True,
            'no_warnings': True,
            'source_address': '0.0.0.0',
            'cookiefile': 'cookies.txt',
        }

        ytdl = yt_dlp.YoutubeDL(ytdl_opts)

        try:
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        except yt_dlp.utils.DownloadError:
            url = f'ytsearch:{url}'
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data and data['entries']:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(disnake.FFmpegPCMAudio(filename, **FFMPEG_OPTIONS), data=data)


async def connectVoice(voice_channel):
    
    if voice_channel.guild.voice_client:
        current_channel = voice_channel.guild.voice_client.channel
        if current_channel == voice_channel:
            return
        else:
            await voice_channel.guild.voice_client.disconnect()
            await voice_channel.connect()
    else:
        await voice_channel.connect()


@bot.listen("on_button_click")
async def lofi_listen(inter: disnake.MessageInteraction):
    if inter.component.custom_id not in ["lofi_stop", "lofi_jazz", "lofi_christmas", "lofi_classic"]:
        return
    if inter.component.custom_id == "lofi_stop":
        if inter.guild.voice_client:
            voice_client = inter.guild.voice_client

            if voice_client.is_playing():
                voice_client.stop()
            await voice_client.disconnect()

            await inter.send('## Музыка остановлена', ephemeral=True)
        else:
            await inter.send("## Бот не подключён к голосовому каналу.", ephemeral=True)
    elif inter.component.custom_id == "lofi_jazz":
        if inter.user.voice and inter.user.voice.channel:
            await connectVoice(inter.user.voice.channel)
            await inter.send("## Играет Jazz", ephemeral=True)
            voice_client = inter.guild.voice_client
            if voice_client:
                if voice_client.is_playing():
                    voice_client.stop()
            source = await YTDLSource.from_url(lofi_streams.get("jazz"), stream=True)
            inter.guild.voice_client.play(source)
        else:
            await inter.send("## Вы не находитесь в голосовом канале", ephemeral=True)
    elif inter.component.custom_id == "lofi_christmas":
        await inter.send("## Сейчас этот lofi недоступен")
        return
        if inter.user.voice and inter.user.voice.channel:
            await connectVoice(inter.user.voice.channel)
            await inter.send("## Играет Christmas", ephemeral=True)
            voice_client = inter.guild.voice_client
            if voice_client:
                if voice_client.is_playing():
                    voice_client.stop()
            source = await YTDLSource.from_url(lofi_streams.get("christmas"), stream=True)
            inter.guild.voice_client.play(source)
        else:
            await inter.send("## Вы не находитесь в голосовом канале", ephemeral=True)
    elif inter.component.custom_id == "lofi_classic":
        if inter.user.voice and inter.user.voice.channel:
            await connectVoice(inter.user.voice.channel)
            await inter.send("## Играет Classic", ephemeral=True)
            voice_client = inter.guild.voice_client
            if voice_client:
                if voice_client.is_playing():
                    voice_client.stop()
            source = await YTDLSource.from_url(lofi_streams.get("classic"), stream=True)
            inter.guild.voice_client.play(source)
        else:
            await inter.send("## Вы не находитесь в голосовом канале", ephemeral=True)