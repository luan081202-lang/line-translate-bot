from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from googletrans import Translator

app = Flask(__name__)

# =========== 設定區 (請務必填寫正確) ===========
# 1. 貼上你的 Channel Access Token (長的那串)
line_bot_api = LineBotApi('OP+VtPNLPOsyfoCSCIDyj0LSaY3u4P8yS8WsvGeRwxDSUsH9yr1T85rZiXFM6D2mLAu3JaPyAv1tXjinix+xpSkbPArSYkw54ixN/iF7s1wPgnvXZITZ+pkxlFn2ke8fCJqdul8ceA6OhTLTD0jq1gdB04t89/1O/w1cDnyilFU=')

# 2. 貼上你的 Channel Secret (短的那串)
handler = WebhookHandler('ca000c82962e7c300bfa99b9cb36a4ab')
# ============================================

translator = Translator()

@app.route("/callback", methods=['POST'])
def callback():
    # 這是 LINE 用來驗證來源是否正確的機制
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_text = event.message.text
    # 在終端機印出收到的字，方便除錯
    print(f"【收到訊息】: {user_text}")
    
    try:
        # 簡單判定：如果包含英文字母且不含中文，就翻成中文；否則翻成英文
        # 這是最穩定的語系判定邏輯
        is_english = any(c.isalpha() for c in user_text) and not any('\u4e00' <= c <= '\u9fff' for c in user_text)
        
        if is_english:
            translated = translator.translate(user_text, dest='zh-tw').text
        else:
            translated = translator.translate(user_text, dest='en').text
            
        print(f"【翻譯結果】: {translated}")
        
        # 回傳訊息給使用者
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=translated)
        )
    except Exception as e:
        # 如果翻譯過程出錯（例如 Google 暫時封鎖），會印出錯誤原因
        print(f"【錯誤報錯】: {e}")
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="抱歉，翻譯引擎反應過慢，請稍後再試一次！")
        )

if __name__ == "__main__":
    # 監聽 5000 端口，對應 ngrok http 5000
    app.run(port=5000)