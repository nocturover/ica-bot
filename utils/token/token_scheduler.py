import threading
import time
from datetime import datetime, timedelta
from utils.token.get_token import get_kis_token
from utils.globals import KIS_ACCESS_TOKEN
from utils.log_print import log_print
from rich import print

class TokenScheduler:
    def __init__(self, check_interval_minutes=30):
        """
        토큰 자동 갱신 스케줄러
        
        Args:
            check_interval_minutes (int): 토큰 체크 간격 (분 단위, 기본값: 30분)
        """
        self.check_interval_minutes = check_interval_minutes
        self.is_running = False
        self.scheduler_thread = None
        self.last_check_time = None
        
    def start(self):
        """스케줄러 시작"""
        if self.is_running:
            log_print("[bold yellow]Warning:[/bold yellow] 토큰 스케줄러가 이미 실행 중입니다.")
            return
            
        self.is_running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        log_print(f"[bold green]토큰 스케줄러가 시작되었습니다. (체크 간격: {self.check_interval_minutes}분)[/bold green]")
        
    def stop(self):
        """스케줄러 중지"""
        self.is_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        log_print("[bold yellow]토큰 스케줄러가 중지되었습니다.[/bold yellow]")
        
    def _scheduler_loop(self):
        """스케줄러 메인 루프"""
        while self.is_running:
            try:
                # 현재 시간 기록
                self.last_check_time = datetime.now()
                
                # 토큰 가져오기 (필요시 자동 갱신)
                token = get_kis_token()
                
                if token:
                    print(f"[dim][SCHEDULER] 토큰 상태: 정상 (다음 체크: {(self.last_check_time + timedelta(minutes=self.check_interval_minutes)).strftime('%Y-%m-%d %H:%M:%S')})[/dim]")
                
                # 지정된 간격만큼 대기
                time.sleep(self.check_interval_minutes * 60)
                
            except Exception as e:
                time.sleep(300)
                
    def get_status(self):
        """스케줄러 상태 정보 반환"""
        status = {
            "is_running": self.is_running,
            "check_interval_minutes": self.check_interval_minutes,
            "last_check_time": self.last_check_time,
            "current_token": KIS_ACCESS_TOKEN[:4] + "..." if KIS_ACCESS_TOKEN else None
        }
        return status

# 전역 스케줄러 인스턴스
token_scheduler = TokenScheduler()

def start_token_scheduler(check_interval_minutes=30):
    """
    토큰 스케줄러 시작 함수
    
    Args:
        check_interval_minutes (int): 체크 간격 (분 단위)
    """
    global token_scheduler
    token_scheduler = TokenScheduler(check_interval_minutes)
    token_scheduler.start()
    
def stop_token_scheduler():
    """토큰 스케줄러 중지 함수"""
    global token_scheduler
    token_scheduler.stop()
    
def get_scheduler_status():
    """스케줄러 상태 조회 함수"""
    global token_scheduler
    return token_scheduler.get_status() 