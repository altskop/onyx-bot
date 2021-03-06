import discord
import asyncio
import os
from gtts import gTTS


if not discord.opus.is_loaded():
    # the 'opus' library here is opus.dll on windows
    # or libopus.so on linux in the current directory
    # you should replace this with the location the
    # opus library is located in and with the proper filename.
    # note that on windows this DLL is automatically provided for you
    discord.opus.load_opus('/usr/lib/libopus.so.0')


class Voice:
    def __init__(self, bot):
        self.bot = bot
        self.voice_clients = []
        self.tts_queue = {}

    async def connect(self, voice_channel: discord.VoiceChannel):
        voice_client = await voice_channel.connect()
        self.voice_clients.append(voice_client)
        while not voice_client.is_connected():
            await asyncio.sleep(1)
        return voice_client

    def play(self, client, source):
        client.play(source)

    async def play_tts(self, client, text):
        while client.is_playing() and client.is_connected():
            await asyncio.sleep(0.1)

        if client.is_connected():
            tts = gTTS(text=text, lang='en')
            tts.save("tts.mp3")
            source = discord.FFmpegPCMAudio("tts.mp3", options="-filter:a \"atempo="+self.bot.config.get("VOICE_SPEED")+"\"")
            self.play(client, source)

    def find_channel_by_user(self, user):
        guild_list = self.bot.guilds
        for guild in guild_list:
            voice_channels = guild.voice_channels
            for voice_channel in voice_channels:
                if user in voice_channel.members:
                    return voice_channel
        return None

    def is_in_voice_in_guild(self, guild) -> bool:
        for client in self.voice_clients:
            if client.channel.guild == guild:
                return True
        return False

    def is_in_voice_channel(self, channel) -> bool:
        for client in self.voice_clients:
            if client.channel.guild == channel.guild:
                if client.channel == channel:
                    return True
        return False

    async def get_voice_client_for_channel(self, channel):
        for client in self.voice_clients:
            if client.channel.guild == channel.guild:
                if client.channel == channel:
                    return client
                await client.move_to(channel)
                return client
        new_client = await self.connect(channel)
        return new_client

    async def disconnect_channel(self, channel):
        for client in self.voice_clients:
            if client.channel == channel:
                await self.stop_and_disconnect(client)
                return

    async def disconnect_voice_from_guild(self, guild):
        for client in self.voice_clients:
            if client.channel.guild == guild:
                await self.stop_and_disconnect(client)
                return

    async def stop_and_disconnect(self, client):
        client.stop()
        self.voice_clients.remove(client)
        await client.disconnect()

