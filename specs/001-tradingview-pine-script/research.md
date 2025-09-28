# Research: Cryptocurrency Backtesting System Best Practices

## 1. 백테스팅 엔진 아키텍처

### Decision: Event-Driven Architecture with Vectorized Operations
**Rationale**:
- 이벤트 드리븐: 실제 거래 환경과 유사한 시뮬레이션 제공
- 벡터 연산: NumPy/Pandas 활용으로 대량 데이터 고속 처리
- 메모리 효율: 청크 단위 데이터 처리로 메모리 사용 최적화

**Alternatives Considered**:
- Loop-based 처리: 단순하지만 성능 저하 심각
- 순수 SQL 기반: 복잡한 전략 구현 제한적

## 2. Pine Script 전략 구조

### Decision: Modular Strategy Template System
**Rationale**:
- 재사용성: 공통 컴포넌트 라이브러리 활용
- 유지보수: 모듈별 독립적 업데이트 가능
- 테스트: 각 모듈 개별 검증 가능

**Best Practices**:
```pine
//@version=5
strategy("Template", overlay=true,
         initial_capital=10000,
         default_qty_type=strategy.percent_of_equity,
         default_qty_value=10,
         commission_type=strategy.commission.percent,
         commission_value=0.1)

// 1. Input Parameters (Grouped)
// 2. Indicator Calculations
// 3. Entry/Exit Logic
// 4. Risk Management
// 5. Visualization
```

## 3. 데이터 관리 전략

### Decision: 심플한 로컬 스토리지 우선
**Rationale**:
- **Parquet**: 메인 저장소 (압축 효율, 빠른 읽기)
- **SQLite**: 메타데이터만
- **메모리 캐시**: 현재 세션만 (Redis 제거 - 불필요한 복잡성)

**Data Quality Management**:
```python
class DataQualityManager:
    """데이터 품질 관리 전용 클래스"""

    def validate_ohlcv(self, df: pd.DataFrame) -> tuple[bool, list[str]]:
        """OHLCV 데이터 검증"""
        errors = []

        # 1. 필수 컬럼 체크
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        if not all(col in df.columns for col in required_cols):
            errors.append("Missing required columns")

        # 2. OHLC 관계 검증
        if (df['low'] > df['high']).any():
            errors.append("Low > High detected")
        if (df['low'] > df['open']).any() or (df['low'] > df['close']).any():
            errors.append("Low price violation")

        # 3. 이상치 탐지 (IQR 방법)
        for col in ['close', 'volume']:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            outliers = ((df[col] < Q1 - 3*IQR) | (df[col] > Q3 + 3*IQR))
            if outliers.any():
                errors.append(f"Outliers in {col}: {outliers.sum()} points")

        # 4. 갭 검사
        time_diff = df.index.to_series().diff()
        expected_diff = pd.Timedelta(minutes=1)  # 1분봉 기준
        gaps = time_diff[time_diff > expected_diff * 1.5]
        if len(gaps) > 0:
            errors.append(f"Time gaps detected: {len(gaps)} gaps")

        return len(errors) == 0, errors
```

**Gap Filling Strategy**:
```python
def fill_gaps(df: pd.DataFrame, method='forward') -> pd.DataFrame:
    """안전한 갭 필링"""
    # 작은 갭만 채움 (5개 이하)
    if method == 'forward':
        return df.fillna(method='ffill', limit=5)
    elif method == 'interpolate':
        return df.interpolate(method='linear', limit=5)
    else:
        # 갭이 크면 그대로 유지 (거래 중단 시뮬레이션)
        return df
```

## 4. 성능 메트릭 계산

### Decision: Industry Standard Metrics
**Essential Metrics**:
1. **Returns**: Total, Annual, Monthly
2. **Risk**: Sharpe (rf=0%), Sortino, Calmar
3. **Drawdown**: Max DD, DD Duration, Recovery
4. **Win Rate**: Win%, Avg Win/Loss, Profit Factor
5. **Trade Analysis**: Avg Duration, Best/Worst Trade

**Calculation Methods**:
```python
# Sharpe Ratio (annualized)
sharpe = (returns.mean() / returns.std()) * sqrt(252)

# Maximum Drawdown
cumulative = (1 + returns).cumprod()
running_max = cumulative.expanding().max()
drawdown = (cumulative - running_max) / running_max
max_dd = drawdown.min()
```

## 5. 리스크 관리 구현

### Decision: Multi-Layer Risk Control
**Layers**:
1. **Position Sizing**: Kelly Criterion, Fixed Fractional
2. **Stop Loss**: ATR-based, Percentage, Support/Resistance
3. **Portfolio Level**: Correlation limits, Sector exposure
4. **Drawdown Control**: Circuit breakers at -10%, -20%

## 6. 테스팅 전략

### Decision: Comprehensive Test Coverage
**Test Categories**:
1. **Unit Tests** (95% coverage):
   - Indicator calculations
   - Signal generation
   - Position sizing

2. **Integration Tests**:
   - Data pipeline
   - Order execution simulation
   - Performance calculation

3. **Regression Tests**:
   - Known strategy results
   - Edge case handling

4. **Property Tests**:
   - Invariants (e.g., portfolio value >= 0)
   - Consistency checks

## 7. 데이터 수집 전략 (CRITICAL)

### Decision: CCXT 라이브러리 우선, Binance API 보조
**Rationale**:
- **CCXT 메인**: 검증된 에러 처리, 자동 rate limiting, 표준화된 데이터 포맷
- **직접 API 보조**: CCXT 미지원 기능만 사용
- **이중 검증**: 데이터 무결성 보장

**Implementation Strategy**:
```python
import ccxt
from typing import Optional
import asyncio
from datetime import datetime
import pandas as pd

class DataCollector:
    def __init__(self):
        # CCXT 인스턴스 (메인)
        self.exchange = ccxt.binance({
            'enableRateLimit': True,  # 자동 rate limiting
            'rateLimit': 50,  # 50ms between requests
            'options': {
                'defaultType': 'spot',
                'adjustForTimeDifference': True
            }
        })
        # 백업 데이터 소스
        self.backup_sources = ['cached_data', 'alternative_api']

    async def fetch_with_retry(self, symbol: str, timeframe: str,
                               since: Optional[int] = None,
                               limit: int = 500) -> pd.DataFrame:
        """
        안전한 데이터 수집 with 다층 에러 처리
        """
        max_retries = 3
        retry_delay = 1

        for attempt in range(max_retries):
            try:
                # Primary: CCXT
                ohlcv = await self.exchange.fetch_ohlcv(
                    symbol, timeframe, since, limit
                )

                # 데이터 검증
                if self._validate_data(ohlcv):
                    return self._to_dataframe(ohlcv)

            except ccxt.NetworkError as e:
                # 네트워크 오류: 재시도
                await asyncio.sleep(retry_delay * (2 ** attempt))
                continue

            except ccxt.ExchangeError as e:
                # 거래소 오류: 백업 소스 사용
                return await self._fetch_from_backup(symbol, timeframe)

            except Exception as e:
                # 예상치 못한 오류: 로깅 후 안전 모드
                self._log_critical_error(e)
                break

        # 모든 시도 실패: 캐시된 데이터 반환
        return self._get_cached_data(symbol, timeframe)
```

**Data Validation Protocol**:
```python
def _validate_data(self, ohlcv: list) -> bool:
    """엄격한 데이터 검증"""
    checks = [
        self._check_continuity,    # 시간 연속성
        self._check_integrity,     # OHLC 관계
        self._check_outliers,       # 이상치 탐지
        self._check_volume,         # 거래량 검증
        self._check_gaps            # 갭 탐지
    ]

    for check in checks:
        if not check(ohlcv):
            return False
    return True
```

**Error Recovery Strategy**:
1. **Level 1**: CCXT 자동 재시도 (내장)
2. **Level 2**: 수동 exponential backoff
3. **Level 3**: 백업 데이터 소스
4. **Level 4**: 로컬 캐시
5. **Level 5**: Safe mode (거래 중단)

## 8. 거래소 수수료 프리셋

### Decision: Configurable Exchange Profiles
**Presets**:
```python
EXCHANGE_PRESETS = {
    'binance': {
        'maker': 0.1,  # 0.1%
        'taker': 0.1,
        'slippage': 0.05  # 0.05%
    },
    'coinbase': {
        'maker': 0.5,
        'taker': 0.5,
        'slippage': 0.1
    }
}
```

## 9. 미래 Trading Bot 확장성

### Decision: Strategy Interface Pattern
**Design**:
```python
class StrategyInterface(ABC):
    @abstractmethod
    def calculate_signals(self, data: pd.DataFrame) -> pd.Series:
        pass

    @abstractmethod
    def get_position_size(self, signal: float, portfolio: Portfolio) -> float:
        pass
```

**Migration Path**:
1. Backtest → Paper Trading → Live Trading
2. Same strategy code across environments
3. Only execution layer changes

## 10. 성능 최적화

### Decision: Parallel Processing with Chunking
**Techniques**:
- Numba JIT compilation for hot paths
- Multiprocessing for multiple symbols
- Vectorized operations (no loops)
- Memory-mapped files for large datasets

**Performance Targets**:
- 1 year backtest: <5 seconds
- 5 year backtest: <30 seconds
- Parameter optimization: <5 minutes (100 combinations)

## 11. 시각화 및 리포팅

### Decision: Interactive HTML Reports
**Components**:
- Equity curve with drawdown
- Trade scatter plot
- Monthly returns heatmap
- Trade distribution histogram

**Export Formats**:
- HTML (interactive, Plotly-based)
- PDF (static report)
- CSV (raw results)
- JSON (for API consumption)

## 12. 실시간 vs 히스토리컬 데이터 처리

### Decision: 명확한 구분과 각각 최적화
**Historical Data** (백테스팅용):
```python
# 대량 일괄 다운로드
async def download_historical(symbol, start, end):
    """한 번에 대량 다운로드 후 저장"""
    data = []
    current = start

    while current < end:
        batch = await exchange.fetch_ohlcv(
            symbol, '1h',
            since=int(current.timestamp() * 1000),
            limit=1000  # 최대 한도
        )
        data.extend(batch)
        current += timedelta(hours=1000)

    # Parquet으로 저장 (압축 효율)
    df = pd.DataFrame(data, columns=['timestamp', 'o', 'h', 'l', 'c', 'v'])
    df.to_parquet(f'data/{symbol}_{start}_{end}.parquet')
```

**Realtime Data** (향후 라이브 트레이딩용):
```python
# WebSocket 스트리밍 (CCXT Pro)
async def stream_realtime(symbol):
    """실시간 데이터 스트림"""
    while True:
        ticker = await exchange.watch_ticker(symbol)
        # 메모리 버퍼에만 저장
        self.buffer.append(ticker)
        # 주기적으로 디스크에 플러시
        if len(self.buffer) > 100:
            self.flush_to_disk()
```

## 13. 불필요한 복잡성 제거 (YAGNI 원칙)

### 제거된 항목들:
1. **Redis 캐싱**: 로컬 메모리로 충분
2. **다중 데이터베이스**: SQLite 하나로 통일
3. **복잡한 ORM**: 직접 SQL 사용
4. **과도한 추상화**: 3단계 이상 상속 금지
5. **미사용 의존성**: backtrader 제거 (직접 구현)

### 유지할 핵심 요소:
```python
# 심플한 구조
project/
├── data/           # Parquet 파일들
├── strategies/     # Pine Script + Python
├── backtesting/    # 핵심 엔진만
│   ├── engine.py   # 200줄 이하
│   ├── data.py     # CCXT wrapper
│   └── metrics.py  # 필수 메트릭만
└── tests/          # 95% 커버리지
```

## 14. 데이터 수집 Best Practices 총정리

### ✅ DO:
1. **CCXT 사용**: 검증된 라이브러리 우선
2. **데이터 검증**: 모든 데이터 다중 검증
3. **에러 처리**: 5단계 복구 전략
4. **로컬 캐싱**: 네트워크 의존도 최소화
5. **증분 업데이트**: 전체 재다운로드 방지

### ❌ DON'T:
1. **직접 API만 사용**: 에러 처리 복잡
2. **검증 없는 저장**: 잘못된 데이터 = 잘못된 백테스트
3. **무한 재시도**: Rate limit 위반 위험
4. **과도한 추상화**: 디버깅 어려움
5. **외부 의존성**: 최소한으로 유지

## Conclusion

**핵심 원칙: "데이터는 모든 것의 기초"**

개선된 접근 방식:
1. **안정성 최우선**: CCXT + 다층 에러 처리로 데이터 무결성 보장
2. **심플함**: 불필요한 복잡성 제거로 유지보수 용이
3. **성능**: Parquet + 벡터 연산으로 속도 확보
4. **확장성**: 실시간 트레이딩 준비된 구조
5. **신뢰성**: 95% 테스트 커버리지 + 데이터 검증

**위험 완화**:
- 데이터 수집 실패 → 5단계 복구 메커니즘
- 잘못된 데이터 → 다중 검증 프로토콜
- API 제한 → CCXT 자동 rate limiting
- 네트워크 장애 → 로컬 캐시 폴백
