from datetime import datetime
from rich import print

def log_print(message):
    """날짜시간과 함께 메시지를 출력하는 함수 (muted)"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[dim][{timestamp}][/dim] {message}")