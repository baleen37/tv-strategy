# TradingView Strategy Repository 📈

프로페셔널 Pine Script v6 전략 개발 및 테스트 프레임워크

## 🎯 특징

- **Pine Script v6** 최신 버전 지원
- **표준화된 보일러플레이트** 템플릿
- **자동화된 검증** 시스템
- **리스크 관리** 통합
- **재사용 가능한 컴포넌트** 라이브러리

## 📁 프로젝트 구조

```
tv-strategy/
├── strategies/              # 전략 스크립트
│   ├── trend-following/    # 추세 추종 전략
│   ├── mean-reversion/     # 평균 회귀 전략
│   ├── momentum/           # 모멘텀 전략
│   │   ├── rsi_strategy.pine      # 기본 RSI 전략
│   │   └── rsi_strategy_v2.pine   # 고급 RSI 전략
│   ├── volume/             # 거래량 기반 전략
│   └── multi-timeframe/    # 다중 시간대 전략
├── indicators/             # 재사용 가능한 지표
├── tests/                  # 검증 도구
│   ├── validator.py        # Pine Script 문법 검증
│   └── test_rsi_strategy.py # RSI 전략 테스트
├── templates/              # 보일러플레이트 템플릿
│   └── strategy_boilerplate.pine
├── utils/                  # 유틸리티 라이브러리
│   ├── risk_management.pine      # 리스크 관리 함수
│   └── technical_indicators.pine # 기술적 지표 함수
└── backtest-results/       # 백테스트 결과
```

## 🚀 빠른 시작

### 1. Pine Script 검증

```bash
# 기본 문법 검증
python tests/validator.py strategies/momentum/rsi_strategy.pine

# 전략 로직 테스트
python tests/test_rsi_strategy.py strategies/momentum/rsi_strategy.pine
```

### 2. TradingView에서 사용

1. TradingView 차트 열기
2. Pine Editor 열기 (차트 하단)
3. 전략 코드 복사/붙여넣기
4. "Add to Chart" 클릭
5. Strategy Tester로 백테스트 실행

## 📊 포함된 전략

### RSI Momentum Strategy V2
고급 RSI 전략 with:
- 다양한 RSI 모드 (Standard, Smoothed, StochRSI)
- 다이버전스 감지
- 트렌드 필터
- 동적 리스크 관리
- 세션 필터링

**주요 기능:**
- 최대 드로다운 제한
- 일일 손실 제한
- ATR 기반 스톱로스
- 트레일링 스톱
- 실시간 성과 대시보드

## 🛠 보일러플레이트 템플릿

`templates/strategy_boilerplate.pine` 특징:

### 구조
1. **메타데이터**: 전략 설정 및 초기 자본
2. **입력 파라미터**: 구조화된 입력 그룹
3. **리스크 관리**: 통합 리스크 컨트롤
4. **유틸리티 함수**: 재사용 가능한 로직
5. **시각화**: 정보 패널 및 차트 표시

### 리스크 관리 기능
- 최대 드로다운 제한
- 일일 손실 제한
- 포지션 사이징
- 거래 시간 제한
- 쿨다운 기간

## 📚 유틸리티 라이브러리

### Risk Management (`utils/risk_management.pine`)
- 포지션 사이징 (Fixed, Kelly, ATR-based)
- 스톱로스 계산 (Percent, ATR, Volatility, Swing)
- 트레일링 스톱
- 샤프/소르티노 비율
- 드로다운 계산

### Technical Indicators (`utils/technical_indicators.pine`)
- 다양한 이동평균 (SMA, EMA, WMA, HMA, TEMA)
- 모멘텀 지표 (RSI, MACD, CCI, Williams %R)
- 변동성 지표 (Bollinger Bands, Keltner, ATR)
- 거래량 지표 (OBV, MFI, CMF)
- 패턴 인식 (Divergence, Support/Resistance)

## 🔧 검증 도구

### `validator.py`
Pine Script 문법 및 구조 검증:
- 버전 확인
- 전략 선언 검증
- 리스크 관리 체크
- 진입/청산 로직 검증
- 문법 오류 감지

### `test_rsi_strategy.py`
RSI 전략 특화 테스트:
- 파라미터 범위 검증
- 리스크/리워드 비율
- 코드 품질 체크
- 잠재적 이슈 감지

## 📈 백테스팅 워크플로우

1. **전략 개발**: 템플릿 사용하여 새 전략 생성
2. **로컬 검증**: Python 검증 도구 실행
3. **TradingView 테스트**: 플랫폼에서 백테스트
4. **결과 분석**: CSV/JSON으로 결과 내보내기
5. **최적화**: 파라미터 조정 및 개선

## ⚠️ 주의사항

- Pine Script는 TradingView 서버에서만 실행
- 백테스트 결과는 실제 거래와 다를 수 있음
- 리페인팅 주의 (request.security 사용 시)
- 슬리피지 및 수수료 고려

## 🤝 기여 방법

1. 새 전략은 적절한 카테고리에 추가
2. 보일러플레이트 구조 준수
3. 검증 도구로 테스트 통과 필수
4. 문서화 및 주석 포함

## 📝 라이센스

MIT License

## 🔗 참고 자료

- [TradingView Pine Script v6 Docs](https://www.tradingview.com/pine-script-docs/)
- [Pine Script Reference](https://www.tradingview.com/pine-script-reference/v6/)
- [Strategy Tester Guide](https://www.tradingview.com/support/solutions/43000481029/)