# 導入所需的模塊
from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, LocationMessage
)

import csv
import math
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
# Channel Secret
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))


# 定義 webhook 路徑和方法
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']  # 從請求中獲取 LINE 的簽名
    body = request.get_data(as_text=True)  # 獲取請求主體

    # 用簽名和主體處理 webhook
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)  # 如果簽名不匹配，中止請求

    return 'OK'


# 定義計算兩點間距離的函數
def calculate_distance(lat1, lon1, lat2, lon2):
    # 使用歐幾里得距離公式計算距離
    return math.sqrt((lat2 - lat1) ** 2 + (lon2 - lon1) ** 2)


# 定義查找最近公廁的函數
def find_nearest_restroom(user_lat, user_lon, filepath='public_toilets_test.csv'):
    nearest_restroom = None
    min_distance = float('inf')
    with open(filepath, newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            restroom_lat = float(row['latitude'])
            restroom_lon = float(row['longitude'])
            distance = calculate_distance(user_lat, user_lon, restroom_lat, restroom_lon)
            if distance < min_distance:
                min_distance = distance
                nearest_restroom = row
    return nearest_restroom


@handler.add(MessageEvent, message=LocationMessage)
def handle_location_message(event):
    # 從事件中獲取用戶的經緯度
    lat = event.message.latitude
    lon = event.message.longitude

    # 打印或記錄經緯度，以便確認是否正確接收到位置信息
    print(f"Received location: latitude={lat}, longitude={lon}")

    # 以下是您處理位置信息的其餘邏輯...
    # 例如，查找最近的公廁並回復用戶
    nearest_restroom = find_nearest_restroom(lat, lon)
    if nearest_restroom:
        reply_message = f"最近的公廁是：{nearest_restroom['name']}，地址：{nearest_restroom['address']}"
    else:
        reply_message = "抱歉，我們找不到附近的公廁。"

    # 回復消息給用戶
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_message)
    )


# 處理文本消息的事件處理器
@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    # 無論收到什麼文本消息，都提示用戶分享位置
    reply_message = "請點選左下角加號並分享位置資訊給我!"
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_message)
    )


# 啟動 Flask 應用
if __name__ == "__main__":
    app.run(port=5000)

# user_status = {}

# from linebot.models import (
#     MessageEvent, TextMessage, TextSendMessage, LocationMessage,
#     TemplateSendMessage, ButtonsTemplate, PostbackAction
# )

# from linebot.models import TemplateSendMessage, ButtonsTemplate, PostbackAction

# @handler.add(MessageEvent, message=TextMessage)
# def handle_text_message(event):
#     # 創建按鈕樣板消息
#     buttons_template_message = TemplateSendMessage(
#         alt_text='互動模式選擇',
#         template=ButtonsTemplate(
#             title='請選擇互動模式',
#             text='選擇後將進行相應的互動',
#             actions=[
#                 PostbackAction(label='最速模式', data='quick_mode'),
#                 PostbackAction(label='篩選模式', data='filter_mode')
#             ]
#         )
#     )

#     # 使用 reply_message 方法發送按鈕樣板消息
#     line_bot_api.reply_message(event.reply_token, buttons_template_message)


# @handler.add(PostbackEvent)
# def handle_postback(event):
#     user_id = event.source.user_id
#     data = event.postback.data

#     if data == 'quick_mode':
#         user_status[user_id] = 'quick_mode'
#         reply_message = "您已選擇最速模式，請分享您的位置。"
#     elif data == 'filter_mode':
#         user_status[user_id] = 'filter_mode'
#         reply_message = "您已選擇篩選模式，請分享您的位置。"
#     else:
#         reply_message = "無效的選擇"

#     line_bot_api.reply_message(
#         event.reply_token,
#         TextSendMessage(text=reply_message)
#     )


# @handler.add(MessageEvent, message=LocationMessage)
# def handle_location_message(event):
#     user_id = event.source.user_id
#     lat = event.message.latitude
#     lon = event.message.longitude

#     if user_id in user_status and user_status[user_id] == 'quick_mode':
#         nearest_restroom = find_nearest_restroom(lat, lon)
#         if nearest_restroom:
#             reply_message = f"最近的公廁是：{nearest_restroom['name']}，地址：{nearest_restroom['address']}"
#         else:
#             reply_message = "抱歉，我們找不到附近的公廁。"
#     elif user_id in user_status and user_status[user_id] == 'filter_mode':
#         # 這裡可以進一步實現篩選模式的邏輯
#         reply_message = "篩選模式下的功能開發中..."
#     else:
#         reply_message = "請選擇互動模式。"

#     line_bot_api.reply_message(
#         event.reply_token,
#         TextSendMessage(text=reply_message)
#     )


# 處理位置消息的事件處理器
# @handler.add(MessageEvent, message=LocationMessage)
# def handle_location_message(event):
#     lat = event.message.latitude  # 獲取用戶發送的緯度
#     lon = event.message.longitude  # 獲取用戶發送的經度

#     nearest_restroom = find_nearest_restroom(lat, lon)


#     nearest_restroom = find_nearest_restroom(lat, lon)
#     if nearest_restroom:
#         reply_message = f"最近的公廁是：{nearest_restroom['name']}，地址：{nearest_restroom['address']}"
#     else:
#         reply_message = "抱歉，我們找不到附近的公廁。"
#     line_bot_api.reply_message(
#         event.reply_token,
#         TextSendMessage(text=reply_message)
    # )
