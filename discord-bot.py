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
    # await channel1.send("Run discord bot!")
    # await channel2.send("Run discord bot!")

# メッセージの検知
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    msg: str = ""
    filepaths: list[str] = []

    # 添付ファイルをチェック
    for attachment in message.attachments:
        # 画像形式をチェック
        if any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']):
            # タイムスタンプ付きのファイル名を生成
            filename = f"image_{attachment.id}.png"
            filepaths.append(f"./images/{filename}")
            
            # 画像を保存
            await attachment.save(filepaths[-1])
            print(f'保存完了: {filepaths[-1]}')

    if message.channel.id == CHANNEL1_ID:
        channel2 = client.get_channel(CHANNEL2_ID)
        for s in message.content.splitlines():
            msg += f"> {s}\n"
        await channel2.send(f'[Bot Test1]\t__{ message.author }__ >>\n{ msg }')
        if filepaths:
            for filepath in filepaths:
                await channel2.send(file=discord.File(filepath))
                # 送信後に画像削除
                os.remove(filepath)
                print(f'削除完了: {filepath}')

    if message.channel.id == CHANNEL2_ID:
        channel1 = client.get_channel(CHANNEL1_ID)
        for s in message.content.splitlines():
            msg += f"> {s}\n"
        await channel1.send(f'[Bot Test2]\t__{ message.author }__ >>\n{ msg }')
        if filepaths:
            for filepath in filepaths:
                await channel1.send(file=discord.File(filepath))
                # 送信後に画像削除
                os.remove(filepath)
                print(f'削除完了: {filepath}')

# Bot起動
client.run(TOKEN)
