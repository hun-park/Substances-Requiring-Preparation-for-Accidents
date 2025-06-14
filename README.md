# 대한민국 사고대비물질 특성 기반 클러스터링
## 1. 프로젝트 개요
제공된 사고대비물질 목록의 CAS 번호를 이용해 웹에서 물리적/화학적 특성 데이터를 자동 수집하고, 머신러닝 클러스터링(K-Means)을 적용하여 유사한 위험 특성을 가진 그룹으로 분류하고 분석합니다.

## 2. 작업 절차 (Workflow)
* 1단계: 데이터 수집 (1_data_crawling.ipynb)
CSV 파일에서 CAS 번호를 읽어 PubChem, NIST 등에서 분자량, 끓는점, 인화점, 폭발한계 등 주요 특성 정보를 크롤링하여 원본 데이터를 저장합니다.
   
* 2단계: 데이터 전처리 (2_data_preprocessing.ipynb)
수집한 데이터의 단위를 통일하고 결측치를 처리합니다. 클러스터링 분석을 위해 모든 데이터를 숫자형으로 변환하고 표준화(scaling)합니다.
   
* 3단계: 클러스터링 모델링 (3_clustering_modeling.ipynb)
정제된 데이터에 K-Means 알고리즘을 적용합니다. Elbow Method와 Silhouette Score를 이용해 최적의 군집 수(K)를 결정하고, 물질별 군집 라벨을 저장합니다.
   
* 4단계: 분석 및 시각화 (4_analysis_visualization.ipynb)
PCA를 통해 고차원 데이터를 2차원으로 축소하여 클러스터링 결과를 시각화합니다. 각 군집의 통계적 특성을 분석하여 그룹별 위험성 프로파일을 해석합니다.

## 3. 프로젝트 구조
```
├── 1_data_crawling.ipynb
├── 2_data_preprocessing.ipynb
├── 3_clustering_modeling.ipynb
├── 4_analysis_visualization.ipynb
├── data/
│   ├── 유해물질 목록 - 사고대비물질.csv
│   ├── crawled_raw_data.csv
│   ├── processed_data.csv
│   └── clustering_results.csv
├── requirements.txt
└── README.md
```

## 4. PubChem 속성 조회 스크립트 사용법

`fetch_properties.py`는 `cas_numbers_table.csv`의 CAS 번호 목록을 읽어
PubChem에서 기본 화학 특성을 조회한 뒤 `cas_numbers_property_table.csv`에 저장합니다.

### 실행 방법

1. 필요한 파이썬 패키지를 설치합니다.

   ```bash
   pip install -r requirements.txt
   ```

2. 스크립트를 실행합니다.

   ```bash
   python fetch_properties.py
   ```

성공적으로 완료되면 새 CSV 파일에 Molecule Formula, Molecular Weight 등 특성 정보가 기록됩니다.
