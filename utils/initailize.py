import json
import os
import sqlite3
from dotenv import load_dotenv
from utils.log_print import log_print
from rich import print
from utils.token.get_token import get_kis_token
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

        # strategy_result 테이블 생성 
        # cycle, symbol, round, T, star_pct, position, avg_price, sell_target_price, star_pct_target_price,cash, portfolio_value, signal, reason, position_rev_rate, realized_profit_amount, position_mdd, cumulative_buy_amount, cumulative_return_rate
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS strategy_result (
                id INTEGER PRIMARY KEY AUTOINCREMENT,   
                executed_at DATETIME NOT NULL,
                cycle INTEGER,               
                symbol TEXT,
                ovrs_excg_cd TEXT,
                round INTEGER,
                T REAL,
                star_pct REAL,
                position REAL,
                avg_price REAL,
                sell_target_price REAL,
                star_pct_target_price REAL,
                cash REAL,
                portfolio_value REAL,
                signal INTEGER,
                reason TEXT,
                position_rev_rate REAL,
                realized_profit_amount REAL,
                position_mdd REAL,
                cumulative_buy_amount REAL,
                cumulative_return_rate REAL,
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
        # 토큰 조회 및 갱신
        get_kis_token()
        
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


def check_settings():
    # setting.json 파일 내 모든 세팅값이 존재하는지 확인 + 표로 출력
    from rich.table import Table
    from rich.console import Console

    console = Console()

    if not os.path.exists("setting.json"):
        log_print("[bold red]Error:[/bold red] setting.json 파일이 존재하지 않습니다.")
        return False

    with open("setting.json", "r") as f:
        settings = json.load(f)

    table = Table(title="[bold yellow]무한매수법 세팅값 확인[/bold yellow]", border_style="yellow")
    table.add_column("설정 항목", style="cyan", justify="center")
    table.add_column("값", style="magenta", justify="center")
    table.add_column("상태", style="green", justify="center")

    all_ok = True
    for key, value in settings.items():
        # 값이 None이거나, 문자열일 경우 strip() 후 빈 문자열인지 확인
        if value is None or (isinstance(value, str) and value.strip() == ""):
            table.add_row(f"[bold red]{key}[/bold red]", "[red]설정되지 않음[/red]", "[bold red]❌[/bold red]")
            all_ok = False
        else:
            table.add_row(f"{key}", f"{value}", "[bold green]✅[/bold green]")

    console.print(table, justify="center")

    if not all_ok:
        log_print("[bold red]설정값 중 누락된 항목이 있습니다. 설정을 확인해주세요.[/bold red]")
        return False

    return True