import asyncio
import os
import discord
from discord.ext import commands
from mcstatus import BedrockServer
from flask import Flask
from threading import Thread

# Env vars
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))
SERVER_IP = os.getenv("MINECRAFT_SERVER_IP")
SERVER_PORT = int(os.getenv("MINECRAFT_SERVER_PORT", "19132"))
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "60"))
WEB_PORT = int(os.getenv("PORT", "10000"))  # Render uses $PORT

# Flask dummy web server
app = Flask(__name__)
@app.route("/")
def home():
    return "Bot is running!"

def run_web():
    app.run(host="0.0.0.0", port=WEB_PORT)

# Discord bot setup
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
last_status = None

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    bot.loop.create_task(check_server_status())

async def check_server_status():
    global last_status
    await bot.wait_until_ready()
    channel = bot.get_channel(CHANNEL_ID)
    server = BedrockServer(SERVER_IP, SERVER_PORT)

    while not bot.is_closed():
        try:
            status = await server.async_status()
            print(f"🟢 Bedrock Server is ONLINE with {status.players_online} players.")
            if last_status is not True:
                await channel.send(f"🟢 Bedrock server is ONLINE with {status.players_online} players.")
                last_status = True
        except Exception as e:
            print(f"🔴 Server check failed: {e}")
            if last_status is not False:
                await channel.send("🔴 Bedrock server is OFFLINE.")
                last_status = False

        await asyncio.sleep(CHECK_INTERVAL)

def start_bot():
    bot.run(TOKEN)

# Run both Flask + bot
if __name__ == "__main__":
    Thread(target=run_web).start()
    start_bot()
