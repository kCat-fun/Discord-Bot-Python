import discord
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv('TOKEN')
CHANNEL1_ID = int(os.getenv('CHANNEL1'))
CHANNEL2_ID = int(os.getenv('CHANNEL2'))

intents = discord.Intents.all()
client = discord.Client(intents=intents)

# Bot起動時に呼び出される関数
@client.event
async def on_ready():
    print("Ready!")
    channel1 = client.get_channel(CHANNEL1_ID)
    channel2 = client.get_channel(CHANNEL2_ID)
    await channel1.send("Run discord bot!")
    await channel2.send("Run discord bot!")

# メッセージの検知
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.channel.id == CHANNEL1_ID:
        channel2 = client.get_channel(CHANNEL2_ID)
        await channel2.send(message.content)

    if message.channel.id == CHANNEL2_ID:
        channel1 = client.get_channel(CHANNEL1_ID)
        await channel1.send(message.content)

# Bot起動
client.run(TOKEN)
