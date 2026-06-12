# 📋 반려동물 구강 및 피부 질환 감지 딥러닝 미니 프로젝트: 데이터 명세서 (Data Specification)

본 문서는 AI Hub의 **반려동물 피부 질환 데이터(381.99 GB)**를 기반으로 진행되는 5일간의 컴퓨터 비전 미니 프로젝트에서 최종 구축된 데이터셋 구조와 전처리 파이프라인 명세서입니다. 

---

## 1. 데이터셋 개요 (Dataset Overview)
* [cite_start]**원본 데이터:** AI Hub 반려동물 피부 질환 데이터 [cite: 81]
* [cite_start]**프로젝트 대상 범위 확장:** 기존 반려견(Dog) 데이터에서 **반려묘(Cat) 데이터까지 축종 범위를 확장(`D`, `C`)**하여 모델의 범용성을 확보함[cite: 95, 106].
* **데이터 관리 구조:**
  * `..` (ROOT) : 프로젝트 최상위 경로
  * [cite_start]`../data/raw/` : 최초 원본 이미지(`*.jpg`) 및 라벨링(`*.json`) 저장소 [cite: 91, 92]
  * `../data/raw_sub/` : 층화 샘플링으로 선정된 알짜배기 정예 표본 이미지 격리 폴더 (3일 차 전처리 가속화용)
  * `../data/processed/` : 정제 완료된 메타데이터 마스터 CSV 파일 보관 경로

---

## 2. 데이터셋 컬럼 명세 (Column Specification)

`dataset.csv` 및 최종 품질 검증이 끝난 `dataset_cleaned.csv` 구조 정의서입니다.

| 컬럼명 (Column) | 타입 (Type) | 설명 (Description) | 비고 / 범위 가이드 |
| :--- | :--- | :--- | :--- |
| **`json_path`** | `String` | 파싱된 원본 JSON 파일의 저장 경로 | 오류 디버깅 및 역추적용 |
| **`img_file`** | `String` | 이미지 파일명 (확장자 포함) | [cite_start]메타데이터 내 `Raw data ID` 매핑 [cite: 139] |
| **`species`** | `String` | 반려동물 축종 코드 | [cite_start]**`D` (개 / Dog)** 및 **`C` (고양이 / Cat)** 대상을 모두 포함 [cite: 147] |
| **`lesion`** | `String` | 피부 질환 클래스 코드 (라벨) | [cite_start]**A1 ~ A7** 분류 코드 체계 적용 [cite: 149] |
| **`lesion_name`**| `String` | 피부 질환 클래스의 한국어 매핑명 | EDA 시각화 및 결과 도출용 한글 레이블 |
| **`region`** | `String` | 촬영 신체 부위 코드 | [cite_start]**B** (몸통), **L** (다리), **H** (머리), **A** (연접부) [cite: 145, 146] |
| **`path_type`** | `String` | 증상 유무 분류명 | [cite_start]`유증상` / `무증상` [cite: 151] |
| **`hash`** | `String` | 이미지 바이너리 MD5 체크섬 값 | 중복 이미지 완전 배제용 고유 키 |
| **`split`** | `String` | 모델 학습용 데이터 분할 그룹 | **`train`** (70%), **`val`** (15%), **`test`** (15%) |
| **`img_path`** | `String` | 로컬 환경 내 원본 이미지 절대 경로 | 로컬 드라이브 전용 매핑 경로 |
| **`sub_img_path`**| `String` | **격리 폴더(`data/raw_sub/`) 내부 경로** | **★ 모델링 팀원 학습 데이터 로더 최적화 입력 컬럼** |
| **`quality`** | `String` | 이미지 자동 품질 검사 결과 코드 | **`OK`** (정상), `밝기이상`, `저해상도`, `단색손상`, `파일손상` |

### [cite_start]🔍 질환 코드 (`lesion` → `lesion_name`) 매핑 규칙 [cite: 149]
* [cite_start]**`A1`**: 구진 / 플라크 (Papule / Plaque) [cite: 149]
* **`A2`**: 비듬 / 각질 / 상피성잔고리 (Scale / Crust) [cite: 149]
* [cite_start]**`A3`**: 태선화 / 과다색소침착 (Lichenification) [cite: 149]
* [cite_start]**`A4`**: 농포 / 여드름 (Pustule) [cite: 149]
* **`A5`**: 미란 / 궤양 (Erosion / Ulcer) [cite: 149]
* [cite_start]**`A6`**: 결절 / 종괴 (Nodule / Tumor) [cite: 149]
* [cite_start]**`A7`**: **무증상 (정상군 / Normal)** -> *JSON 내부 `lesions` 공백 시 `Path` 데이터 폴백 예외처리 완료* [cite: 149]

---

## 3. 핵심 정제 및 최적화 파이프라인 흐름

1. **라벨-이미지 일치 필터링 & 고속 해시 중복 제거 (`01_data_collection.ipynb`)**
   * 축종(`D`, `C`) 및 유효 라벨 확인 후, 로컬 드라이브상에 실제 매핑되는 원본 `.jpg` 파일이 존재하는지 딕셔너리 인덱싱 기반으로 교차 검증을 진행합니다.
   * `hashlib.md5` 연산을 활용해 완벽하게 중복되는 중복본 이미지 장수를 원천 제거했습니다.

2. **클래스 및 부위 균형을 고려한 층화 샘플링 (Stratified Sampling)**
   * 특정 증상이나 특정 촬영 부위에만 딥러닝 모델이 편향 학습되는 것을 막기 위해 `groupby(['lesion', 'region'])` 기반 샘플링을 수행합니다.
   * 각 클래스별 목표 데이터 볼륨 수(`TARGET_PER_CLASS = 5000`)에 맞춘 균등 분할 기법을 적용했습니다.

3. **알짜배기 이미지 데이터 격리 (`raw_sub`)**
   * 전체 수십만 장 중 최종 샘플링된 최정예 표본 이미지들만 멀티스레딩(`ThreadPoolExecutor`)을 통해 프로젝트 전용 폴더(`data/raw_sub/`)로 고속 복사 처리했습니다.
   * 이를 통해 모델링 담당자는 대용량 스토리지 인프라 없이 소형화된 환경에서 수십 배 빠른 이미지 I/O 속도로 학습을 진행할 수 있습니다.

4. **EDA 기반 품질 스크리닝 (`02_eda.ipynb` → `dataset_cleaned.csv`)**
   * 이미지 픽셀 매트릭스의 기초 통계 데이터($100 \times 100$ 미만의 `저해상도`, 평균 밝기값 기준을 벗어난 `밝기이상`, 표준편차가 지나치게 낮은 `단색손상` 등)를 기준으로 이미지 품질 스크리닝을 자동화했습니다.
   * 결함 이미지가 완벽하게 차단되고 **`quality == 'OK'`** 가 판정된 행만 선별하여 최종 배포용 마스터 메타데이터 파일인 **`dataset_cleaned.csv`**를 생성했습니다.

---

## 4. 모델링 팀원 학습 파이프라인 연동 가이드

* **데이터셋 선언:** 데이터 학습 파이프라인 생성 시 `dataset_cleaned.csv`를 호출한 뒤, 입력 이미지 경로를 `df['sub_img_path']`로 연동하십시오.
* **정규화 설정값 (Normalization Config):** `02_eda.ipynb` 실행 결과단 최하위에 출력되는 RGB 채널별 `mean` 및 `std` 리스트 값을 복사하여 모델 트랜스폼 내 `transforms.Normalize()`의 매개변수로 그대로 주입하여 최적 수렴 속도를 확보하십시오.