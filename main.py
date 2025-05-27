import asyncio
import os
import discord
from discord.ext import commands
from mcstatus import JavaServer

# Load environment variables
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))
SERVER_IP = os.getenv("MINECRAFT_SERVER_IP")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "60"))  # default to 60s

# Setup Discord bot
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Track server status to avoid duplicate messages
last_status = None

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    bot.loop.create_task(check_server_status())

async def check_server_status():
    global last_status
    await bot.wait_until_ready()
    channel = bot.get_channel(CHANNEL_ID)
    server = JavaServer.lookup(SERVER_IP)

    while not bot.is_closed():
        try:
            status = await server.async_status()
            print(f"🟢 Server is ONLINE with {status.players.online} players.")
            if last_status is not True:
                await channel.send(f"🟢 Server is ONLINE with {status.players.online} players.")
                last_status = True
        except Exception as e:
            print(f"🔴 Server check failed: {e}")
            if last_status is not False:
                await channel.send("🔴 Server is OFFLINE.")
                last_status = False

        await asyncio.sleep(CHECK_INTERVAL)

bot.run(TOKEN)
