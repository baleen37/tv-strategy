# Quickstart Guide: 최소 암호화폐 백테스팅 시스템

## 🚀 3분 안에 시작하기

### 1. 환경 설정 (1분)

```bash
# 프로젝트 디렉토리로 이동
cd tv-strategy

# Python 가상환경 설정 및 의존성 설치
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. 데이터 다운로드 (1분)

```bash
# BTC/USDT 일봉 데이터 다운로드 (최근 100일)
python -m src.data.ccxt_client download BTCUSDT 1d 100

# 다운로드된 데이터 확인
ls data/
# 출력: BTCUSDT_1d_100.parquet
```

### 3. 백테스트 실행 (1분)

```bash
# 기본 RSI 전략으로 백테스트
python -m src.main backtest

# 출력 예시:
# 📊 Loading data: BTCUSDT 1d (100 bars)
# 🔄 Running RSI backtest...
# 📈 Total Return: 12.5%
# 📉 Max Drawdown: -8.2%
# 🎯 Win Rate: 65.0%
# ✅ Backtest complete!
```

## 📊 추가 사용법

### 다른 심볼 백테스트

```bash
# ETH/USDT 백테스트
python -m src.data.ccxt_client download ETHUSDT 1d 100
python -m src.main backtest --symbol ETHUSDT

# 더 긴 기간 데이터
python -m src.data.ccxt_client download BTCUSDT 1d 365
python -m src.main backtest --symbol BTCUSDT
```

### Pine Script 전략 검증

```bash
# RSI 전략 Pine Script 검증
python -m tests.test_pine src/strategies/rsi_basic.pine

# 출력:
# ✅ Pine Script v6 문법 확인
# ✅ 전략 구조 검증
# ✅ RSI 로직 검증 완료
```

## 🧪 테스트 실행

```bash
# 모든 테스트 실행 (95% 커버리지)
pytest --cov=src --cov-report=term-missing

# 특정 테스트만
pytest tests/test_data.py
pytest tests/test_backtest.py
```

## 🔧 새 전략 추가

```bash
# 템플릿 복사
cp src/strategies/template.pine src/strategies/my_strategy.pine

# 전략 수정 후 검증
python -m tests.test_pine src/strategies/my_strategy.pine
```

## 🐛 트러블슈팅

```bash
# CCXT 연결 테스트
python -c "import ccxt; print(ccxt.binance().fetch_ticker('BTC/USDT'))"

# 의존성 재설치
pip install -r requirements.txt --force-reinstall

# 테스트 커버리지 확인
pytest --cov=src --cov-fail-under=95
```

## ⚠️ 중요 사항

- **데이터 품질**: CCXT 자동 재시도로 안정성 확보
- **테스트 커버리지**: 95% 필수 (Constitution 준수)
- **YAGNI 원칙**: 필요한 기능만 구현

---

다음 단계: `/tasks` 명령으로 구현 작업 시작
