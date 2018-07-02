# -*- coding: utf-8 -*-

import os
import sys
import gmail
from time import sleep

import RPi.GPIO as GPIO
from time import sleep
import subprocess
import datetime

import imaplib, re, email, six

# カメラ撮影関数
def shotPicture():
    d = datetime.datetime.today()
    filename = "{0}{1:02d}{2:02d}{3:02d}{4:02d}{5:02d}.jpg".format(d.year, d.month, d.day, d.hour, d.minute, d.second)
    args = ['raspistill', '-o', filename, '-t', '1']
    subprocess.Popen(args)
    return filename

# メール送信
def sendGmail(u,p,t,s,b,a):
    #u=user,p=pass,t=to_addr,s=subject,b=body,a=attachment
    client = gmail.GMail(u, p)
    if a == '':
        message = gmail.Message(s,to=t,text=b)
    else:
        message = gmail.Message(s,to=t,text=b,attachments=[a])
    client.send(message)
    client.close()

# メール受信
def recieveGmail(s,u,p):
    # s=server,u=username,p=password
    client = imaplib.IMAP4_SSL(s)
    client.login(u,p)
    # 受信箱指定
    client.select('INBOX')
    # 未読メールをメモリに格納（この時点で既読になる）
    typ, [data] = client.search(None, "(UNSEEN)")

    # ない場合は空のcuesリストを返す
    # 未読メールがあったか確認
    cues = []
    if typ == "OK":
        if data != b'':
            print("new mail(s)")
            # メールを一件ずつ処理
            for num in data.split():
                result, d = client.fetch(num, "(RFC822)")
                raw_email = d[0][1]
                #文字コード取得用
                msg = email.message_from_string(raw_email.decode('utf-8'))
                fromObj = email.header.decode_header(msg.get('From'))
                for f in fromObj:
                    cue = ""
                    if isinstance(f[0],bytes):
                        cue = f[0].decode('utf-8')
                    else:
                        cue = str(f[0])
                    cue = re.search(r'<(.+)>',cue)
                    cue = cue.group(0).replace("<","").replace(">","")
                    cues.append(cue)
    client.close()
    client.logout()
    return cues


# gmail定義
username = 'アカウント名@gmail.com'
password = 'パスワード'
server = 'imap.gmail.com'

# 返信するホワイトリスト定義
whitelist = ['返信する','パスワード','のリスト','hogehoge@gmail.com']

while True:
    cues = recieveGmail(server,username,password)
    cues = list(set(cues))
    if cues == []:
        sleep(2)
    else:
        print(cues)
        for addr in cues:
            if addr in whitelist:
                sendGmail(username,password,addr,'かしこまり','ちょっと待ってね','')
                pictpass = shotPicture()
                sleep(3)
                sendGmail(username,password,addr,'はいどうぞ','いかが？',pictpass)
