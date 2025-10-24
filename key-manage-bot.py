import discord
from discord.ui import Button, View, Modal, TextInput
from discord import ButtonStyle
from dotenv import load_dotenv
import os
from datetime import datetime, time
import asyncio

load_dotenv()

TOKEN = os.getenv('TOKEN')
HARDWARE_BUTTON_CHANNEL = int(os.getenv('HARDWARE_BUTTON_CHANNEL'))
HARDWARE_LOG_CHANNEL = int(os.getenv('HARDWARE_LOG_CHANNEL'))
FACTORY_BUTTON_CHANNEL = int(os.getenv('FACTORY_BUTTON_CHANNEL'))
FACTORY_LOG_CHANNEL = int(os.getenv('FACTORY_LOG_CHANNEL'))

intents = discord.Intents.all()
client = discord.Client(intents=intents)

# カギの状態を管理（共通のサークル室なので1つ）
key_status = {
    "holder": None,  # カギを持っている人
    "location": "事務局",  # カギの場所（内部管理用）
    "is_locked": True  # 施錠状態
}

# 移動先入力用のモーダル
class LocationModal(Modal, title="移動先を入力"):
    location_input = TextInput(
        label="移動先",
        placeholder="例: 工房、食堂、etc...",
        required=True,
        max_length=50
    )
    
    def __init__(self, user, key_type):
        super().__init__()
        self.user = user
        self.key_type = key_type
    
    async def on_submit(self, interaction: discord.Interaction):
        location = self.location_input.value
        key_status["location"] = location
        
        # 両方のログチャンネルに通知
        hardware_log = client.get_channel(HARDWARE_LOG_CHANNEL)
        factory_log = client.get_channel(FACTORY_LOG_CHANNEL)
        
        embed = discord.Embed(
            title="🚶 カギ移動",
            description=f"**{self.user.mention}** がカギを移動しました",
            color=discord.Color.purple(),
            timestamp=datetime.now()
        )
        embed.add_field(name="移動先", value=location, inline=False)
        embed.add_field(name="現在の所持者", value=key_status["holder"] or "なし", inline=True)
        embed.add_field(name="施錠状態", value="🔒 施錠中" if key_status["is_locked"] else "🔓 開錠中", inline=True)
        
        await hardware_log.send(embed=embed)
        await factory_log.send(embed=embed)
        
        # 両方のボタンチャンネルにボタンを再送信
        hardware_button = client.get_channel(HARDWARE_BUTTON_CHANNEL)
        factory_button = client.get_channel(FACTORY_BUTTON_CHANNEL)
        await send_management_panel(hardware_button, "hardware")
        await send_management_panel(factory_button, "factory")
        
        await interaction.response.send_message(f"カギの場所を **{location}** に更新しました", ephemeral=True)

# 備考入力用のモーダル
class NoteModal(Modal, title="備考を入力"):
    note_input = TextInput(
        label="備考",
        placeholder="例: 30分後に戻ります、17時に閉めて帰ります、etc...",
        required=True,
        style=discord.TextStyle.paragraph,
        max_length=500
    )
    
    def __init__(self, user, key_type):
        super().__init__()
        self.user = user
        self.key_type = key_type
    
    async def on_submit(self, interaction: discord.Interaction):
        note = self.note_input.value
        
        # 両方のログチャンネルに通知
        hardware_log = client.get_channel(HARDWARE_LOG_CHANNEL)
        factory_log = client.get_channel(FACTORY_LOG_CHANNEL)
        
        embed = discord.Embed(
            title="📝 備考",
            description=f"**{self.user.mention}** からの備考",
            color=discord.Color.orange(),
            timestamp=datetime.now()
        )
        embed.add_field(name="メッセージ", value=note, inline=False)
        embed.add_field(name="現在の所持者", value=key_status["holder"] or "なし", inline=True)
        embed.add_field(name="施錠状態", value="🔒 施錠中" if key_status["is_locked"] else "🔓 開錠中", inline=True)
        
        await hardware_log.send(embed=embed)
        await factory_log.send(embed=embed)
        
        # 両方のボタンチャンネルにボタンを再送信
        hardware_button = client.get_channel(HARDWARE_BUTTON_CHANNEL)
        factory_button = client.get_channel(FACTORY_BUTTON_CHANNEL)
        await send_management_panel(hardware_button, "hardware")
        await send_management_panel(factory_button, "factory")
        
        await interaction.response.send_message("✅ 備考を送信しました", ephemeral=True)

# カギ管理用のViewクラス
class KeyManagementView(View):
    def __init__(self, key_type):
        super().__init__(timeout=None)
        self.key_type = key_type
    
    @discord.ui.button(label="📥 借りる", style=ButtonStyle.primary, custom_id="borrow_key")
    async def borrow_button(self, interaction: discord.Interaction, button: Button):
        if key_status["holder"]:
            await interaction.response.send_message(
                f"❌ カギは既に **{key_status['holder']}** が借りています",
                ephemeral=True
            )
            return
        
        key_status["holder"] = interaction.user.mention
        
        # 両方のログチャンネルに通知
        hardware_log = client.get_channel(HARDWARE_LOG_CHANNEL)
        factory_log = client.get_channel(FACTORY_LOG_CHANNEL)
        
        embed = discord.Embed(
            title="📥 カギ貸出",
            description=f"**{interaction.user.mention}** がカギを借りました",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        embed.add_field(name="施錠状態", value="🔒 施錠中" if key_status["is_locked"] else "🔓 開錠中", inline=True)
        
        await hardware_log.send(embed=embed)
        await factory_log.send(embed=embed)
        
        # 両方のボタンチャンネルにボタンを再送信
        hardware_button = client.get_channel(HARDWARE_BUTTON_CHANNEL)
        factory_button = client.get_channel(FACTORY_BUTTON_CHANNEL)
        await send_management_panel(hardware_button, "hardware")
        await send_management_panel(factory_button, "factory")
        
        await interaction.response.send_message("✅ カギを借りました", ephemeral=True)
    
    @discord.ui.button(label="📤 返却", style=ButtonStyle.primary, custom_id="return_key")
    async def return_button(self, interaction: discord.Interaction, button: Button):
        if not key_status["holder"]:
            await interaction.response.send_message("❌ カギは誰も借りていません", ephemeral=True)
            return
        
        previous_holder = key_status["holder"]
        key_status["holder"] = None
        key_status["location"] = "事務局"
        
        # 両方のログチャンネルに通知
        hardware_log = client.get_channel(HARDWARE_LOG_CHANNEL)
        factory_log = client.get_channel(FACTORY_LOG_CHANNEL)
        
        embed = discord.Embed(
            title="📤 カギ返却",
            description=f"**{interaction.user.mention}** がカギを返却しました",
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        embed.add_field(name="前の所持者", value=previous_holder, inline=True)
        
        await hardware_log.send(embed=embed)
        await factory_log.send(embed=embed)
        
        # 両方のボタンチャンネルにボタンを再送信
        hardware_button = client.get_channel(HARDWARE_BUTTON_CHANNEL)
        factory_button = client.get_channel(FACTORY_BUTTON_CHANNEL)
        await send_management_panel(hardware_button, "hardware")
        await send_management_panel(factory_button, "factory")
        
        await interaction.response.send_message("✅ カギを返却しました", ephemeral=True)
    
    @discord.ui.button(label="🔓 開錠", style=ButtonStyle.success, custom_id="unlock_key")
    async def unlock_button(self, interaction: discord.Interaction, button: Button):
        if not key_status["is_locked"]:
            await interaction.response.send_message("❌ 既に開錠されています", ephemeral=True)
            return
        
        key_status["is_locked"] = False
        key_status["holder"] = interaction.user.mention
        
        # 両方のログチャンネルに通知
        hardware_log = client.get_channel(HARDWARE_LOG_CHANNEL)
        factory_log = client.get_channel(FACTORY_LOG_CHANNEL)
        
        embed = discord.Embed(
            title="🔓 開錠",
            description=f"**{interaction.user.mention}** が開錠しました",
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        embed.add_field(name="現在の所持者", value=key_status["holder"] or "なし", inline=True)
        
        await hardware_log.send(embed=embed)
        await factory_log.send(embed=embed)
        
        # 両方のボタンチャンネルにボタンを再送信
        hardware_button = client.get_channel(HARDWARE_BUTTON_CHANNEL)
        factory_button = client.get_channel(FACTORY_BUTTON_CHANNEL)
        await send_management_panel(hardware_button, "hardware")
        await send_management_panel(factory_button, "factory")
        
        await interaction.response.send_message("✅ 開錠しました", ephemeral=True)
    
    @discord.ui.button(label="🔒 施錠", style=ButtonStyle.danger, custom_id="lock_key")
    async def lock_button(self, interaction: discord.Interaction, button: Button):
        if key_status["is_locked"]:
            await interaction.response.send_message("❌ 既に施錠されています", ephemeral=True)
            return
        
        key_status["is_locked"] = True
        
        # 両方のログチャンネルに通知
        hardware_log = client.get_channel(HARDWARE_LOG_CHANNEL)
        factory_log = client.get_channel(FACTORY_LOG_CHANNEL)
        
        embed = discord.Embed(
            title="🔒 施錠",
            description=f"**{interaction.user.mention}** が施錠しました",
            color=discord.Color.red(),
            timestamp=datetime.now()
        )
        embed.add_field(name="現在の所持者", value=key_status["holder"] or "なし", inline=True)
        
        await hardware_log.send(embed=embed)
        await factory_log.send(embed=embed)
        
        # 両方のボタンチャンネルにボタンを再送信
        hardware_button = client.get_channel(HARDWARE_BUTTON_CHANNEL)
        factory_button = client.get_channel(FACTORY_BUTTON_CHANNEL)
        await send_management_panel(hardware_button, "hardware")
        await send_management_panel(factory_button, "factory")
        
        await interaction.response.send_message("✅ 施錠しました", ephemeral=True)
    
    @discord.ui.button(label="🚶 移動", style=ButtonStyle.secondary, custom_id="move_key", row=1)
    async def move_button(self, interaction: discord.Interaction, button: Button):
        if not key_status["holder"]:
            await interaction.response.send_message("❌ カギが借りられていません", ephemeral=True)
            return
        
        modal = LocationModal(interaction.user, self.key_type)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="🔄 所持者変更", style=ButtonStyle.secondary, custom_id="change_holder", row=1)
    async def change_holder_button(self, interaction: discord.Interaction, button: Button):
        if not key_status["holder"]:
            await interaction.response.send_message("❌ カギが借りられていません", ephemeral=True)
            return
        
        previous_holder = key_status["holder"]
        key_status["holder"] = interaction.user.mention
        
        # 両方のログチャンネルに通知
        hardware_log = client.get_channel(HARDWARE_LOG_CHANNEL)
        factory_log = client.get_channel(FACTORY_LOG_CHANNEL)
        
        embed = discord.Embed(
            title="🔄 所持者変更",
            description=f"**{interaction.user.mention}** がカギの所持者を変更しました",
            color=discord.Color.teal(),
            timestamp=datetime.now()
        )
        embed.add_field(name="前の所持者", value=previous_holder or "なし", inline=True)
        embed.add_field(name="新しい所持者", value=interaction.user.mention, inline=True)
        embed.add_field(name="施錠状態", value="🔒 施錠中" if key_status["is_locked"] else "🔓 開錠中", inline=True)
        
        await hardware_log.send(embed=embed)
        await factory_log.send(embed=embed)
        
        # 両方のボタンチャンネルにボタンを再送信
        hardware_button = client.get_channel(HARDWARE_BUTTON_CHANNEL)
        factory_button = client.get_channel(FACTORY_BUTTON_CHANNEL)
        await send_management_panel(hardware_button, "hardware")
        await send_management_panel(factory_button, "factory")
        
        await interaction.response.send_message("✅ 所持者をあなたに変更しました", ephemeral=True)
    
    @discord.ui.button(label="📝 備考", style=ButtonStyle.secondary, custom_id="note_button", row=1)
    async def note_button(self, interaction: discord.Interaction, button: Button):
        modal = NoteModal(interaction.user, self.key_type)
        await interaction.response.send_modal(modal)

# 管理パネルを送信する関数
async def send_management_panel(channel, key_type):
    embed = discord.Embed(
        title="🔑 サークル室カギ管理システム",
        description="以下のボタンでカギの状態を管理してください",
        color=discord.Color.gold()
    )
    embed.add_field(name="📥 借りる", value="カギを借ります", inline=False)
    embed.add_field(name="📤 返却", value="カギを返却します", inline=False)
    embed.add_field(name="🔓 開錠", value="サークル室を開錠します", inline=False)
    embed.add_field(name="🔒 施錠", value="サークル室を施錠します", inline=False)
    embed.add_field(name="🚶 移動", value="カギの場所を更新します", inline=False)
    embed.add_field(name="🔄 所持者変更", value="カギの所持者を変更します", inline=False)
    embed.add_field(name="📝 備考", value="自由にメッセージを送信します", inline=False)
    
    # 現在の状態を表示
    status_text = f"**現在の状態**\n"
    status_text += f"所持者: {key_status['holder'] or 'なし'}\n"
    status_text += f"施錠状態: {'🔒 施錠中' if key_status['is_locked'] else '🔓 開錠中'}"
    embed.add_field(name="ℹ️ 状態", value=status_text, inline=False)
    
    view = KeyManagementView(key_type)
    await channel.send(embed=embed, view=view)

# Bot起動時に呼び出される関数
@client.event
async def on_ready():
    print("Ready!")
    
    hardware_button = client.get_channel(HARDWARE_BUTTON_CHANNEL)
    factory_button = client.get_channel(FACTORY_BUTTON_CHANNEL)
    
    # 両方のチャンネルに管理パネルを送信
    await send_management_panel(hardware_button, "hardware")
    await send_management_panel(factory_button, "factory")
    
    # 22時のリマインダータスクを開始
    client.loop.create_task(daily_reminder())
    # 24時の自動返却タスクを開始
    client.loop.create_task(auto_return())

# 毎日22時にリマインダーを送信
async def daily_reminder():
    await client.wait_until_ready()
    hardware_button = client.get_channel(HARDWARE_BUTTON_CHANNEL)
    factory_button = client.get_channel(FACTORY_BUTTON_CHANNEL)
    hardware_log = client.get_channel(HARDWARE_LOG_CHANNEL)
    factory_log = client.get_channel(FACTORY_LOG_CHANNEL)
    
    while not client.is_closed():
        now = datetime.now()
        target_time = datetime.combine(now.date(), time(22, 0))
        
        # 既に22時を過ぎていたら翌日の22時に設定
        if now >= target_time:
            target_time = datetime.combine(now.date(), time(22, 0))
            target_time = target_time.replace(day=target_time.day + 1)
        
        # 22時までの秒数を計算
        seconds_until_target = (target_time - now).total_seconds()
        
        # 22時まで待機
        await asyncio.sleep(seconds_until_target)
        
        # カギを借りている人がいる場合のみメッセージを送信
        if key_status["holder"]:
            # 両方のボタンチャンネルにメンション付きメッセージ
            message = (
                f"⏰ {key_status['holder']} さん\n"
                f"**22時になりました！カギを今すぐ返却してください。**"
            )
            await hardware_button.send(message)
            await factory_button.send(message)
            
            # 両方のログチャンネルにも通知
            embed = discord.Embed(
                title="⏰ 返却リマインダー",
                description=f"22時になりました。{key_status['holder']} にリマインダーを送信しました",
                color=discord.Color.orange(),
                timestamp=datetime.now()
            )
            embed.add_field(name="現在の所持者", value=key_status["holder"], inline=True)
            
            await hardware_log.send(embed=embed)
            await factory_log.send(embed=embed)
        
        # 次のチェックまで少し待機（1分後）
        await asyncio.sleep(60)

# 毎日24時に自動返却
async def auto_return():
    await client.wait_until_ready()
    hardware_button = client.get_channel(HARDWARE_BUTTON_CHANNEL)
    factory_button = client.get_channel(FACTORY_BUTTON_CHANNEL)
    hardware_log = client.get_channel(HARDWARE_LOG_CHANNEL)
    factory_log = client.get_channel(FACTORY_LOG_CHANNEL)
    
    while not client.is_closed():
        now = datetime.now()
        target_time = datetime.combine(now.date(), time(0, 0))
        
        # 既に0時を過ぎていたら翌日の0時に設定
        if now >= target_time:
            target_time = datetime.combine(now.date(), time(0, 0))
            target_time = target_time.replace(day=target_time.day + 1)
        
        # 0時までの秒数を計算
        seconds_until_target = (target_time - now).total_seconds()
        
        # 0時まで待機
        await asyncio.sleep(seconds_until_target)
        
        # カギを借りている人がいる場合のみ自動返却
        if key_status["holder"]:
            previous_holder = key_status["holder"]
            key_status["holder"] = None
            key_status["location"] = "事務局"
            
            # 両方のボタンチャンネルに通知
            message = (
                f"🔄 **24時になったため、自動的にカギを返却しました**\n"
                f"前の所持者: {previous_holder}"
            )
            await hardware_button.send(message)
            await factory_button.send(message)
            
            # 両方のログチャンネルにも通知
            embed = discord.Embed(
                title="🔄 自動返却",
                description="24時になったため、カギを自動的に返却しました",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            embed.add_field(name="前の所持者", value=previous_holder, inline=True)
            
            await hardware_log.send(embed=embed)
            await factory_log.send(embed=embed)
            
            # 両方のボタンチャンネルにボタンを再送信
            await send_management_panel(hardware_button, "hardware")
            await send_management_panel(factory_button, "factory")
        
        # 次のチェックまで少し待機（1分後）
        await asyncio.sleep(60)

# Bot起動
client.run(TOKEN)