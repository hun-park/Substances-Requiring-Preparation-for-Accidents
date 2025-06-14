# 사고대비물질 데이터 수집 도구

이 저장소는 대한민국 "사고대비물질" 목록의 CAS 번호를 이용해 주요 물리·화학 특성을 수집하는 간단한 스크립트를 제공합니다.

## 파일 구성

- `cas_numbers_table.csv` – 사고대비물질 목록과 CAS 번호
- `fetch_properties.py` – PubChem에서 기본 특성을 조회하여 `cas_numbers_property_table.csv`로 저장합니다.
- `fetch_extended_properties.py` – PubChem, ChemSpider, NIST WebBook을 활용해 더 많은 특성을 수집하여 `cas_numbers_property_table_v2.csv`로 저장합니다.
- `requirements.txt` – 실행에 필요한 파이썬 패키지 목록

## 사전 준비

```bash
pip install -r requirements.txt
```

`fetch_extended_properties.py`를 사용할 경우 ChemSpider API 키가 필요합니다. 환경변수 `CHEMSPIDER_API_KEY` 또는 `CHEMSPIDER_TOKEN`에 키를 설정하세요.

## 사용 방법

### 기본 특성 수집

```bash
python fetch_properties.py
```

CAS 번호별로 분자식, 분자량, LogP 등 기본 정보를 `cas_numbers_property_table.csv`에 기록합니다.

### 확장 특성 수집

```bash
python fetch_extended_properties.py
```

분자량, 끓는점, 녹는점, 밀도, log Kow 등을 수집하여 `cas_numbers_property_table_v2.csv`로 저장합니다. 화씨나 켈빈으로 표시된 온도는 자동으로 섭씨로 변환됩니다.

