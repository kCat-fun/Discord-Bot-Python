# Discord-Bot-Python
Disocrdで2サーバー間でメッセージのやり取りをするBotです。<br/><br/>
**使用例**<br /><br />
![image](https://github.com/user-attachments/assets/c7fd6299-e422-43ca-a092-fa35d4eee83b)<br />
![image](https://github.com/user-attachments/assets/c3be22bb-638a-4cf0-8d5d-bc2ad5956cfa)

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
