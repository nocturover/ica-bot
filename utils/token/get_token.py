import os
import sqlite3
from datetime import datetime, timedelta
import requests
from utils.log_print import log_print

def get_kis_token():
    """KIS 토큰 조회/생성 함수"""
    try:
        # 환경변수 확인
        app_key = os.getenv("KIS_APP_KEY")
        app_secret = os.getenv("KIS_APP_SECRET")
        
        if not app_key or not app_secret:
            log_print("[bold red]Error:[/bold red] KIS_APP_KEY 또는 KIS_APP_SECRET이 설정되지 않았습니다.")
            return None
        
        # 데이터베이스 연결
        conn = sqlite3.connect("database/db.sqlite3")
        cursor = conn.cursor()
        
        # 1. DB에서 kis 토큰 중 가장 최신 것을 찾음
        cursor.execute("""
            SELECT token, expired_at FROM Token 
            WHERE provider = 'kis' 
            ORDER BY expired_at DESC 
            LIMIT 1
        """)
        latest = cursor.fetchone()
        
        now = datetime.now()
        one_hour = timedelta(hours=1)
        
        if latest:
            token, expired_at_str = latest
            expired_at = datetime.fromisoformat(expired_at_str.replace('Z', '+00:00'))
            
            # 만료 1시간 전이 아니면 기존 토큰 사용
            if expired_at - now > one_hour:
                # 전역변수에 토큰 저장
                import utils.globals
                utils.globals.KIS_ACCESS_TOKEN = token
                conn.close()
                return token
        
        # 2. 만료 1시간 이내면 새로 발급
        
        url = "https://openapi.koreainvestment.com:9443/oauth2/tokenP"
        body = {
            "grant_type": "client_credentials",
            "appkey": app_key,
            "appsecret": app_secret,
        }
        headers = {
            "Content-Type": "application/json",
        }
        
        response = requests.post(url, headers=headers, json=body)
        
        if not response.ok:
            log_print(f"[bold red]Error:[/bold red] 토큰 발급 실패: {response.status_code} {response.text}")
            conn.close()
            return None
        
        data = response.json()
        access_token = data.get("access_token")
        expired_at = data.get("access_token_token_expired")
        
        if not access_token or not expired_at:
            log_print("[bold red]Error:[/bold red] 토큰 응답에 필수 필드가 없습니다.")
            conn.close()
            return None
        
        # DB에 저장
        cursor.execute("""
            INSERT INTO Token (provider, token, expired_at, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """, ('kis', access_token, expired_at, now, now))
        
        conn.commit()
        conn.close()
        
        # 전역변수에 토큰 저장
        import utils.globals
        utils.globals.KIS_ACCESS_TOKEN = access_token
        return access_token
        
    except Exception as e:
        log_print(f"[bold red]Error:[/bold red] KIS 토큰 발급 중 오류 발생: {e}")
        return None