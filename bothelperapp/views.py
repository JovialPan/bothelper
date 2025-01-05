from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage, StickerSendMessage, ImageSendMessage, LocationSendMessage
from datetime import datetime
import random
import requests
from bs4 import BeautifulSoup

line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)
def index(request):
    return HttpResponse("Hello World. I'm line bot.")

def invoice():
    url = "https://invoice.etax.nat.gov.tw/index.html"

    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36"
    headers = {'User-Agent': user_agent}
    html = requests.get(url, headers=headers)
    html.encoding ='uft-8'

    soup = BeautifulSoup(html.text, 'html.parser')
    soup.encoding = 'utf-8'

    pp = soup.find_all('a',class_='etw-on')

    rts = "開獎期別:" + pp[0].text + "\n"
    
    nn = soup.find_all('p',class_="etw-tbiggest")
    rts += "特別獎:" + nn[0].text + "\n"
    rts += "特獎:" + nn[1].text + "\n"
    rts += "頭獎:" + nn[2].text.strip() +", " + nn[3].text.strip() +", " + nn[4].text.strip()

    return rts
    
def news():
    url = "https://www.cna.com.tw/list/aall.aspx"
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36"
    headers = {'User-Agent': user_agent}
    html = requests.get(url, headers=headers)
    html.encoding ='uft-8'

    soup = BeautifulSoup(html.text, 'html.parser')
    soup.encoding = 'utf-8'

    nn = soup.find(id='jsMainList')
    rts = ""

    for i in nn.find_all('li')[:5]:
        rts += i.find('div',class_='date').text + ' '
        rts += i.find('h2').text+'\n'
        rts += 'https://www.cna.com.tw/' + i.find('a')['href']
        rts += '\n\n'

    return rts

def banks():
    url = "https://rate.bot.com.tw/xrt?Lang=zh-TW"
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36"
    headers = {'User-Agent': user_agent}
    html = requests.get(url, headers=headers)
    html.encoding = 'utf-8'
    soup = BeautifulSoup(html.text, 'html.parser')

    rows = soup.select("table.table tbody tr")[:3]  
    rts = ""
    for i, row in enumerate(rows, start=1):
        currency_name = row.select_one("div.hidden-phone.print_show").text.strip() 
        cash_buy = row.select_one("td[data-table='本行現金買入']").text.strip()  
        cash_sell = row.select_one("td[data-table='本行現金賣出']").text.strip()  
        rts +=(f"{i}.  {currency_name}") + "\n"
        rts +=(f"   現金買入: {cash_buy}")+ "\n"
        rts +=(f"   現金賣出: {cash_sell}")
        rts += "\n\n"

    return rts


@csrf_exempt
def callback(request):
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')
        try:
            events = parser.parse(body, signature)
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()

        for event in events:
            # 若有訊息事件
           
                
             if isinstance(event, MessageEvent):

                txtmsg = event.message.text

                if txtmsg in ["你好", "Hello", "早安", "Hi", "嗨", "哈囉"]:
                    
                    stkpkg, stkid = 8525, 16581290
                    replymsg = "你好, 小幫手已經準備好為您服務了。"

                    line_bot_api.reply_message(
                    event.reply_token,
                    [StickerSendMessage(package_id = stkpkg, sticker_id=stkid),
                     TextSendMessage( text = replymsg )])

                elif txtmsg.startswith("今天吃什麼"):
                    names = ["蛋炒飯", "紅燒肉", "宮保雞丁", "魚香茄子", "水煮魚", "北京烤鴨", "火鍋", "麻婆豆腐", "小籠包", "鍋貼", "炸醬麵", "清蒸鱸魚", "蠔油芥蘭", "鹽酥雞", "酸辣湯", "蘿蔔糕", "鳳梨蝦球", "台灣牛肉麵", "日式拉麵", "壽司", "生魚片", "天婦羅", "章魚燒", "韓式泡菜鍋", "石鍋拌飯", "韓式炸雞", "泰式綠咖哩", "越南河粉", "印度咖哩", "義大利披薩", "義大利麵", "番茄羅勒湯", "希臘沙拉", "墨西哥玉米餅", "酪梨吐司", "美國漢堡", "炸雞翅", "烤排骨", "法國牛排", "法式焗蜆", "蘇格蘭蛋", "德國豬腳", "西班牙海鮮燉飯", "俄羅斯羅宋湯", "埃及豆泥", "土耳其烤肉捲", "摩洛哥塔吉鍋", "巴西烤肉", "澳洲羊排", "紐約起司蛋糕"]

                    replymsg = "今天吃 " + random.choice(names)

                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage( text = replymsg ))

                elif txtmsg in ["龍山寺求籤","求籤","龍山寺拜拜"]:
                    num = random.choice(range(1,101))
                    imgurl = f"https://www.lungshan.org.tw/fortune_sticks/images/{num:0>3d}.jpg"

                    line_bot_api.reply_message(
                        event.reply_token,
                        ImageSendMessage(original_content_url=imgurl,
                        preview_image_url=imgurl))

                elif txtmsg == "統一發票":
                    replymsg = invoice()
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage( text = replymsg ))

                elif txtmsg == "最新新聞":
                    replymsg = news()
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage( text = replymsg ))
                
                elif txtmsg == "匯率":
                    replymsg = banks()
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage( text = replymsg ))

                else:
                    currentDateAndTime = datetime.now()
                    currentTime = currentDateAndTime.strftime("%H:%M:%S")
                    replymsg = "現在時間: " + currentTime + "\n"
                    replymsg += "已收到以下訊息: " + "\n" 
                    replymsg += "「" + txtmsg + "」"
                    # 回傳收到的文字訊息
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage( text = replymsg ))

        return HttpResponse()
    else:
        return HttpResponseBadRequest()