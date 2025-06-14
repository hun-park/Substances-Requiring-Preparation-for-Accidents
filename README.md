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

분자량, 끓는점, 녹는점, 밀도, log Kow 등을 수집하여 `cas_numbers_property_table_v2.csv`로 저장합니다. 온도는 웹사이트에 표시된 단위를 그대로 기록합니다.


### 클러스터링 예제

`cluster_substances.py` 스크립트는 `cas_numbers_property_table_v2.csv` 파일을 활용해 물질들을 다양한 특성 조합으로 K-평균 클러스터링합니다. 분자량, 끓는점, 녹는점, log Kow 네 가지 특성의 모든 짝 조합과 네 특성을 PCA로 축소한 경우에 대해 최적의 클러스터 수(2~6 사이)를 결정하여 이미지로 저장합니다. 각 그래프의 축에는 사용된 특성 조합이, 점 위에는 CAS 번호가 표시되며, 그래프 아래에는 실루엣 점수가 나타납니다. 결과 이미지는 `results/` 디렉터리에 저장되며 저장소에는 포함되지 않으므로 실행 후 직접 확인하세요.

```bash
python cluster_substances.py
```

생성된 PNG 파일을 확인하여 적절한 클러스터 수를 판단할 수 있습니다.
