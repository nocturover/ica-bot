#!/usr/bin/env python3
"""
토큰 스케줄러 테스트 스크립트
"""

import time
from utils.token_scheduler import start_token_scheduler, stop_token_scheduler, get_scheduler_status
from utils.globals import KIS_ACCESS_TOKEN
from utils.log_print import log_print

def test_scheduler():
    """스케줄러 테스트 함수"""
    log_print("[bold cyan]토큰 스케줄러 테스트를 시작합니다...[/bold cyan]")
    
    # 스케줄러 시작 (1분 간격으로 테스트)
    start_token_scheduler(check_interval_minutes=1)
    
    try:
        # 5분간 실행 (5번의 체크)
        for i in range(5):
            time.sleep(60)  # 1분 대기
            
            # 현재 상태 출력
            status = get_scheduler_status()
            log_print(f"[bold green]테스트 {i+1}/5 - 스케줄러 상태:[/bold green]")
            log_print(f"  실행 중: {status['is_running']}")
            log_print(f"  체크 간격: {status['check_interval_minutes']}분")
            log_print(f"  마지막 체크: {status['last_check_time']}")
            log_print(f"  현재 토큰: {status['current_token']}")
            log_print("")
            
    except KeyboardInterrupt:
        log_print("[bold yellow]사용자에 의해 테스트가 중단되었습니다.[/bold yellow]")
    
    finally:
        # 스케줄러 중지
        stop_token_scheduler()
        log_print("[bold green]테스트가 완료되었습니다.[/bold green]")

if __name__ == "__main__":
    test_scheduler() 