from PIL import Image
from slack_sdk import WebClient
import os

def send_slack_msg(msg):
    """Slack 메시지 전송"""
    oauth_token = os.getenv("SLACK_BOT_OAUTH_TOKEN")
    channel = os.getenv("SLACK_CHANNEL")
    
    if not oauth_token or not channel:
        return
    
    client = WebClient(oauth_token)
    response = client.chat_postMessage(channel=channel, text=msg)
    
    return response

def convert_image(original_img):
    """이미지에서 가장 진한 픽셀만 남기고 나머지는 흰색 처리"""
    img_rgb = original_img.convert("RGB")
    width, height = img_rgb.size
    darkest_color = (255, 255, 255)
    
    # 가장 진한 픽셀 찾기
    for y in range(height):
        for x in range(width):
            r, g, b = img_rgb.getpixel((x, y))
            intensity = r + g + b
            if intensity < sum(darkest_color):
                darkest_color = (r, g, b)
    
    # 새로운 흰색 이미지 생성
    new_img = Image.new("RGB", (width, height), (255, 255, 255))
    
    # 진한 픽셀만 검정색으로 찍기
    for y in range(height):
        for x in range(width):
            r, g, b = img_rgb.getpixel((x, y))
            if (r, g, b) == darkest_color:
                new_img.putpixel((x, y), (0, 0, 0))
    
    return new_img
