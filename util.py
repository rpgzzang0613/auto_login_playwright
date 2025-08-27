from PIL import Image
from slack_sdk import WebClient
import os
import time
from functools import wraps

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

def retry(times=2, delay=1):
    """재시도 데코레이터: 지정 횟수만큼 실패 시 재시도"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(times):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"{func.__name__} 시도 {attempt+1} 실패: {e}")
                    time.sleep(delay)
            raise Exception(f"{func.__name__} 재시도 {times}회 실패")
        return wrapper
    return decorator
