from utils.initailize import check_db, check_env_file, check_holdings, check_kis_token, check_settings
from rich.console import Console
from rich.table import Table
console = Console()


console.print()
console.rule("", style="blue", characters="=")
console.print("[bold cyan]ICA Bot v0.0.1[/bold cyan]", justify="center")
console.rule("", style="blue", characters="=")
console.print()



def print_step_table(step_num, column_title, row_text):
    table = Table(
        title=f"[bold yellow]Step{step_num}[/bold yellow]",
        border_style="yellow",
    )
    table.add_column(column_title, style="cyan", justify="center")
    table.add_row(row_text)
    console.print(table, justify="center")

def print_check_result(title, success_message, error_message, check_function):
    """재사용 가능한 체크 결과 출력 함수"""
    if check_function():
        console.rule(f"[bold green]:white_check_mark: {title} 완료! :white_check_mark:[/bold green]")
        console.print(f"[bold green]{success_message}[/bold green]", justify="center")
        console.print()
        return True
    else:
        console.print(f"[bold red]{error_message}[/bold red]", justify="center")
        return False

# Step1 : .env 파일 확인
print_step_table(1, ".env 파일 확인", ".env 에 설정된 계좌번호 및 app key 확인")
if not print_check_result(
    ".env 파일 확인",
    "모든 환경변수가 정상적으로 설정되었습니다!",
    "환경변수 설정이 올바르지 않습니다.",
    check_env_file
):
    exit()

# Step2 : db 파일 확인
print_step_table(2, "db 파일 확인", "db.sqlite3 파일이 존재하는지 확인합니다.")
if not print_check_result(
    "db 파일 확인",
    "db.sqlite3 파일이 존재합니다.",
    "db.sqlite3 파일 조회/생성 실패했습니다.",
    check_db
):
    exit()

# Step3 : 토큰 조회/생성 테이블
print_step_table(3, "KIS 토큰 조회/생성/스케줄러", "KIS 토큰을 조회/생성하고 스케줄러를 시작합니다.")
if not print_check_result(
    "KIS 토큰 조회/생성",
    "KIS 토큰이 정상적으로 조회/생성되었습니다.",
    "KIS 토큰 조회/생성 실패했습니다.",
    check_kis_token 
):
    exit()

# Step4 : 보유종목조회 테이블
print_step_table(4, "해외주식 체결기준현재잔고", "해외주식 체결기준현재잔고를 조회합니다.")
if not print_check_result(
    "해외주식 체결기준현재잔고",
    "해외주식 체결기준현재잔고가 정상적으로 조회되었습니다.",
    "해외주식 체결기준현재잔고 조회 실패했습니다.",
    check_holdings
):
    exit()

# Step5 : 무한매수법 세팅값 확인 및 시작 
print_step_table(5, "무한매수법 세팅값 확인", "무한매수법 세팅값을 확인합니다.")
if not print_check_result(
    "무한매수법 세팅값 확인",
    "무한매수법 세팅값이 정상적으로 확인되었습니다.",
    "무한매수법 세팅값 확인 실패했습니다.",
    check_settings
):
    exit()
