import os
import sqlite3
from dotenv import load_dotenv
from utils.log_print import log_print
from rich import print
from utils.token.token_scheduler import start_token_scheduler, get_scheduler_status

def check_env_file():
    if not os.path.exists(".env"):
        log_print("[bold red]Error:[/bold red] .env 파일이 존재하지 않습니다.")
        return False
    load_dotenv(".env")
    env_vars = {
        "KIS_APP_KEY": (lambda x: x[:4] + "*" * (len(x) - 4) if x else None)(os.getenv("KIS_APP_KEY")),
        "KIS_APP_SECRET": (lambda x: x[:4] + "*" * (len(x) - 4) if x else None)(os.getenv("KIS_APP_SECRET")),
        "ACCOUNT": os.getenv("ACCOUNT"),
        "KOREXIM_ACCESS_KEY": (lambda x: x[:4] + "*" * (len(x) - 4) if x else None)(os.getenv("KOREXIM_ACCESS_KEY")),
    }
    all_ok = True
    for key, value in env_vars.items():
        if value is None or value.strip() == "":
            log_print(f"[bold red]{key}[/bold red] : [red]설정되지 않음[/red]")
            all_ok = False
        else:
            log_print(f"[bold green]{key}[/bold green] : {value}")
    return all_ok

def check_db():
    try:
        # database 디렉토리 생성
        os.makedirs("database", exist_ok=True)
        
        if not os.path.exists("database/db.sqlite3"):
            log_print("[bold yellow]Warning:[/bold yellow] db.sqlite3 파일이 존재하지 않습니다.")
            log_print("[bold yellow]Warning:[/bold yellow] db.sqlite3 파일을 생성합니다.")
        
        conn = sqlite3.connect("database/db.sqlite3")
        cursor = conn.cursor()
        
        # Token 테이블 생성
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Token (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                provider TEXT NOT NULL,
                token TEXT UNIQUE NOT NULL,
                expired_at DATETIME NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        if not os.path.exists("database/db.sqlite3"):
            log_print("[bold green]db.sqlite3 파일을 생성했습니다.[/bold green]")
        else:
            # 데이터베이스에 존재하는 테이블들을 보기 좋게 출력
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            tables = [table[0] for table in cursor.fetchall()]
            if tables:
                log_print("[bold green]📋 현재 데이터베이스에 존재하는 테이블 목록:[/bold green]")
                for idx, table_name in enumerate(tables, 1):
                    log_print(f"[bold cyan]{idx}. {table_name}[/bold cyan]")
            else:
                log_print("[bold yellow]데이터베이스에 테이블이 존재하지 않습니다.[/bold yellow]")

                   
        conn.commit()
        conn.close()
            
        return True
    except Exception as e:
        log_print(f"[bold red]Error:[/bold red] {e}")
        return False

def check_kis_token():
    """KIS 토큰 체크 및 스케줄러 시작 - True/False만 반환"""
    try:
        # Step5 : 토큰 자동 갱신 스케줄러 시작
        log_print("[bold cyan]🚀 토큰 자동 갱신 스케줄러를 시작합니다...[/bold cyan]")
        start_token_scheduler(check_interval_minutes=30)

        # 스케줄러 상태 출력
        status = get_scheduler_status()
        log_print(f"[bold green]\t✅ 스케줄러 상태: {'실행 중' if status['is_running'] else '중지됨'}[/bold green]")
        log_print(f"[bold green]\t⏰ 체크 간격: {status['check_interval_minutes']}분[/bold green]")

        log_print("[bold green]\t🎉 모든 초기화가 완료되었습니다![/bold green]")
        log_print("[bold yellow]\t🔄 토큰은 30분마다 자동으로 체크되고 갱신됩니다.[/bold yellow]")
        
        return True
    except Exception as e:
        log_print(f"[bold red]❌ Error:[/bold red] {e}")
        return False   


def check_holdings():
    """해외주식 보유종목 조회 체크 함수"""
    from utils.kis_tr.해외주식_체결기준현재잔고 import check_overseas_holdings
    return check_overseas_holdings()

def check_balance():
    return True