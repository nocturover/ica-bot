import os
import requests
from utils.globals import KIS_ACCESS_TOKEN
from utils.log_print import log_print
from rich.table import Table
from rich.console import Console
import json

console = Console()

def get_overseas_holdings():
    """해외주식 보유종목 조회 (해외주식 체결기준현재잔고[v1_해외주식-008])"""
    try:
        # 환경변수 확인
        app_key = os.getenv("KIS_APP_KEY")
        app_secret = os.getenv("KIS_APP_SECRET")
        account = os.getenv("ACCOUNT")
        
        if not app_key or not app_secret or not account:
            log_print("[bold red]Error:[/bold red] 환경변수가 설정되지 않았습니다.")
            return None
        
        # 토큰 확인
        if not KIS_ACCESS_TOKEN:
            log_print("[bold red]Error:[/bold red] KIS 토큰이 없습니다.")
            return None
        
        # 계좌번호 분리 (8-2 형식)
        if len(account) != 11:
            log_print("[bold red]Error:[/bold red] 계좌번호 형식이 올바르지 않습니다. (하이픈 포함 11자리)")
            return None
        
        cano = account[:8]  # 종합계좌번호 (앞 8자리)
        acnt_prdt_cd = account[-2:]  # 계좌상품코드 (뒤 2자리)
        
        # API URL - 해외주식 체결기준현재잔고[v1_해외주식-008] (실전투자)
        url = "https://openapi.koreainvestment.com:9443/uapi/overseas-stock/v1/trading/inquire-present-balance"
        
        # 헤더 설정
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "authorization": f"Bearer {KIS_ACCESS_TOKEN}",
            "appkey": app_key,
            "appsecret": app_secret,
            "tr_id": "CTRP6504R"  # 실전투자 TR ID
        }
        
        # 쿼리 파라미터 - 모든 해외주식 전체 조회
        params = {
            "CANO": cano,  # 종합계좌번호
            "ACNT_PRDT_CD": acnt_prdt_cd,  # 계좌상품코드
            "WCRC_FRCR_DVSN_CD": "02",  # 외화
            "NATN_CD": "000",  # 전체 국가
            "TR_MKET_CD": "00",  # 전체 거래시장
            "INQR_DVSN_CD": "00"  # 전체
        }
        
        log_print("[bold cyan]🌍 해외주식 체결기준현재잔고 조회 중...[/bold cyan]")
        
        # API 호출
        response = requests.get(url, headers=headers, params=params)
        
        if not response.ok:
            log_print(f"[bold red]Error:[/bold red] API 호출 실패: {response.status_code}")
            log_print(f"[bold red]Response:[/bold red] {response.text}")
            return None
        
        data = response.json()
        
        # 응답 확인
        if data.get("rt_cd") != "0":
            log_print(f"[bold red]Error:[/bold red] API 응답 오류")
            log_print(f"[bold red]메시지:[/bold red] {data.get('msg1', '알 수 없는 오류')}")
            return None
        
        # 결과 출력
        print_all_outputs(data)
        
        return data
        
    except Exception as e:
        log_print(f"[bold red]Error:[/bold red] 해외주식 체결기준현재잔고 조회 중 오류 발생: {e}")
        return None

def print_all_outputs(data):
    """모든 output을 콘솔로 출력"""
    console.print()
    console.rule("[bold cyan]📊 해외주식 체결기준현재잔고 조회 결과[/bold cyan]", style="cyan")
    
    # output1 (보유종목 상세)
    output1 = data.get("output1", [])
    if output1:
        console.print()
        console.rule("[bold green]📈 보유종목 상세[/bold green]", style="green")
        console.print(f"[bold green]보유종목 수: {len(output1)}개[/bold green]")
        
        # 보유종목 테이블 생성
        table = Table(title="[bold green]보유종목 목록[/bold green]", show_header=True, header_style="bold green")
        table.add_column("종목코드", style="cyan", width=12)
        table.add_column("종목명", style="white", width=20)
        table.add_column("보유수량", style="yellow", width=12)
        table.add_column("평균단가", style="yellow", width=15)
        table.add_column("현재가", style="yellow", width=15)
        table.add_column("평가손익", style="red", width=15)
        table.add_column("수익률", style="red", width=10)
        table.add_column("거래시장", style="blue", width=10)
        
        for item in output1:
            # 수익률에 따른 색상 결정
            evlu_pfls_rt = float(item.get("evlu_pfls_rt1", "0"))
            profit_color = "green" if evlu_pfls_rt > 0 else "red" if evlu_pfls_rt < 0 else "white"
            
            table.add_row(
                item.get("pdno", ""),
                item.get("prdt_name", ""),
                f"{int(float(item.get('ccld_qty_smtl1', '0'))):,}",
                f"${float(item.get('avg_unpr3', '0')):,.2f}",
                f"${float(item.get('ovrs_now_pric1', '0')):,.2f}",
                f"${float(item.get('evlu_pfls_amt2', '0')):,.2f}",
                f"{evlu_pfls_rt:.2f}%",
                item.get("tr_mket_name", "")
            )
        
        console.print(table)
    else:
        console.print()
        console.print("[bold yellow]📭 보유종목이 없습니다.[/bold yellow]")
    
    # output2 (통화별 요약)
    output2 = data.get("output2", [])
    if output2:
        console.print()
        console.rule("[bold blue]💰 통화별 요약[/bold blue]", style="blue")
        
        # 통화별 요약 테이블 생성
        table = Table(title="[bold blue]통화별 잔고 현황[/bold blue]", show_header=True, header_style="bold blue")
        table.add_column("통화", style="cyan", width=8)
        table.add_column("통화명", style="white", width=15)
        table.add_column("예수금액", style="yellow", width=15)
        table.add_column("출금가능금액", style="yellow", width=15)
        table.add_column("평가금액", style="yellow", width=15)
        table.add_column("최초환율", style="blue", width=12)
        
        for item in output2:
            table.add_row(
                item.get("crcy_cd", ""),
                item.get("crcy_cd_name", ""),
                f"${float(item.get('frcr_dncl_amt_2', '0')):,.2f}",
                f"${float(item.get('frcr_drwg_psbl_amt_1', '0')):,.2f}",
                f"${float(item.get('frcr_evlu_amt2', '0')):,.2f}",
                f"₩{float(item.get('frst_bltn_exrt', '0')):,.2f}"
            )
        
        console.print(table)
    
    # output3 (전체 요약)
    output3 = data.get("output3", {})
    if output3:
        console.print()
        console.rule("[bold magenta]📊 전체 계좌 요약[/bold magenta]", style="magenta")
        
        # 전체 요약 테이블 생성
        table = Table(title="[bold magenta]계좌 전체 현황[/bold magenta]", show_header=True, header_style="bold magenta")
        table.add_column("구분", style="cyan", width=20)
        table.add_column("금액", style="yellow", width=20)
        table.add_column("구분", style="cyan", width=20)
        table.add_column("금액", style="yellow", width=20)
        
        # 첫 번째 행
        pchs_amt = int(output3.get("pchs_amt_smtl", "0"))
        evlu_amt = int(output3.get("evlu_amt_smtl", "0"))
        evlu_pfls = int(output3.get("evlu_pfls_amt_smtl", "0"))
        tot_asst = int(output3.get("tot_asst_amt", "0"))
        
        table.add_row(
            "매입금액합계",
            f"₩{pchs_amt:,}",
            "평가금액합계",
            f"₩{evlu_amt:,}"
        )
        
        # 두 번째 행
        evlu_erng_rt = float(output3.get("evlu_erng_rt1", "0"))
        tot_evlu_pfls = float(output3.get("tot_evlu_pfls_amt", "0"))
        wdrw_psbl = int(output3.get("wdrw_psbl_tot_amt", "0"))
        frcr_use_psbl = float(output3.get("frcr_use_psbl_amt", "0"))
        
        table.add_row(
            "평가손익금액합계",
            f"₩{evlu_pfls:,}",
            "평가수익률",
            f"{evlu_erng_rt:.2f}%"
        )
        
        # 세 번째 행
        table.add_row(
            "총자산금액",
            f"₩{tot_asst:,}",
            "인출가능총금액",
            f"₩{wdrw_psbl:,}"
        )
        
        # 네 번째 행
        table.add_row(
            "총평가손익금액",
            f"₩{tot_evlu_pfls:,.2f}",
            "외화사용가능금액",
            f"₩{frcr_use_psbl:,.2f}"
        )
        
        console.print(table)
    
    # 연속조회 정보
    ctx_area_fk200 = data.get("ctx_area_fk200", "")
    ctx_area_nk200 = data.get("ctx_area_nk200", "")
    tr_cont = data.get("tr_cont", "")
    
    if ctx_area_fk200 or ctx_area_nk200:
        console.print()
        console.rule("[bold magenta]🔄 연속조회 정보[/bold magenta]", style="magenta")
        console.print(f"[bold magenta]ctx_area_fk200:[/bold magenta] {ctx_area_fk200}")
        console.print(f"[bold magenta]ctx_area_nk200:[/bold magenta] {ctx_area_nk200}")
        console.print(f"[bold magenta]tr_cont:[/bold magenta] {tr_cont}")

def check_overseas_holdings():
    """해외주식 보유종목 체크 함수 - True/False만 반환"""
    result = get_overseas_holdings()
    return result is not None

class OverseasHoldings:
    """
    해외주식 체결기준현재잔고 조회용 클래스 (인스턴스 방식)
    사용 예시:
        holdings = OverseasHoldings(appkey, appsecret, access_token, account)
        data = holdings.get_holdings()
        holdings.print_outputs(data)
    """
    API_URL = "https://openapi.koreainvestment.com:9443/uapi/overseas-stock/v1/trading/inquire-present-balance"
    TR_ID = "CTRP6504R"  # 실전투자 TR ID

    def __init__(self, appkey, appsecret, access_token, account):
        self.appkey = appkey
        self.appsecret = appsecret
        self.access_token = access_token
        self.account = account
        self.console = console

    def _split_account(self):
        if len(self.account) != 11:
            raise ValueError("계좌번호 형식이 올바르지 않습니다. (하이픈 포함 11자리)")
        cano = self.account[:8]
        acnt_prdt_cd = self.account[-2:]
        return cano, acnt_prdt_cd

    def _make_headers(self):
        return {
            "Content-Type": "application/json; charset=utf-8",
            "authorization": f"Bearer {self.access_token}",
            "appkey": self.appkey,
            "appsecret": self.appsecret,
            "tr_id": self.TR_ID
        }

    def _make_params(self, cano, acnt_prdt_cd):
        return {
            "CANO": cano,
            "ACNT_PRDT_CD": acnt_prdt_cd,
            "WCRC_FRCR_DVSN_CD": "02",
            "NATN_CD": "000",
            "TR_MKET_CD": "00",
            "INQR_DVSN_CD": "00"
        }

    def get_holdings(self):
        """해외주식 보유종목 조회 (성공시 dict 반환, 실패시 None)"""
        """외화예수금: frcr_dncl_amt_2
        출금가능금액: frcr_drwg_psbl_amt_1
        평가금액: frcr_evlu_amt2
        최초환율: frst_bltn_exrt
        """
        try:
            cano, acnt_prdt_cd = self._split_account()
            headers = self._make_headers()
            params = self._make_params(cano, acnt_prdt_cd)
            log_print("[bold cyan]🌍 (클래스) 해외주식 체결기준현재잔고 조회 시도[/bold cyan]")
            response = requests.get(self.API_URL, headers=headers, params=params)
            if not response.ok:
                return None
            data = response.json()
            if data.get("rt_cd") != "0":
                return None
            return data
        except Exception:
            return None

    def print_outputs(self, data):
        """조회 결과를 콘솔로 출력 (기존 print_all_outputs 재사용)"""
        print_all_outputs(data)
