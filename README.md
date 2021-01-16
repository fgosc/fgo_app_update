# fgo_app_update
アプリストアからFGOアプリの更新をチェックしてDiscordのwebhookにpostする

ここでは bot を提供するだけなのでbotを実行するサーバーは自分で用意する必要があります

# 実行環境
Pythonが動作する環境

Windows と Linux で動作を確認しています

# インストール
まずは Python をインストールしてください
## 必要なライブラリのインストール
```
$ pip install -r requirements.txt
```
## 設定ファイルのコピー
```
$ copy fgoappupdate-dst.ini fgoappupdate.ini  
```
## 設定ファイル fgoappupdate.ini の編集
```webhook= ```のあとにウェブフックURLを入力してください
画面の「ウェブフックURLをコピー」を押すと取得できます

![image](https://user-images.githubusercontent.com/62515228/104086843-72d7fc80-529e-11eb-85ed-cff1d8241c6a.png)

例:
```
webhook= https://discordapp.com/api/webhooks/00000000000000/abcdefghijklmn--ABCDEFGHIJKLMN
```
## 実行権の付与(UNIXの場合)
```
$ chmod +x fgoappupdate.py
```

# 使用法
下記のコマンド実行でアップデートの有無をチェックします
```
$ python3 ./fgoappupdate.py
```
出力例:

![image](https://user-images.githubusercontent.com/62515228/104086955-8b94e200-529f-11eb-8e87-2b8f846155c8.png)

実用的には cron などを利用して定期的に実行することになります

## Unix で cron を使用して5分毎に実行する例
```$ crontab -e```を実行して下記を入力 

```
0,5,10,15,20,25,30,35,40,45,50,55       *       *       *       *       /home/fgophi/bin/fgoappupdate.py
```
