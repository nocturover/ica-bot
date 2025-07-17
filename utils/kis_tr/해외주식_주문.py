import requests

class OverseasStockOrder:
    """
    한국투자증권 해외주식 주문 API 래퍼 클래스 (실전계좌용, 인스턴스 방식)

    사용 예시:
    >>> order = OverseasStockOrder(
    ...     appkey='...', appsecret='...', access_token='Bearer ...',
    ...     account_no='12345678', account_product_code='01'
    ... )
    >>> # 미국 나스닥, AAPL 1주, 180달러 지정가 매수
    >>> result = order.buy(
    ...     exchange='US', ovrs_excg_cd='NASD', symbol='AAPL', qty=1, price=180.0
    ... )
    >>> print(result)
    >>> # 미국 나스닥, AAPL 1주, 200달러 지정가 매도
    >>> result = order.sell(
    ...     exchange='US', ovrs_excg_cd='NASD', symbol='AAPL', qty=1, price=200.0
    ... )
    >>> print(result)

    파라미터 설명:
    - appkey: OpenAPI 앱키
    - appsecret: OpenAPI 앱시크릿
    - access_token: 'Bearer ...' 형식의 접근 토큰
    - account_no: 계좌 앞 8자리
    - account_product_code: 계좌 뒤 2자리
    - exchange: 'US'(미국), 'JP'(일본), 'HK'(홍콩) 등 (TR_ID 자동 결정)
    - ovrs_excg_cd: 해외거래소코드 (예: 'NASD', 'NYSE', 'AMEX', 'SEHK', 'TKSE' 등)
    - symbol: 종목코드(12자리, 필요시 0-padding)
    - qty: 주문수량(정수)
    - price: 주문단가(지정가)
    - ord_type: 주문구분(00: 지정가, 31/32/33/34 등은 API 문서 참고)
    """
    BASE_URL = "https://openapi.koreainvestment.com:9443"
    ORDER_PATH = "/uapi/overseas-stock/v1/trading/order"

    # 거래소별 TR_ID 매핑 (실전)
    TR_ID_MAP = {
        "US": {"buy": "TTTT1002U", "sell": "TTTT1006U"},  # 미국(나스닥)
        "JP": {"buy": "TTTS0308U", "sell": "TTTS0307U"},  # 일본
        "HK": {"buy": "TTTS1002U", "sell": "TTTS1001U"},  # 홍콩
        # 필요시 추가
    }

    def __init__(self, appkey, appsecret, access_token, account_no, account_product_code):
        self.appkey = appkey
        self.appsecret = appsecret
        self.account_no = account_no
        self.account_product_code = account_product_code
        self.access_token = access_token

    def _make_headers(self, tr_id):
        return {
            "Content-Type": "application/json",
            "authorization": 'Bearer ' + self.access_token,  # self.access_token은 'Bearer ...' 형태로 전달
            "appKey": self.appkey,
            "appSecret": self.appsecret,
            "tr_id": tr_id,
            "custtype": "P",
        }


    def _order(self, side, exchange, ovrs_excg_cd, symbol, qty, price, ord_type="00"):
        """
        내부 주문 실행 함수 (직접 호출하지 마세요)
        side: 'buy' or 'sell'
        exchange: 'US', 'JP', 'HK' 등 (TR_ID 자동 결정)
        ovrs_excg_cd: 해외거래소코드 (예: 'NASD', 'NYSE', 'SEHK', 'TKSE' 등)
        symbol: 종목코드 (12자리)
        qty: 주문수량 (정수)
        price: 주문단가 (float, 지정가)
        ord_type: 주문구분 (00: 지정가, 31/32/33/34 등은 API 문서 참고)
        """
        tr_info = self.TR_ID_MAP[exchange]
        tr_id = tr_info[side]
        body = {
            "CANO": self.account_no,
            "ACNT_PRDT_CD": self.account_product_code,
            "OVRS_EXCG_CD": ovrs_excg_cd,
            "PDNO": symbol,
            "ORD_QTY": str(int(qty)),
            "OVRS_ORD_UNPR": f"{round(price,2)}",
            "ORD_SVR_DVSN_CD": "0",
            "ORD_DVSN": ord_type,
        }
        headers = self._make_headers(tr_id)
        url = self.BASE_URL + self.ORDER_PATH
        response = requests.post(url, headers=headers, json=body)
        return response.json()

    def buy(self, exchange, ovrs_excg_cd, symbol, qty, price, ord_type="00"):
        """
        해외주식 매수 주문
        :param exchange: 'US', 'JP', 'HK' 등 (TR_ID 자동 결정)
        :param ovrs_excg_cd: 해외거래소코드 (예: 'NASD', 'NYSE', 'AMEX', 'SEHK', 'TKSE' 등)
        :param symbol: 종목코드(12자리) - SOXL, AAPL, 
        :param qty: 주문수량
        :param price: 주문단가(지정가)
        :param ord_type: 주문구분(00: 지정가, 31/32/33/34 등)
        :return: 주문 결과(JSON)
        """
        return self._order("buy", exchange, ovrs_excg_cd, symbol, qty, price, ord_type)

    def sell(self, exchange, ovrs_excg_cd, symbol, qty, price, ord_type="00"):
        """
        해외주식 매도 주문
        :param exchange: 'US', 'JP', 'HK' 등 (TR_ID 자동 결정)
        :param ovrs_excg_cd: 해외거래소코드 (예: 'NASD', 'NYSE', 'AMEX', 'SEHK', 'TKSE' 등)
        :param symbol: 종목코드(12자리) - SOXL, AAPL, 
        :param qty: 주문수량
        :param price: 주문단가(지정가)
        :param ord_type: 주문구분(00: 지정가, 31/32/33/34 등)
        :return: 주문 결과(JSON)
        """
        return self._order("sell", exchange, ovrs_excg_cd, symbol, qty, price, ord_type)