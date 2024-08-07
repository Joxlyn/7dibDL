import discord
from discord.ext import commands
import yt_dlp as youtube_dl
#import youtube_dl
import os
from collections import deque
from collections import defaultdict
import asyncio
import datetime
from dotenv import load_dotenv
from discord.ext.commands import Context
from discord.ui import *
import aiohttp
from discord.utils import get
import random
from googlesearch import search
import subprocess

#from discord.ui import Button, View

load_dotenv()

intents = discord.Intents.all()
intents.voice_states = True
bot = commands.Bot(command_prefix='!', intents=intents)

queues = defaultdict(deque)
song_paused = defaultdict(bool)
file_counters = defaultdict(int)
current_songs = defaultdict(dict)
global_eq_filter = ""

class MenuMusica(discord.ui.View):

    @discord.ui.button(label="Agregar Cancion", row=0, style=discord.ButtonStyle.green)
    async def primer_button_callback(self, interaction, button):
        await play(interaction)

    @discord.ui.button(label="Pausar Cancion", row=0, style=discord.ButtonStyle.primary)
    async def segundo_button_callback(self, interaction, button):
        await pausar(interaction)

    @discord.ui.button(label="Reanudar Cancion", row=0, style=discord.ButtonStyle.primary)
    async def tercer_button_callback(self, interaction, button):
        await resume(interaction)

    @discord.ui.button(label="Saltar Cancion", row=0, style=discord.ButtonStyle.primary)
    async def cuarto_button_callback(self, interaction, button):
        await skip(interaction)

    @discord.ui.button(label="Repetir Cancion", row=1, style=discord.ButtonStyle.primary)
    async def quinto_button_callback(self, interaction, button):
        await repeat(interaction)

    @discord.ui.button(label="Bucle", row=1, style=discord.ButtonStyle.grey, disabled=True)
    async def sexto_button_callback(self, interaction, button):
        await detener(interaction)

    """
    @discord.ui.button(label="Detener Cancion", row=0, style=discord.ButtonStyle.primary)
    async def cuarto_button_callback(self, interaction, button):
        await detener(interaction)
    """

    @discord.ui.button(label="Mostrar Cancion Actual", row=1, style=discord.ButtonStyle.primary)
    async def septimo_button_callback(self, interaction, button):
        await np(interaction)

    @discord.ui.button(label="Mostrar Letra de la Cancion", row=1, style=discord.ButtonStyle.primary)
    async def octavo_button_callback(self, interaction, button):
        await lyrics(interaction)
    
    @discord.ui.button(label="Ver lista de canciones en espera", row=2, style=discord.ButtonStyle.primary)
    async def noveno_button_callback(self, interaction, button):
        await cola(interaction)

    @discord.ui.button(label="Limpiar lista de canciones", row=2, style=discord.ButtonStyle.primary)
    async def decimo_button_callback(self, interaction, button):
        await clear(interaction)

    @discord.ui.button(label="Join", row=2, style=discord.ButtonStyle.green)
    async def decimo_uno_button_callback(self, interaction, button):
        await join(interaction)

    @discord.ui.button(label="Desconectar", row=2, style=discord.ButtonStyle.red)
    async def decimo_dos_button_callback(self, interaction, button):
        await desconectar(interaction)

    
    # @discord.ui.button(label="24/7", row=3, style=discord.ButtonStyle.grey, disabled=True)
    # async def decimo_tres_button_callback(self, interaction, button):
    #     await skip(interaction)

    # @discord.ui.button(label="EQ", row=3, style=discord.ButtonStyle.grey, disabled=True)
    # async def decimo_cuatro_button_callback(self, interaction, button):
    #     await skip(interaction)

    # @discord.ui.button(label="Go To", row=3, style=discord.ButtonStyle.grey, disabled=True)
    # async def decimo_cinco_button_callback(self, interaction, button):
    #     await skip(interaction)
    
    # @discord.ui.button(label="playsong", row=3, style=discord.ButtonStyle.grey, disabled=True)
    # async def decimo_sexto_button_callback(self, interaction, button):
    #     await skip(interaction)

    # @discord.ui.button(label="remove", row=4, style=discord.ButtonStyle.grey, disabled=True)
    # async def decimo_septimo_button_callback(self, interaction, button):
    #     await skip(interaction)

    @discord.ui.button(label="Mostrar lista de comandos", row=4, style=discord.ButtonStyle.grey, disabled=True)
    async def decimo_octavo_button_callback(self, interaction, button):
        await bot.help_command(interaction)

class MyHelpCommand(commands.DefaultHelpCommand):
    def __init__(self):
        super().__init__()

    async def send_bot_help(self, mapping):
        ctx_or_interaction = self.context

        embed = discord.Embed(title="Comandos del Bot", description="Aquí tienes la lista de comandos disponibles:", color=discord.Color.blue())

        for cog, commands in mapping.items():
            if cog is None:
                # Ordena los comandos por nombre
                sorted_commands = sorted(commands, key=lambda x: x.name)

                for command in sorted_commands:
                    embed.add_field(name=f"**!{command.name}**", value=f"**Descripción:**\n{command.help}\n**Ejemplo:**\n*{command.usage}*\n**------------------------------------------------**\n", inline=False)

        if isinstance(ctx_or_interaction, discord.Interaction):
            embed.set_footer(text=f"Solicitado por {ctx_or_interaction.user.name}")
            await ctx_or_interaction.response.send_message(embed=embed)
        else:
            embed.set_footer(text=f"Solicitado por {ctx_or_interaction.author.name}")
            await ctx_or_interaction.send(embed=embed)

# Asigna el nuevo comando de ayuda al bot
bot.help_command = MyHelpCommand()

@bot.command(help='Sirve para mostrar un menu con las funciones principales del bot', usage='!menu')
async def menu(ctx_or_interaction):
    #await ctx.send("lista_button_callback_menu_discord_ui_Buttons: <discord.embeds.Embed object at 0x000001824D3F5A68>", view=MenuMusica()) # Send a message with our View class that contains the button
    embed = discord.Embed(title="MENU PRINCIPAL", description=f"¡Bienvenid@!\nDa clic en algun boton del menu principal para poder usar el bot", color=discord.Color(int("FFEE00", 16)))
    embed.set_footer(text=f"Solicitado por {ctx_or_interaction.author.name}")
    await ctx_or_interaction.send(embed=embed, view=MenuMusica())

@bot.command()
async def testButton(ctx):
    view = MusicButtonView()
    await ctx.send("Selecciona una opción:", view=view)

# Comando para configurar el filtro EQ globalmente
@bot.command(help='Sirve para configurar el ecualizador del bot. Existen estos ecualizadores: rock, hardrock, pop, electronica, metal, jazz, graves, bajos, voz, eco y default', usage='!set_eq {ecualizador-name}')
async def set_eq(ctx, eq_type):
    global global_eq_filter

    if eq_type == "rock":
        global_eq_filter = "equalizer=f=12800:width_type=h:width=50:g=5"

    elif eq_type == "hardrock":
        global_eq_filter = "equalizer=f=8000:width_type=h:width=50:g=-5"

    elif eq_type == "pop":
        global_eq_filter = "equalizer=f=16000:width_type=h:width=50:g=5"

    elif eq_type == "electronica":
        global_eq_filter = "equalizer=f=16000:width_type=h:width=50:g=-5"

    elif eq_type == "metal":
        global_eq_filter = "equalizer=f=8000:width_type=h:width=50:g=-5"

    elif eq_type == "jazz":
        global_eq_filter = "equalizer=f=19200:width_type=h:width=50:g=3"

    elif eq_type == "graves":
        global_eq_filter = "equalizer=f=40:width_type=h:width=50:g=-15"

    elif eq_type == "bajos":
        global_eq_filter = "equalizer=f=250:width_type=h:width=50:g=2"

    elif eq_type == "voz":
        global_eq_filter = "equalizer=f=8000:width_type=h:width=50:g=5"
    
    elif eq_type == "eco":
        global_eq_filter = "aecho=0.8:0.9:1000:0.3"

    elif eq_type == "novoz":
        global_eq_filter = "highpass=f=20000,lowpass=f=30000"
    
    elif eq_type == "default":
        global_eq_filter = "equalizer=f=100:width_type=h:width=50:g=0"

    elif eq_type == "test":
        global_eq_filter = "equalizer=f=10000000:width_type=h:width=50000000:g=10000000"

    else:
        embed = discord.Embed(title="Tipo de filtro EQ no válido. Usa algun filtro valido como lo son: 'rock', 'hardrock', 'pop', 'electronica', 'metal', 'jazz', 'graves', 'bajos', 'voz', 'eco' o 'default'.", color=discord.Color(int("F70000", 16)))
        embed.set_footer(text=f"Solicitado por {ctx.author.name}")
        await ctx.send(embed=embed)
        return

    embed = discord.Embed(title=f"Filtro EQ configurado como: **'{eq_type}'**", color=discord.Color(int("99AAB5", 16)))
    embed.set_footer(text=f"Solicitado por {ctx.author.name}")
    await ctx.send(embed=embed)
    print(f'Filtro utilizado: {global_eq_filter}')

async def reproducir_siguiente(ctx_or_interaction):
    await reproducir_siguiente_btn(ctx_or_interaction)

async def reproducir_siguiente_btn(ctx_or_interaction):
    global song_paused, file_counters, current_songs

    if isinstance(ctx_or_interaction, discord.Interaction):
        guild = ctx_or_interaction.guild
        voice_client = guild.voice_client
        author = ctx_or_interaction.user
        voice_state = author.voice
        voice_channel = voice_state.channel
    else:
        ctx = ctx_or_interaction
        guild = ctx.guild
        voice_client = ctx.voice_client
        voice_channel = ctx.author.voice.channel

    if isinstance(ctx_or_interaction, discord.Interaction):
        embed = discord.Embed(title="Cargando Siguiente Cancion...", color=discord.Color(int("FFEE00", 16)))
        embed.set_footer(text=f"Solicitado por {ctx_or_interaction.user.name}")
        await ctx_or_interaction.message.edit(embed=embed)  # Enviar un mensaje de respuesta inicial
    else:
        embed = discord.Embed(title="Cargando Siguiente Cancion...", color=discord.Color(int("FFEE00", 16)))
        embed.set_footer(text=f"Solicitado por {ctx_or_interaction.author.name}")
        await ctx_or_interaction.send(embed=embed)

    file_counters[guild.id] += 1

    if len(queues[guild.id]) == 0:
        current_songs[guild.id] = None
        return

    next_song = queues[guild.id].popleft()
    current_songs[guild.id] = next_song
    url = next_song['url']
    title = next_song['title']

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'opus',  # MP3
            'preferredquality': '192',  # 128, 192 o 320
        }],
        'outtmpl': f'audio/video{file_counters[guild.id]:02d}'  # Ruta de salida para guardar el archivo de audio
    }

    if not os.path.isfile('ffmpeg.exe'):
        if isinstance(ctx_or_interaction, discord.Interaction):
            embed = discord.Embed(title="FFmpeg no está instalado. Descarga manualmente FFmpeg y coloca 'ffmpeg.exe' en el mismo directorio que este script.", color=discord.Color(int("F70000", 16)))
            embed.set_footer(text=f"Solicitado por {ctx_or_interaction.user.name}")
            await ctx_or_interaction.message.edit(embed=embed)
        else:
            embed = discord.Embed(title="FFmpeg no está instalado. Descarga manualmente FFmpeg y coloca 'ffmpeg.exe' en el mismo directorio que este script.", color=discord.Color(int("F70000", 16)))
            embed.set_footer(text=f"Solicitado por {ctx_or_interaction.author.name}")
            await ctx_or_interaction.send(embed=embed)
        return

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        url2 = info['formats'][0]['url']

    if voice_channel is None:
        if isinstance(ctx_or_interaction, discord.Interaction):
            embed = discord.Embed(title="No estás en un canal de voz.", color=discord.Color(int("F70000", 16)))
            embed.set_footer(text=f"Solicitado por {ctx_or_interaction.user.name}")
            await ctx_or_interaction.message.edit(embed=embed)
        else:
            embed = discord.Embed(title="No estás en un canal de voz.", color=discord.Color(int("F70000", 16)))
            embed.set_footer(text=f"Solicitado por {ctx_or_interaction.author.name}")
            await ctx_or_interaction.send(embed=embed)
        return

    if voice_client is None:
        voice_client = await voice_channel.connect()
    elif voice_client.channel != voice_channel:
        await voice_client.move_to(voice_channel)

    voice_client.stop()
    duration = datetime.timedelta(seconds=info.get('duration', 0))
    duration_minutes = duration.seconds // 60
    duration_seconds = duration.seconds % 60
    current_songs[guild.id] = {
        'url': url,
        'title': title,
        'author': next_song['author'],
        'duration': info.get('duration', 0)  # Almacena la duración en segundos
    }
    filtroEQ = global_eq_filter

    source = discord.FFmpegPCMAudio(f'audio/video{file_counters[guild.id]:02d}.opus', options=[f'-b:a 320k', f'-af {filtroEQ}'])

    def after_playing(error):
        file_counters[guild.id] += 1
        asyncio.run_coroutine_threadsafe(reproducir_siguiente(ctx_or_interaction), bot.loop)

    voice_client.play(source, after=after_playing)

    duration = datetime.timedelta(seconds=info.get('duration', 0))
    duration_minutes = duration.seconds // 60
    duration_seconds = duration.seconds % 60

    embed = discord.Embed(title="Reproduciendo Cancion:", color=discord.Color(int("08FF10", 16)))
    embed.add_field(name="Nombre", value=title, inline=False)
    embed.add_field(name="Autor", value=info.get('uploader', 'Desconocido'), inline=False)
    embed.add_field(name="URL", value=url, inline=False)
    embed.add_field(name="Duración", value=f"{duration_minutes}:{duration_seconds:02d}", inline=False)
    embed.set_thumbnail(url=info.get('thumbnail', ''))
    embed.set_footer(text=f"Solicitado por {current_songs[guild.id]['author']}")
    if isinstance(ctx_or_interaction, discord.Interaction):
        await ctx_or_interaction.message.edit(embed=embed, view=MenuMusica())
    else:
        await ctx_or_interaction.send(embed=embed, view=MenuMusica())

    if song_paused[guild.id]:
        voice_client.pause()
        song_paused[guild.id] = False

@bot.event
async def on_ready():
    print(f'Conectado como {bot.user.name}')

@bot.command(help='Sirve para agregar una canción a la cola y después reproducirla', usage='!play {url-cancion}')
async def play(ctx, url=None):
    await play_btn(ctx, url)

async def play_btn(ctx_or_interaction, url):
    global file_counters, current_songs

    # Extrae la información necesaria del contexto del comando o la interacción
    if isinstance(ctx_or_interaction, discord.Interaction):
        ctx = ctx_or_interaction.channel
        guild = ctx_or_interaction.guild
        author_name = ctx_or_interaction.user.name
        voice_client = guild.voice_client
    else:
        ctx = ctx_or_interaction
        guild = ctx.guild
        author_name = ctx.author.name
        voice_client = ctx.voice_client

    # Para poder tener un mensaje principal cuando se usan botones y/o se escribe un comando manualmente.
    if isinstance(ctx_or_interaction, discord.Interaction):
        embed = discord.Embed(title="Ejecutando Comando...", color=discord.Color(int("FFEE00", 16)))
        embed.set_footer(text=f"Solicitado por {ctx_or_interaction.user.name}")
        await ctx_or_interaction.response.send_message(embed=embed, delete_after=0) # Mensaje inicial para evitar error de "Interaccion Fallida"
        
        embed = discord.Embed(title="Ejecutando Comando...", color=discord.Color(int("FFEE00", 16)))
        embed.set_footer(text=f"Solicitado por {ctx_or_interaction.user.name}")
        await ctx_or_interaction.message.edit(embed=embed) # Se edita el mensaje que envia el bot cuando se ejecuta "!menu"
    else:
        embed = discord.Embed(title="Ejecutando Comando...", color=discord.Color(int("FFEE00", 16)))
        embed.set_footer(text=f"Solicitado por {ctx_or_interaction.author.name}")
        await ctx_or_interaction.send(embed=embed)

    if url is None:
        if isinstance(ctx_or_interaction, discord.Interaction):
            embed = discord.Embed(title="Por favor, ingresa la URL de la canción.", color=discord.Color(int("FFEE00", 16)))
            embed.set_footer(text=f"Solicitado por {ctx_or_interaction.user.name}")
            await ctx_or_interaction.message.edit(embed=embed)
        else:
            embed = discord.Embed(title="Por favor, ingresa la URL de la canción.", color=discord.Color(int("FFEE00", 16)))
            embed.set_footer(text=f"Solicitado por {ctx_or_interaction.author.name}")
            await ctx_or_interaction.send(embed=embed)
        
        # Espera la respuesta del usuario en el mismo canal
        try:
            if isinstance(ctx_or_interaction, discord.Interaction):
                response = await bot.wait_for("message", check=lambda message: message.channel == ctx_or_interaction.channel and message.author == ctx_or_interaction.user, timeout=30)
            else:
                response = await bot.wait_for("message", check=lambda message: message.channel == ctx.channel and message.author == ctx.author, timeout=30)
            url = response.content.strip()
        except asyncio.TimeoutError:
            if isinstance(ctx_or_interaction, discord.Interaction):
                embed = discord.Embed(title="Se agoto el tiempo para ingresar la URL de la cancion. Por favor, vuelva a apretar el boton 'Agregar Cancion' y envie una URL valida para reproducir una cancion.", color=discord.Color(int("F70000", 16)))
                embed.set_footer(text=f"Solicitado por {ctx_or_interaction.user.name}")
                await ctx_or_interaction.message.edit(embed=embed)
            else:
                embed = discord.Embed(title="Se agoto el tiempo para ingresar la URL de la cancion. Por favor, vuelva a apretar el boton 'Agregar Cancion' y envie una URL valida para reproducir una cancion.", color=discord.Color(int("F70000", 16)))
                embed.set_footer(text=f"Solicitado por {ctx_or_interaction.author.name}")
                await ctx_or_interaction.send(embed=embed)
            return

    if isinstance(ctx_or_interaction, discord.Interaction):
        if not ctx_or_interaction.user.voice:
            embed = discord.Embed(title="Debes estar en un canal de voz para usar este comando.", color=discord.Color(int("F70000", 16)))
            embed.set_footer(text=f"Solicitado por {ctx_or_interaction.user.name}")
            await ctx_or_interaction.message.edit(embed=embed)
            return
    else:
        if not ctx.author.voice:
            embed = discord.Embed(title="Debes estar en un canal de voz para usar este comando.", color=discord.Color(int("F70000", 16)))
            embed.set_footer(text=f"Solicitado por {ctx_or_interaction.author.name}")
            await ctx_or_interaction.send(embed=embed)
            return

    # Continúa con el proceso de reproducción de la canción usando la URL proporcionada
    ydl_opts = {
        'verbose': True,
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'opus', #MP3
            'preferredquality': '192', #128, 192 o 320
        }],
        'outtmpl': f'audio/video{file_counters[guild.id]:02d}.opus'  # Ruta de salida para guardar el archivo de audio (.mp3)
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

        if 'entries' in info:
            # Es una playlist
            playlist_title = info['title']
            playlist_url = url
            playlist_author = author_name

            for entry in info['entries']:
                song_url = entry['webpage_url']
                song_title = entry['title']

                song = {
                    'url': song_url,
                    'title': song_title,
                    'author': playlist_author
                }

                queues[guild.id].append(song)

            embed = discord.Embed(title="Playlist agregada a la cola.", color=discord.Color(int("FFEE00", 16)))
            embed.add_field(name="Nombre", value=playlist_title, inline=False)
            embed.add_field(name="Autor", value=playlist_author, inline=False)
            embed.add_field(name="URL", value=playlist_url, inline=False)
            embed.set_footer(text=f"Solicitado por {ctx_or_interaction.user.name}" if isinstance(ctx_or_interaction, discord.Interaction) else f"Solicitado por {ctx_or_interaction.author.name}")

        else:
            # Es una canción individual
            title = info['title']

            song = {
                'url': url,
                'title': title,
                'author': author_name
            }

            queues[guild.id].append(song)

            embed = discord.Embed(title="Nueva canción agregada a la cola.", color=discord.Color(int("FFEE00", 16)))
            embed.add_field(name="Nombre", value=title, inline=False)
            embed.add_field(name="Autor", value=info.get('uploader', 'Desconocido'), inline=False)
            embed.add_field(name="URL", value=url, inline=False)
            embed.set_image(url=info.get('thumbnail', ''))
            embed.set_footer(text=f"Solicitado por {ctx_or_interaction.user.name}" if isinstance(ctx_or_interaction, discord.Interaction) else f"Solicitado por {ctx_or_interaction.author.name}")

    if isinstance(ctx_or_interaction, discord.Interaction):
        #await ctx_or_interaction.response.send_message(embed=embed)
        await ctx_or_interaction.message.edit(embed=embed)
        #pass
    else:
        await ctx_or_interaction.send(embed=embed)

    if len(queues[guild.id]) == 1 and (guild.voice_client is None or not guild.voice_client.is_playing()):
        current_songs[guild.id] = song
        await reproducir_siguiente(ctx_or_interaction)

@bot.command(help='Sirve para pausar la cancion actual', usage='!pausar')
async def pausar(ctx):
    await pausar_btn(ctx)

async def pausar_btn(ctx_or_interaction):
    if isinstance(ctx_or_interaction, discord.Interaction):
        guild = ctx_or_interaction.guild
        voice_client = guild.voice_client
    else:
        ctx = ctx_or_interaction
        guild = ctx.guild
        voice_client = ctx.voice_client

    # Para poder tener un mensaje principal cuando se usan botones y/o se escribe un comando manualmente.
    if isinstance(ctx_or_interaction, discord.Interaction):
        embed = discord.Embed(title="Ejecutando Comando...", color=discord.Color(int("FFEE00", 16)))
        embed.set_footer(text=f"Solicitado por {ctx_or_interaction.user.name}")
        await ctx_or_interaction.response.send_message(embed=embed, delete_after=0) # Mensaje inicial para evitar error de "Interaccion Fallida"
        
        embed = discord.Embed(title="Ejecutando Comando...", color=discord.Color(int("FFEE00", 16)))
        embed.set_footer(text=f"Solicitado por {ctx_or_interaction.user.name}")
        await ctx_or_interaction.message.edit(embed=embed) # Se edita el mensaje que envia el bot cuando se ejecuta "!menu"
    else:
        embed = discord.Embed(title="Ejecutando Comando...", color=discord.Color(int("FFEE00", 16)))
        embed.set_footer(text=f"Solicitado por {ctx_or_interaction.author.name}")
        await ctx_or_interaction.send(embed=embed)

    if voice_client and voice_client.is_playing():
        voice_client.pause()
        song_paused[guild.id] = True
        if isinstance(ctx_or_interaction, discord.Interaction):
            embed = discord.Embed(title="Cancion Pausada", color=discord.Color(int("FFEE00", 16)))
            embed.set_footer(text=f"Solicitado por {ctx_or_interaction.user.name}")
            await ctx_or_interaction.message.edit(embed=embed)
        else:
            embed = discord.Embed(title="Cancion Pausada", color=discord.Color(int("FFEE00", 16)))
            embed.set_footer(text=f"Solicitado por {ctx_or_interaction.author.name}")
            await ctx_or_interaction.send(embed=embed)
    else:
        if isinstance(ctx_or_interaction, discord.Interaction):
            embed = discord.Embed(title="Error al pausar la cancion. No se está reproduciendo ninguna canción o hay una cancion pausada actualmente.", color=discord.Color(int("F70000", 16)))
            embed.set_footer(text=f"Solicitado por {ctx_or_interaction.user.name}")
            await ctx_or_interaction.message.edit(embed=embed)
        else:
            embed = discord.Embed(title="Error al pausar la cancion. No se está reproduciendo ninguna canción o hay una cancion pausada actualmente.", color=discord.Color(int("F70000", 16)))
            embed.set_footer(text=f"Solicitado por {ctx_or_interaction.author.name}")
            await ctx_or_interaction.send(embed=embed)

@bot.command(help='Sirve para quitar la pausa de la cancion actual', usage='!resume')
async def resume(ctx):
    await resume_btn(ctx)

async def resume_btn(ctx_or_interaction):
    if isinstance(ctx_or_interaction, discord.Interaction):
        guild = ctx_or_interaction.guild
        voice_client = guild.voice_client
    else:
        ctx = ctx_or_interaction
        guild = ctx.guild
        voice_client = ctx.voice_client
    
    # Para poder tener un mensaje principal cuando se usan botones y/o se escribe un comando manualmente.
    if isinstance(ctx_or_interaction, discord.Interaction):
        embed = discord.Embed(title="Ejecutando Comando...", color=discord.Color(int("FFEE00", 16)))
        embed.set_footer(text=f"Solicitado por {ctx_or_interaction.user.name}")
        await ctx_or_interaction.response.send_message(embed=embed, delete_after=0) # Mensaje inicial para evitar error de "Interaccion Fallida"
        
        embed = discord.Embed(title="Ejecutando Comando...", color=discord.Color(int("FFEE00", 16)))
        embed.set_footer(text=f"Solicitado por {ctx_or_interaction.user.name}")
        await ctx_or_interaction.message.edit(embed=embed) # Se edita el mensaje que envia el bot cuando se ejecuta "!menu"
    else:
        embed = discord.Embed(title="Ejecutando Comando...", color=discord.Color(int("FFEE00", 16)))
        embed.set_footer(text=f"Solicitado por {ctx_or_interaction.author.name}")
        await ctx_or_interaction.send(embed=embed)

    if voice_client and voice_client.is_paused():
        voice_client.resume()
        song_paused[guild.id] = False
        if isinstance(ctx_or_interaction, discord.Interaction):
            embed = discord.Embed(title="La reproducción se ha reanudado.", color=discord.Color(int("08FF10", 16)))
            embed.set_footer(text=f"Solicitado por {ctx_or_interaction.user.name}")
            await ctx_or_interaction.message.edit(embed=embed)
        else:
            embed = discord.Embed(title="La reproducción se ha reanudado.", color=discord.Color(int("08FF10", 16)))
            embed.set_footer(text=f"Solicitado por {ctx_or_interaction.author.name}")
            await ctx_or_interaction.send(embed=embed)
    else:
        if isinstance(ctx_or_interaction, discord.Interaction):
            embed = discord.Embed(title="No se ha pausado ninguna canción.", color=discord.Color(int("F70000", 16)))
            embed.set_footer(text=f"Solicitado por {ctx_or_interaction.user.name}")
            await ctx_or_interaction.message.edit(embed=embed)
        else:
            embed = discord.Embed(title="No se ha pausado ninguna canción.", color=discord.Color(int("F70000", 16)))
            embed.set_footer(text=f"Solicitado por {ctx_or_interaction.author.name}")
            await ctx_or_interaction.send(embed=embed)

@bot.command(help='Sirve para saltar la cancion actual', usage='!skip')
async def skip(ctx):
    await skip_btn(ctx)

async def skip_btn(ctx_or_interaction):
    if isinstance(ctx_or_interaction, discord.Interaction):
        guild = ctx_or_interaction.guild
        voice_client = guild.voice_client
    else:
        ctx = ctx_or_interaction
        guild = ctx.guild
        voice_client = ctx.voice_client

    # Para poder tener un mensaje principal cuando se usan botones y/o se escribe un comando manualmente.
    if isinstance(ctx_or_interaction, discord.Interaction):
        embed = discord.Embed(title="Ejecutando Comando...", color=discord.Color(int("FFEE00", 16)))
        embed.set_footer(text=f"Solicitado por {ctx_or_interaction.user.name}")
        await ctx_or_interaction.response.send_message(embed=embed, delete_after=0) # Mensaje inicial para evitar error de "Interaccion Fallida"
        
        embed = discord.Embed(title="Ejecutando Comando...", color=discord.Color(int("FFEE00", 16)))
        embed.set_footer(text=f"Solicitado por {ctx_or_interaction.user.name}")
        await ctx_or_interaction.message.edit(embed=embed) # Se edita el mensaje que envia el bot cuando se ejecuta "!menu"
    else:
        embed = discord.Embed(title="Ejecutando Comando...", color=discord.Color(int("FFEE00", 16)))
        embed.set_footer(text=f"Solicitado por {ctx_or_interaction.author.name}")
        await ctx_or_interaction.send(embed=embed)

    if voice_client and voice_client.is_playing():
        voice_client.stop()
        if isinstance(ctx_or_interaction, discord.Interaction):
            embed = discord.Embed(title="Canción saltada.", color=discord.Color.blue())
            embed.set_footer(text=f"Solicitado por {ctx_or_interaction.user.name}")
            await ctx_or_interaction.message.edit(embed=embed)
        else:
            embed = discord.Embed(title="Canción saltada.", color=discord.Color.blue())
            embed.set_footer(text=f"Solicitado por {ctx_or_interaction.author.name}")
            await ctx_or_interaction.send(embed=embed)
    else:
        if isinstance(ctx_or_interaction, discord.Interaction):
            embed = discord.Embed(title="No se está reproduciendo ninguna canción.", color=discord.Color(int("F70000", 16)))
            embed.set_footer(text=f"Solicitado por {ctx_or_interaction.user.name}")
            await ctx_or_interaction.message.edit(embed=embed)
        else:
            embed = discord.Embed(title="No se está reproduciendo ninguna canción.", color=discord.Color(int("F70000", 16)))
            embed.set_footer(text=f"Solicitado por {ctx_or_interaction.author.name}")
            await ctx_or_interaction.send(embed=embed)


@bot.command(help='Sirve para detener la cancion actual', usage='!detener')
async def detener(ctx):
    await detener_btn(ctx)

async def detener_btn(ctx_or_interaction):
    if isinstance(ctx_or_interaction, discord.Interaction):
        guild = ctx_or_interaction.guild
        voice_client = guild.voice_client
    else:
        ctx = ctx_or_interaction
        guild = ctx.guild
        voice_client = ctx.voice_client

    # Para poder tener un mensaje principal cuando se usan botones y/o se escribe un comando manualmente.
    if isinstance(ctx_or_interaction, discord.Interaction):
        embed = discord.Embed(title="Ejecutando Comando...", color=discord.Color(int("FFEE00", 16)))
        embed.set_footer(text=f"Solicitado por {ctx_or_interaction.user.name}")
        await ctx_or_interaction.response.send_message(embed=embed, delete_after=0) # Mensaje inicial para evitar error de "Interaccion Fallida"
        
        embed = discord.Embed(title="Ejecutando Comando...", color=discord.Color(int("FFEE00", 16)))
        embed.set_footer(text=f"Solicitado por {ctx_or_interaction.user.name}")
        await ctx_or_interaction.message.edit(embed=embed) # Se edita el mensaje que envia el bot cuando se ejecuta "!menu"
    else:
        embed = discord.Embed(title="Ejecutando Comando...", color=discord.Color(int("FFEE00", 16)))
        embed.set_footer(text=f"Solicitado por {ctx_or_interaction.author.name}")
        await ctx_or_interaction.send(embed=embed)

    if voice_client is None:
        if isinstance(ctx_or_interaction, discord.Interaction):
            embed = discord.Embed(title="No estoy reproduciendo nada en este momento.", color=discord.Color(int("FFFFFF", 16)))
            embed.set_footer(text=f"Solicitado por {ctx_or_interaction.user.name}")
            await ctx_or_interaction.message.edit(embed=embed)
        else:
            embed = discord.Embed(title="No estoy reproduciendo nada en este momento.", color=discord.Color(int("FFFFFF", 16)))
            embed.set_footer(text=f"Solicitado por {ctx_or_interaction.author.name}")
            await ctx_or_interaction.send(embed=embed)
        return

    if voice_client.is_playing() or voice_client.is_paused():
        voice_client.stop()
        if isinstance(ctx_or_interaction, discord.Interaction):
            embed = discord.Embed(title="La reproducción se ha detenido.", color=discord.Color(int("F70000", 16)))
            embed.set_footer(text=f"Solicitado por {ctx_or_interaction.user.name}")
            await ctx_or_interaction.message.edit(embed=embed)
        else:
            embed = discord.Embed(title="La reproducción se ha detenido.", color=discord.Color(int("F70000", 16)))
            embed.set_footer(text=f"Solicitado por {ctx_or_interaction.author.name}")
            await ctx_or_interaction.send(embed=embed)
    else:
        if isinstance(ctx_or_interaction, discord.Interaction):
            embed = discord.Embed(title="No estoy reproduciendo nada en este momento.", color=discord.Color(int("F70000", 16)))
            embed.set_footer(text=f"Solicitado por {ctx_or_interaction.user.name}")
            await ctx_or_interaction.message.edit(embed=embed)
        else:
            embed = discord.Embed(title="No estoy reproduciendo nada en este momento.", color=discord.Color(int("F70000", 16)))
            embed.set_footer(text=f"Solicitado por {ctx_or_interaction.author.name}")
            await ctx_or_interaction.send(embed=embed)

@bot.command(help='Sirve para desconectar el bot del canal de voz', usage='!desconectar')
async def desconectar(ctx):
    await desconectar_btn(ctx)

async def desconectar_btn(ctx_or_interaction):
    if isinstance(ctx_or_interaction, discord.Interaction):
        guild = ctx_or_interaction.guild
        voice_client = guild.voice_client
    else:
        ctx = ctx_or_interaction
        guild = ctx.guild
        voice_client = guild.voice_client

    # Para poder tener un mensaje principal cuando se usan botones y/o se escribe un comando manualmente.
    if isinstance(ctx_or_interaction, discord.Interaction):
        embed = discord.Embed(title="Ejecutando Comando...", color=discord.Color(int("FFEE00", 16)))
        embed.set_footer(text=f"Solicitado por {ctx_or_interaction.user.name}")
        await ctx_or_interaction.response.send_message(embed=embed, delete_after=0) # Mensaje inicial para evitar error de "Interaccion Fallida"
        
        embed = discord.Embed(title="Ejecutando Comando...", color=discord.Color(int("FFEE00", 16)))
        embed.set_footer(text=f"Solicitado por {ctx_or_interaction.user.name}")
        await ctx_or_interaction.message.edit(embed=embed) # Se edita el mensaje que envia el bot cuando se ejecuta "!menu"
    else:
        embed = discord.Embed(title="Ejecutando Comando...", color=discord.Color(int("FFEE00", 16)))
        embed.set_footer(text=f"Solicitado por {ctx_or_interaction.author.name}")
        await ctx_or_interaction.send(embed=embed)

    # Verificar si el bot está conectado a un canal de voz
    if voice_client is None:
        if isinstance(ctx_or_interaction, discord.Interaction):
            embed = discord.Embed(title="No estoy conectado a ningún canal de voz.", color=discord.Color(int("F70000", 16)))
            embed.set_footer(text=f"Solicitado por {ctx_or_interaction.user.name}")
            await ctx_or_interaction.message.edit(embed=embed)
        else:
            embed = discord.Embed(title="No estoy conectado a ningún canal de voz.", color=discord.Color(int("F70000", 16)))
            embed.set_footer(text=f"Solicitado por {ctx_or_interaction.author.name}")
            await ctx_or_interaction.send(embed=embed)
        return

    # Desconectar del canal de voz si está conectado
    if voice_client.is_connected():
        await voice_client.disconnect()
        if isinstance(ctx_or_interaction, discord.Interaction):
            embed = discord.Embed(title="Desconectado del canal de voz.", color=discord.Color(int("08FF10", 16)))
            embed.set_footer(text=f"Solicitado por {ctx_or_interaction.user.name}")
            await ctx_or_interaction.message.edit(embed=embed)
        else:
            embed = discord.Embed(title="Desconectado del canal de voz.", color=discord.Color(int("08FF10", 16)))
            embed.set_footer(text=f"Solicitado por {ctx_or_interaction.author.name}")
            await ctx_or_interaction.send(embed=embed)
    else:
        if isinstance(ctx_or_interaction, discord.Interaction):
            embed = discord.Embed(title="No estoy conectado a ningún canal de voz.", color=discord.Color(int("F70000", 16)))
            embed.set_footer(text=f"Solicitado por {ctx_or_interaction.user.name}")
            await ctx_or_interaction.message.edit(embed=embed)
        else:
            embed = discord.Embed(title="No estoy conectado a ningún canal de voz.", color=discord.Color(int("F70000", 16)))
            embed.set_footer(text=f"Solicitado por {ctx_or_interaction.author.name}")
            await ctx_or_interaction.send(embed=embed)

@bot.command(help='Sirve para ver la lista de canciones que se encuentran en espera o cola', usage='!cola')
async def cola(ctx):
    await cola_btn(ctx)

async def cola_btn(ctx_or_interaction):
    if isinstance(ctx_or_interaction, discord.Interaction):
        guild = ctx_or_interaction.guild
    else:
        ctx = ctx_or_interaction
        guild = ctx.guild

    # Para poder tener un mensaje principal cuando se usan botones y/o se escribe un comando manualmente.
    if isinstance(ctx_or_interaction, discord.Interaction):
        embed = discord.Embed(title="Ejecutando Comando...", color=discord.Color(int("FFEE00", 16)))
        embed.set_footer(text=f"Solicitado por {ctx_or_interaction.user.name}")
        await ctx_or_interaction.response.send_message(embed=embed, delete_after=0) # Mensaje inicial para evitar error de "Interaccion Fallida"
        
        embed = discord.Embed(title="Ejecutando Comando...", color=discord.Color(int("FFEE00", 16)))
        embed.set_footer(text=f"Solicitado por {ctx_or_interaction.user.name}")
        await ctx_or_interaction.message.edit(embed=embed) # Se edita el mensaje que envia el bot cuando se ejecuta "!menu"
    else:
        embed = discord.Embed(title="Ejecutando Comando...", color=discord.Color(int("FFEE00", 16)))
        embed.set_footer(text=f"Solicitado por {ctx_or_interaction.author.name}")
        await ctx_or_interaction.send(embed=embed)

    if len(queues[guild.id]) == 0:
        if isinstance(ctx_or_interaction, discord.Interaction):
            embed = discord.Embed(title="No hay canciones en la cola.", color=discord.Color(int("F70000", 16)))
            embed.set_footer(text=f"Solicitado por {ctx_or_interaction.user.name}")
            await ctx_or_interaction.message.edit(embed=embed)
        else:
            embed = discord.Embed(title="No hay canciones en la cola.", color=discord.Color(int("F70000", 16)))
            embed.set_footer(text=f"Solicitado por {ctx_or_interaction.author.name}")
            await ctx_or_interaction.send(embed=embed)
    else:
        embed = discord.Embed(title="Canciones en cola", color=discord.Color(int("FFEE00", 16)))
        embed.set_footer(text=f"Solicitado por {ctx_or_interaction.user.name}" if isinstance(ctx_or_interaction, discord.Interaction) else f"Solicitado por {ctx_or_interaction.author.name}")

        for i, song in enumerate(queues[guild.id]):
            title = song["title"]
            embed.add_field(name=f"{i+1}. {title}", value="\u200b", inline=False)

        if isinstance(ctx_or_interaction, discord.Interaction):
            await ctx_or_interaction.message.edit(embed=embed)
        else:
            await ctx_or_interaction.send(embed=embed)

@bot.command(help='Sirve para limpiar la lista de canciones que se encuentran en espera o cola', usage='!clear')
async def clear(ctx):
    await clear_btn(ctx)

async def clear_btn(ctx_or_interaction):
    global queues, file_counters
    
    # Extrae la información necesaria del contexto del comando o la interacción
    if isinstance(ctx_or_interaction, discord.Interaction):
        guild = ctx_or_interaction.guild
    else:
        ctx = ctx_or_interaction
        guild = ctx.guild

    # Para poder tener un mensaje principal cuando se usan botones y/o se escribe un comando manualmente.
    if isinstance(ctx_or_interaction, discord.Interaction):
        embed = discord.Embed(title="Ejecutando Comando...", color=discord.Color(int("FFEE00", 16)))
        embed.set_footer(text=f"Solicitado por {ctx_or_interaction.user.name}")
        await ctx_or_interaction.response.send_message(embed=embed, delete_after=0) # Mensaje inicial para evitar error de "Interaccion Fallida"
        
        embed = discord.Embed(title="Ejecutando Comando...", color=discord.Color(int("FFEE00", 16)))
        embed.set_footer(text=f"Solicitado por {ctx_or_interaction.user.name}")
        await ctx_or_interaction.message.edit(embed=embed) # Se edita el mensaje que envia el bot cuando se ejecuta "!menu"
    else:
        embed = discord.Embed(title="Ejecutando Comando...", color=discord.Color(int("FFEE00", 16)))
        embed.set_footer(text=f"Solicitado por {ctx_or_interaction.author.name}")
        await ctx_or_interaction.send(embed=embed)

    # Limpiar la cola de canciones
    queues[guild.id].clear()
    
    # Eliminar archivos descargados
    try:
        files = os.listdir('audio')
        for file in files:
            if file.startswith('video'):
                os.remove(os.path.join('audio', file))
        file_counters[guild.id] = 1
        if isinstance(ctx_or_interaction, discord.Interaction):
            embed = discord.Embed(title="La cola de canciones ha sido limpiada.", color=discord.Color(int("FFFFFF", 16)))
            embed.set_footer(text=f"Solicitado por {ctx_or_interaction.user.name}")
            await ctx_or_interaction.message.edit(embed=embed)
        else:
            embed = discord.Embed(title="La cola de canciones ha sido limpiada.", color=discord.Color(int("FFFFFF", 16)))
            embed.set_footer(text=f"Solicitado por {ctx_or_interaction.author.name}")
            await ctx_or_interaction.send(embed=embed)
    except Exception as e:
        # Para debug
        if isinstance(ctx_or_interaction, discord.Interaction):
            embed = discord.Embed(title=f'Error al eliminar archivos: {e}', color=discord.Color(int("F70000", 16)))
            embed.set_footer(text=f"Solicitado por {ctx_or_interaction.user.name}")
            await ctx_or_interaction.message.edit(embed=embed)
        else:
            embed = discord.Embed(title=f'Error al eliminar archivos: {e}', color=discord.Color(int("F70000", 16)))
            embed.set_footer(text=f"Solicitado por {ctx_or_interaction.author.name}")
            await ctx_or_interaction.send(embed=embed)
        print(f'Error al eliminar archivos: {e}')

@bot.command(help='Sirve para ver que cancion se esta reproduciendo actualmente', usage='!np')
async def np(ctx):
    await np_btn(ctx)

async def np_btn(ctx_or_interaction):
    guild = ctx_or_interaction.guild

    # Para poder tener un mensaje principal cuando se usan botones y/o se escribe un comando manualmente.
    if isinstance(ctx_or_interaction, discord.Interaction):
        embed = discord.Embed(title="Ejecutando Comando...", color=discord.Color(int("FFEE00", 16)))
        embed.set_footer(text=f"Solicitado por {ctx_or_interaction.user.name}")
        await ctx_or_interaction.response.send_message(embed=embed, delete_after=0) # Mensaje inicial para evitar error de "Interaccion Fallida"
        
        embed = discord.Embed(title="Ejecutando Comando...", color=discord.Color(int("FFEE00", 16)))
        embed.set_footer(text=f"Solicitado por {ctx_or_interaction.user.name}")
        await ctx_or_interaction.message.edit(embed=embed) # Se edita el mensaje que envia el bot cuando se ejecuta "!menu"
    else:
        embed = discord.Embed(title="Ejecutando Comando...", color=discord.Color(int("FFEE00", 16)))
        embed.set_footer(text=f"Solicitado por {ctx_or_interaction.author.name}")
        await ctx_or_interaction.send(embed=embed)

    # Verificar si hay un título de una canción
    if current_songs[guild.id] is None or 'title' not in current_songs[guild.id]:
        if isinstance(ctx_or_interaction, discord.Interaction):
            embed = discord.Embed(title="No se está reproduciendo ninguna canción en este momento.", color=discord.Color(int("F70000", 16)))
            embed.set_footer(text=f"Solicitado por {ctx_or_interaction.user.name}")
            await ctx_or_interaction.message.edit(embed=embed)
        else:
            embed = discord.Embed(title="No se está reproduciendo ninguna canción en este momento.", color=discord.Color(int("F70000", 16)))
            embed.set_footer(text=f"Solicitado por {ctx_or_interaction.author.name}")
            await ctx_or_interaction.send(embed=embed)
        return

    if current_songs[guild.id] is None:
        if isinstance(ctx_or_interaction, discord.Interaction):
            embed = discord.Embed(title="No se está reproduciendo ninguna canción en este momento.", color=discord.Color(int("F70000", 16)))
            embed.set_footer(text=f"Solicitado por {ctx_or_interaction.user.name}")
            await ctx_or_interaction.message.edit(embed=embed)
        else:
            embed = discord.Embed(title="No se está reproduciendo ninguna canción en este momento.", color=discord.Color(int("F70000", 16)))
            embed.set_footer(text=f"Solicitado por {ctx_or_interaction.author.name}")
            await ctx_or_interaction.send(embed=embed)
    else:
        if isinstance(ctx_or_interaction, discord.Interaction):
            author = ctx_or_interaction.user
            voice_state = author.voice
            if voice_state is None or voice_state.channel is None:
                embed = discord.Embed(title="No estás en un canal de voz.", color=discord.Color(int("F70000", 16)))
                embed.set_footer(text=f"Solicitado por {ctx_or_interaction.user.name}")
                await ctx_or_interaction.message.edit(embed=embed)
                return
            voice_channel = voice_state.channel
            embed = discord.Embed(title="Cargando Informacion de la Cancion Actual...", color=discord.Color(int("FFEE00", 16)))
            embed.set_footer(text=f"Solicitado por {ctx_or_interaction.user.name}")
            await ctx_or_interaction.message.edit(embed=embed)
        else:
            ctx = ctx_or_interaction
            voice_channel = ctx.author.voice.channel
            embed = discord.Embed(title="Cargando Informacion de la Cancion Actual...", color=discord.Color(int("FFEE00", 16)))
            embed.set_footer(text=f"Solicitado por {ctx_or_interaction.author.name}")
            await ctx_or_interaction.send(embed=embed)

        title = current_songs[guild.id]['title']
        url = current_songs[guild.id]['url']

        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'opus', #MP3
                'preferredquality': '192', #128, 192 o 320
            }],
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        author = info.get('uploader', 'Desconocido')
        duration = datetime.timedelta(seconds=info.get('duration', 0))
        duration_minutes = duration.seconds // 60
        duration_seconds = duration.seconds % 60
        thumbnail = info.get('thumbnail', '')

        # Crear la vista de los botones y añadir los botones
        if isinstance(ctx_or_interaction, discord.Interaction):
            embed = discord.Embed(title="Canción actual:", color=discord.Color(int("08FF10", 16)))
            embed.add_field(name="Nombre", value=title, inline=False)
            embed.add_field(name="Autor", value=author, inline=False)
            embed.add_field(name="URL", value=url, inline=False)
            embed.add_field(name="Duración", value=f"{duration_minutes}:{duration_seconds:02d}", inline=False)
            embed.set_thumbnail(url=thumbnail)
            embed.set_footer(text=f"Solicitado por {ctx_or_interaction.user.name}")
            await ctx_or_interaction.message.edit(embed=embed, view=MenuMusica())
        else:
            embed = discord.Embed(title="Canción actual:", color=discord.Color(int("08FF10", 16)))
            embed.add_field(name="Nombre", value=title, inline=False)
            embed.add_field(name="Autor", value=author, inline=False)
            embed.add_field(name="URL", value=url, inline=False)
            embed.add_field(name="Duración", value=f"{duration_minutes}:{duration_seconds:02d}", inline=False)
            embed.set_thumbnail(url=thumbnail)
            embed.set_footer(text=f"Solicitado por {ctx_or_interaction.author.name}")
            await ctx_or_interaction.send(embed=embed, view=MenuMusica())

@bot.command(help='Sirve para añadir el bot al canal de voz que se encuentra el usuario', usage='!join')
async def join(ctx):
    await join_btn(ctx)

async def join_btn(ctx_or_interaction):
    # Extrae la información necesaria del contexto del comando o la interacción
    if isinstance(ctx_or_interaction, discord.Interaction):
        guild = ctx_or_interaction.guild
        author = ctx_or_interaction.user
        voice_client = guild.voice_client
    else:
        ctx = ctx_or_interaction
        guild = ctx.guild
        author = ctx.author
        voice_client = guild.voice_client

    # Para poder tener un mensaje principal cuando se usan botones y/o se escribe un comando manualmente.
    if isinstance(ctx_or_interaction, discord.Interaction):
        embed = discord.Embed(title="Ejecutando Comando...", color=discord.Color(int("FFEE00", 16)))
        embed.set_footer(text=f"Solicitado por {ctx_or_interaction.user.name}")
        await ctx_or_interaction.response.send_message(embed=embed, delete_after=0) # Mensaje inicial para evitar error de "Interaccion Fallida"
        
        embed = discord.Embed(title="Ejecutando Comando...", color=discord.Color(int("FFEE00", 16)))
        embed.set_footer(text=f"Solicitado por {ctx_or_interaction.user.name}")
        await ctx_or_interaction.message.edit(embed=embed) # Se edita el mensaje que envia el bot cuando se ejecuta "!menu"
    else:
        embed = discord.Embed(title="Ejecutando Comando...", color=discord.Color(int("FFEE00", 16)))
        embed.set_footer(text=f"Solicitado por {ctx_or_interaction.author.name}")
        await ctx_or_interaction.send(embed=embed)

    # Verificar si el bot está en un canal de voz
    if voice_client is None:
        # Verificar si el autor está en un canal de voz
        if author.voice:
            channel = author.voice.channel
            await channel.connect()
            #await channel.connect(bitrate=320000)
        else:
            if isinstance(ctx_or_interaction, discord.Interaction):
                embed = discord.Embed(title="Debes estar en un canal de voz para usar este comando.", color=discord.Color(int("F70000", 16)))
                embed.set_footer(text=f"Solicitado por {ctx_or_interaction.user.name}")
                await ctx_or_interaction.message.edit(embed=embed)
            else:
                embed = discord.Embed(title="Debes estar en un canal de voz para usar este comando.", color=discord.Color(int("F70000", 16)))
                embed.set_footer(text=f"Solicitado por {ctx_or_interaction.author.name}")
                await ctx_or_interaction.send(embed=embed)
            return
    else:
        # Mover al bot al canal de voz del autor
        await voice_client.move_to(author.voice.channel)

    if isinstance(ctx_or_interaction, discord.Interaction):
        embed = discord.Embed(title="Unido al canal de voz.", description="Por favor, ejecuta el comando '!menu' (sin las comillas) para poder utilizar el bot.", color=discord.Color(int("08FF10", 16)))
        embed.set_footer(text=f"Solicitado por {ctx_or_interaction.user.name}")
        await ctx_or_interaction.message.edit(embed=embed)
    else:
        embed = discord.Embed(title="Unido al canal de voz.", description="Por favor, ejecuta el comando '!menu' (sin las comillas) para poder utilizar el bot.", color=discord.Color(int("08FF10", 16)))
        embed.set_footer(text=f"Solicitado por {ctx_or_interaction.author.name}")
        await ctx_or_interaction.send(embed=embed)


@bot.command(help='Sirve para saltar a un tiempo en especifico en la cancion actual', usage='!goto {minutos:segundos}')
async def goto(ctx, time):

    voice_client = ctx.voice_client
    guild = ctx.guild

    print("DESDE INICIO 1")
    print(current_songs[guild.id])

    author = ctx.author.name
    #file_counters[guild.id] -= 1

    print("DESDE INICIO 2")
    print(current_songs[guild.id])

    if not voice_client or not voice_client.is_playing():
        embed = discord.Embed(title="No se está reproduciendo ninguna canción en este momento.", color=discord.Color(int("F70000", 16)))
        embed.set_footer(text=f"Solicitado por {author}")
        await ctx.send(embed=embed)
        return

    # Parsear el tiempo ingresado por el usuario en formato 'mm:ss'
    minutes, seconds = map(int, time.split(':'))
    target_time = minutes * 60 + seconds

    print("DESDE INICIO 3")
    print(current_songs[guild.id])

    # Obtener la información de la canción actual
    if current_songs[guild.id] is None:
        embed = discord.Embed(title="No se está reproduciendo ninguna canción en este momento.", color=discord.Color(int("F70000", 16)))
        embed.set_footer(text=f"Solicitado por {author}")
        await ctx.send(embed=embed)
        return
    
    # Verificar si el tiempo ingresado es válido
    song_duration = current_songs[guild.id]['duration']
    if target_time < 0 or target_time > song_duration:
        embed = discord.Embed(title="Tiempo no válido. Asegúrate de ingresar un tiempo dentro de la duración de la canción.", color=discord.Color(int("F70000", 16)))
        embed.set_footer(text=f"Solicitado por {author}")
        await ctx.send(embed=embed)
        return

    # Restaurar la pausa si la canción estaba pausada antes de saltar al tiempo especificado
    #if song_paused[guild.id]:
        #voice_client.pause()
        #song_paused[guild.id] = False

    filtroEQ = global_eq_filter
    print(filtroEQ)

    # Generar una nueva fuente de audio desde el tiempo especificado
    audio_file = f'audio/video{file_counters[guild.id]:02d}.opus'  # Asegúrate de usar el mismo formato que en el comando play
    source = discord.FFmpegPCMAudio(audio_file, before_options=f"-ss {target_time}", options=[f'-b:a 320k', f'-af {filtroEQ}']) #MP3

    def after_playing(error):
        # Reproducir la siguiente canción después de la actual
        #file_counters[guild.id] += 1
        asyncio.run_coroutine_threadsafe(reproducir_siguiente(ctx), bot.loop)
        # Eliminar el archivo original después de que se haya reproducido
        #if os.path.exists(audio_file):
            #os.remove(audio_file)

    # Calcular la nueva duración de la canción actual
    new_duration = current_songs[guild.id]['duration'] - target_time

    # Actualizar la información de la canción actual
    #current_songs[guild.id].update({
        #'duration': new_duration
    #})

    # Detener la reproducción actual
    if voice_client and voice_client.is_playing():
        voice_client.pause()
        # Enviar un mensaje de confirmación al usuario
        embed = discord.Embed(title="Canción saltada al tiempo especificado.", color=discord.Color(int("08FF10", 16)))
        embed.add_field(name="Nuevo tiempo", value=f"{minutes}:{seconds:02d}", inline=False)
        embed.set_footer(text=f"Solicitado por {author}")
        await ctx.send(embed=embed)
        # Reproducir la canción desde el tiempo especificado
        voice_client.play(source, after=after_playing)
        #voice_client.stop()
        #ctx.voice_client.stop()

    
    #voice_client.play(source, after=after_playing)

    print("Antes")
    print(current_songs[guild.id])


    print("Despues")
    print(current_songs[guild.id])

    print(f'Generando archivo de audio: {audio_file}')

    print("DESDE FINAL 0")
    print(current_songs[guild.id])

    
    print("DESDE FINAL 1")
    print(current_songs[guild.id])

@bot.command(help='Sirve para eliminar de la lista de espera o cola alguna cancion en especifico', usage='!remove {numero-cola}')
async def remove(ctx, index: int):
    guild = ctx.guild

    if not queues[guild.id]:
        embed = discord.Embed(title="No hay canciones en la cola para remover.", color=discord.Color(int("F70000", 16)))
        embed.set_footer(text=f"Solicitado por {ctx.author.name}")
        await ctx.send(embed=embed)
        return

    if 1 <= index <= len(queues[guild.id]):
        removed_song = queues[guild.id][index - 1]
        queues[guild.id].remove(removed_song)
        embed = discord.Embed(title=f"Canción removida de la cola: {removed_song['title']}", color=discord.Color(int("FFEE00", 16)))
        embed.set_footer(text=f"Solicitado por {ctx.author.name}")
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title=f"Numero fuera de la lista de la cola. Ingresa un numero valido de la cola de musica", color=discord.Color(int("F70000", 16)))
        #embed = discord.Embed(title=f"Índice inválido. Ingresa un número entre 1 y {len(queues[guild.id])}.", color=discord.Color(int("F70000", 16)))
        embed.set_footer(text=f"Solicitado por {ctx.author.name}")
        await ctx.send(embed=embed)

@bot.command(help='Sirve para mostrar la letra de la cancion actual', usage='!lyrics')
async def lyrics(ctx):
    await lyrics_btn(ctx)

async def lyrics_btn(ctx_or_interaction):
    if isinstance(ctx_or_interaction, discord.Interaction):
        guild = ctx_or_interaction.guild
    else:
        ctx = ctx_or_interaction
        guild = ctx.guild

    # Para poder tener un mensaje principal cuando se usan botones y/o se escribe un comando manualmente.
    if isinstance(ctx_or_interaction, discord.Interaction):
        embed = discord.Embed(title="Ejecutando Comando...", color=discord.Color(int("FFEE00", 16)))
        embed.set_footer(text=f"Solicitado por {ctx_or_interaction.user.name}")
        await ctx_or_interaction.response.send_message(embed=embed, delete_after=0) # Mensaje inicial para evitar error de "Interaccion Fallida"
        
        embed = discord.Embed(title="Ejecutando Comando...", color=discord.Color(int("FFEE00", 16)))
        embed.set_footer(text=f"Solicitado por {ctx_or_interaction.user.name}")
        await ctx_or_interaction.message.edit(embed=embed) # Se edita el mensaje que envia el bot cuando se ejecuta "!menu"
    else:
        embed = discord.Embed(title="Ejecutando Comando...", color=discord.Color(int("FFEE00", 16)))
        embed.set_footer(text=f"Solicitado por {ctx_or_interaction.author.name}")
        await ctx_or_interaction.send(embed=embed)

    # Verificar si hay un título de una canción
    if current_songs[guild.id] is None or 'title' not in current_songs[guild.id]:
        if isinstance(ctx_or_interaction, discord.Interaction):
            embed = discord.Embed(title="No se está reproduciendo ninguna canción en este momento.", color=discord.Color(int("F70000", 16)))
            embed.set_footer(text=f"Solicitado por {ctx_or_interaction.user.name}")
            await ctx_or_interaction.message.edit(embed=embed)
        else:
            embed = discord.Embed(title="No se está reproduciendo ninguna canción en este momento.", color=discord.Color(int("F70000", 16)))
            embed.set_footer(text=f"Solicitado por {ctx_or_interaction.author.name}")
            await ctx_or_interaction.send(embed=embed)
        return

    full_title = current_songs[guild.id]['title']
    author, title = map(str.strip, full_title.split('-', 1) if '-' in full_title else (full_title, "Desconocido"))
    #author, title = map(str.strip, full_title.split('-', 1) if '-' in full_title else (full_title, "Desconocido"))

    # Mostrar un mensaje de "cargando" mientras se descarga la letra
    if isinstance(ctx_or_interaction, discord.Interaction):
        embed = discord.Embed(title=f"Letra de la canción: {title} - {author}", description="Obteniendo la letra de la canción actual. Por favor, espere...", color=discord.Color(int("FFEE00", 16)))
        embed.set_footer(text=f"Solicitado por {ctx_or_interaction.user.name}")
        response_msg = await ctx_or_interaction.message.edit(embed=embed)
    else:
        embed = discord.Embed(title=f"Letra de la canción: {title} - {author}", description="Obteniendo la letra de la canción actual. Por favor, espere...", color=discord.Color(int("FFEE00", 16)))
        embed.set_footer(text=f"Solicitado por {ctx_or_interaction.author.name}")
        response_msg = await ctx_or_interaction.edit(embed=embed) if hasattr(ctx_or_interaction, 'edit') else await ctx_or_interaction.send(embed=embed)

    # Llamada a la API para obtener las letras
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://api.lyrics.ovh/v1/{author}/{title}') as response:
            data = await response.json()

            if 'lyrics' in data:
                lyrics = data['lyrics']

                # Eliminar la primera línea
                lyrics_lines = lyrics.split('\n', 1)
                if len(lyrics_lines) > 1:
                    lyrics = lyrics_lines[1]

                # Agregar la imagen del álbum como miniatura (si está disponible)
                url = current_songs[guild.id]['url']
                thumbnail_url = None

                ydl_opts = {'format': 'bestaudio/best'}
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    thumbnail_url = ydl.extract_info(url, download=False).get('thumbnail', None)

                if thumbnail_url:
                    embed = discord.Embed(title=f"Letra de la canción: {title} - {author}", description=lyrics, color=discord.Color(int("08FF10", 16)))
                    embed.set_thumbnail(url=thumbnail_url)
                else:
                    embed = discord.Embed(title=f"Letra de la canción: {title} - {author}", description=lyrics, color=discord.Color(int("08FF10", 16)))

                # Editar el mensaje original para mostrar la letra de la canción
                try:
                    await response_msg.edit(embed=embed)
                except discord.errors.InteractionResponded:
                    pass  # No hacer nada si la interacción ya ha sido respondida anteriormente
            else:
                if isinstance(ctx_or_interaction, discord.Interaction):
                    embed = discord.Embed(title=f"No se encontró la letra para la canción: {title} - {author}.", color=discord.Color(int("F70000", 16)))
                    embed.set_footer(text=f"Solicitado por {ctx_or_interaction.user.name}")
                    await response_msg.edit(embed=embed)
                else:
                    embed = discord.Embed(title=f"No se encontró la letra para la canción: {title} - {author}.", color=discord.Color(int("F70000", 16)))
                    embed.set_footer(text=f"Solicitado por {ctx_or_interaction.author.name}")
                    await response_msg.edit(embed=embed)

@bot.command(help='Sirve para mover una cancion en especifico al principio de la lista de espera o cola', usage='!playsong {numero-cola}')
async def playsong(ctx, index: int):
    guild = ctx.guild

    if not queues[guild.id]:
        embed = discord.Embed(title="No hay canciones en la cola para reproducir.", color=discord.Color(int("F70000", 16)))
        embed.set_footer(text=f"Solicitado por {ctx.author.name}")
        await ctx.send(embed=embed)
        return

    if 1 <= index <= len(queues[guild.id]):
        # Guardar la cola actual antes de reproducir la canción específica
        cola_original = queues[guild.id].copy()
        print(f"Cola original: {queues[guild.id]}")
        print(f"Cola copiada: {cola_original}")

        # Eliminar la canción específica de la cola original y almacenada en otra variable
        song_to_move = cola_original[index - 1]
        queues[guild.id].remove(song_to_move)
        print(f"Cancion extraida de la cola copiada (la que el usuario quiere): {song_to_move}")

        # Mover la canción al principio de la cola
        listaCompleta = deque([song_to_move])
        listaCompleta.extend(queues[guild.id])
        queues[guild.id] = listaCompleta
        print(f"Cola final con la cancion extraida y colocada al principio + restante de la cola: {queues[guild.id]}")
        
        embed = discord.Embed(title=f"Cancion agregada al principio de la cola", color=discord.Color(int("F70000", 16)))
        embed.add_field(name="Nombre", value=song_to_move['title'], inline=False)
        embed.set_footer(text=f"Solicitado por {ctx.author.name}")
        await ctx.send(embed=embed)

        # Reproducir la canción específica
        #await reproducir_siguiente(ctx)
        
    else:
        embed = discord.Embed(title=f"Número fuera de la lista de la cola. Ingresa un número válido de la cola de música.", color=discord.Color(int("F70000", 16)))
        embed.set_footer(text=f"Solicitado por {ctx.author.name}")
        await ctx.send(embed=embed)

@bot.command(help='Sirve para repetir la cancion actual', usage='!repeat {numero-repeticiones}')
async def repeat(ctx, times: int = None):
    await repeat_btn(ctx, times)

async def repeat_btn(ctx_or_interaction, times):
    # Extrae la información necesaria del contexto del comando o la interacción
    if isinstance(ctx_or_interaction, discord.Interaction):
        guild = ctx_or_interaction.guild
        author_name = ctx_or_interaction.user.name
        voice_client = guild.voice_client
    else:
        ctx = ctx_or_interaction
        guild = ctx.guild
        author_name = ctx.author.name
        voice_client = ctx.voice_client

    # Para poder tener un mensaje principal cuando se usan botones y/o se escribe un comando manualmente.
    if isinstance(ctx_or_interaction, discord.Interaction):
        embed = discord.Embed(title="Ejecutando Comando...", color=discord.Color(int("FFEE00", 16)))
        embed.set_footer(text=f"Solicitado por {ctx_or_interaction.user.name}")
        await ctx_or_interaction.response.send_message(embed=embed, delete_after=0) # Mensaje inicial para evitar error de "Interaccion Fallida"
        
        embed = discord.Embed(title="Ejecutando Comando...", color=discord.Color(int("FFEE00", 16)))
        embed.set_footer(text=f"Solicitado por {ctx_or_interaction.user.name}")
        await ctx_or_interaction.message.edit(embed=embed) # Se edita el mensaje que envia el bot cuando se ejecuta "!menu"
    else:
        embed = discord.Embed(title="Ejecutando Comando...", color=discord.Color(int("FFEE00", 16)))
        embed.set_footer(text=f"Solicitado por {ctx_or_interaction.author.name}")
        await ctx_or_interaction.send(embed=embed)

    if times is None:
        if isinstance(ctx_or_interaction, discord.Interaction):
            embed = discord.Embed(title="Por favor, ingresa cuantas veces quieres repetir la canción actual.", color=discord.Color(int("FFEE00", 16)))
            embed.set_footer(text=f"Solicitado por {ctx_or_interaction.user.name}")
            await ctx_or_interaction.message.edit(embed=embed)
        else:
            embed = discord.Embed(title="Por favor, ingresa cuantas veces quieres repetir la canción actual.", color=discord.Color(int("FFEE00", 16)))
            embed.set_footer(text=f"Solicitado por {ctx_or_interaction.author.name}")
            await ctx_or_interaction.send(embed=embed)
        
        # Espera la respuesta del usuario en el mismo canal
        try:
            if isinstance(ctx_or_interaction, discord.Interaction):
                response = await bot.wait_for("message", check=lambda message: message.channel == ctx_or_interaction.channel and message.author == ctx_or_interaction.user, timeout=10)
            else:
                response = await bot.wait_for("message", check=lambda message: message.channel == ctx.channel and message.author == ctx.author, timeout=10) # tambien puede ser None
            times = int(response.content.strip())
        except ValueError:
            if isinstance(ctx_or_interaction, discord.Interaction):
                embed = discord.Embed(title="ERROR, valor ingresado no correcto. Por favor, ingresa un número de repeticiones válido.", color=discord.Color(int("F70000", 16)))
                embed.set_footer(text=f"Solicitado por {ctx_or_interaction.user.name}")
                await ctx_or_interaction.message.edit(embed=embed)
            else:
                embed.set_footer(text=f"Solicitado por {ctx_or_interaction.author.name}")
                await ctx_or_interaction.send(embed=embed)
            return
        except asyncio.TimeoutError:
            if isinstance(ctx_or_interaction, discord.Interaction):
                embed = discord.Embed(title="Se agoto el tiempo para ingresar un numero de repeticiones a la cancion actual. Por favor, vuelva a apretar el boton 'Repetir Cancion' y envie un número de repeticiones válido para repetir la cancion actual.", color=discord.Color(int("F70000", 16)))
                embed.set_footer(text=f"Solicitado por {ctx_or_interaction.user.name}")
                await ctx_or_interaction.message.edit(embed=embed)
            else:
                embed = discord.Embed(title="Se agoto el tiempo para ingresar un numero de repeticiones a la cancion actual. Por favor, vuelva a apretar el boton 'Repetir Cancion' y envie un número de repeticiones válido para repetir la cancion actual.", color=discord.Color(int("F70000", 16)))
                embed.set_footer(text=f"Solicitado por {ctx_or_interaction.author.name}")
                await ctx_or_interaction.send(embed=embed)
            return

    # Verificar si hay un título de una canción
    if current_songs[guild.id] is None or 'title' not in current_songs[guild.id]:
        if isinstance(ctx_or_interaction, discord.Interaction):
            embed = discord.Embed(title="No se está reproduciendo ninguna canción en este momento.", color=discord.Color(int("F70000", 16)))
            embed.set_footer(text=f"Solicitado por {ctx_or_interaction.user.name}")
            await ctx_or_interaction.message.edit(embed=embed)
        else:
            embed = discord.Embed(title="No se está reproduciendo ninguna canción en este momento.", color=discord.Color(int("F70000", 16)))
            embed.set_footer(text=f"Solicitado por {ctx_or_interaction.author.name}")
            await ctx_or_interaction.send(embed=embed)
        return

    if current_songs[guild.id] is None:
        embed = discord.Embed(title="No se está reproduciendo ninguna canción en este momento.", color=discord.Color(int("F70000", 16)))
        embed.set_footer(text=f"Solicitado por {author_name}")
        if isinstance(ctx_or_interaction, discord.Interaction):
            await ctx_or_interaction.message.edit(embed=embed)
        else:
            await ctx_or_interaction.send(embed=embed)
        return

    # Guardar la canción actual y la cola actual
    current_song = current_songs[guild.id]
    current_queue = queues[guild.id].copy()

    # Repetir la canción según el número de veces especificado
    repeated_queue = [current_song] * times + list(current_queue)
    queues[guild.id] = deque(repeated_queue)

    embed = discord.Embed(title=f"Canción repetida {times} veces y agregada al principio de la cola.", color=discord.Color(int("08FF10", 16)))
    embed.add_field(name="Nombre", value=current_song['title'], inline=False)
    embed.set_footer(text=f"Solicitado por {author_name}")
    if isinstance(ctx_or_interaction, discord.Interaction):
        await ctx_or_interaction.message.edit(embed=embed)
    else:
        await ctx_or_interaction.send(embed=embed)

    # Si no hay ninguna canción reproduciéndose, iniciar la reproducción
    if voice_client and not voice_client.is_playing():
        await reproducir_siguiente(ctx)

autoplay_enabled = False

# Lista de reproducción predeterminada (solo como ejemplo, debes reemplazar con tus propias URLs)
default_playlist = [
    "https://www.youtube.com/watch?v=y5BJHYrbg1U",  # Ejemplo de URL de YouTube
    "https://www.youtube.com/watch?v=eJO5HU_7_1w"  # Otra URL de ejemplo
]

# Lista de géneros musicales
#genres = ['rock', 'pop', 'electronica']
#genres = ['Palaye Royale', 'Twenty One Pilots', 'Arctic Monkeys', 'Eminem']

# Función para obtener una URL aleatoria de YouTube relacionada con un género musical específico
def get_random_song_url(genre):
    query = f"{genre} music"
    search_results = list(search(query, num=10, stop=10, pause=2))
    
    # Filtra los resultados para obtener solo URLs de YouTube
    youtube_results = [url for url in search_results if 'youtube.com/watch?v=' in url]
    
    # Elige una URL aleatoria de la lista
    random_song_url = random.choice(youtube_results)
    
    return random_song_url

# Función para agregar URLs aleatorias de canciones de géneros específicos a la lista default_playlist
async def add_random_songs_to_default_playlist():
    global default_playlist
    
    for genre in genres:
        random_song_url = get_random_song_url(genre)
        default_playlist.append(random_song_url)

# Función asincrónica para agregar canciones predeterminadas a la cola
async def add_default_songs_to_queue(ctx):
    
    for song_url in default_playlist:
        await play(ctx, song_url)

        # Esperar 3 minutos antes de agregar más canciones
        # await asyncio.sleep(15)  # 15 segundos

# Comando para activar el autoplay
@bot.command(help='Activa la reproducción continua de canciones 24/7 **(COMANDO EN COSNTRUCCION - NO USAR)**', usage='!autoplay on')
async def autoplay_on(ctx):
    global autoplay_enabled

    if not autoplay_enabled:
        autoplay_enabled = True
        await ctx.send('Autoplay activado. El bot empezará a reproducir canciones continuamente.')
        # Llamada a la función para agregar canciones aleatorias a la lista default_playlist
        # await add_random_songs_to_default_playlist()
        await add_default_songs_to_queue(ctx)  # Agregar canciones automáticamente a la cola al activar el autoplay
        #await autoplay(ctx)
    else:
        await ctx.send('El autoplay ya está activado.')

# Comando para desactivar el autoplay
@bot.command(help='Desactiva la reproducción continua de canciones **(COMANDO EN COSNTRUCCION - NO USAR)**', usage='!autoplay off')
async def autoplay_off(ctx):
    global autoplay_enabled

    if autoplay_enabled:
        autoplay_enabled = False
        await ctx.send('Autoplay desactivado. El bot dejará de reproducir canciones continuamente.')
    else:
        await ctx.send('El autoplay ya está desactivado.')

# Función para activar la reproducción automática de canciones
# async def autoplay(ctx):
#     global default_playlist

#     # Agregar canciones aleatorias a la lista default_playlist
#     add_random_songs_to_default_playlist()

#     # Verificar si el bot no está reproduciendo ninguna canción y el default_playlist no está vacío
#     if not ctx.voice_client.is_playing() and default_playlist:
#         song_url = default_playlist.pop(0)  # Obtener la primera canción de la lista
#         await play_song(ctx, song_url)  # Reproducir la canción

TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)