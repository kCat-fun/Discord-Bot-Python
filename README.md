# Discord-Bot-Python
Disocrdで2サーバー間でメッセージのやり取りをするBot

## 使い方
1. このレポジトリをcloneする
```bash
git clone git@github.com:kCat-fun/Discord-Bot-Python.git
cd Discord-Bot-Python
```  
2. .envファイルを作成する
```bash
touch .env
```  
3. DiscordのAPIキーとルームIDを設定する
```bash
nano .env
```
```env:.env
TOKEN=
# discord-bot.pyで必要
CHANNEL1=
CHANNEL2=
# key-manage-bot.pyで必要
HARDWARE_BUTTON_CHANNEL=
HARDWARE_LOG_CHANNEL=
FACTORY_BUTTON_CHANNEL=
FACTORY_LOG_CHANNEL=
```
4. discord-bot.pyを実行する
```bash
# メッセージ送受信Bot
python3 discord-bot.py
# 鍵管理Bot
python3 key-manage-bot.py
```
※ ライブラリがインストールされてない場合は以下を実行
```bash
pip install discord.py
pip install python-dotenv
```
