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
CHANNEL1=
CHANNEL2=
```
4. discord-bot.pyを実行する
```bash
python3 discord-bot.py
```
※ ライブラリがインストールされてない場合は以下を実行
```bash
pip install discord.py
pip install python-dotenv
```
