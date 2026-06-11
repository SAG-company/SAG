# 🐾 반려동물 피부 질환 감지 CNN 모델

반려동물 피부 질환 이미지를 분류하는 딥러닝 기반 컴퓨터 비전 프로젝트입니다.
AI Hub의 반려동물 피부 질환 데이터셋을 활용하여 7가지 증상을 분류합니다.

---

## 👥 팀 구성

| 이름 | 역할 |
|------|------|
| OOO | 데이터 수집, EDA, 데이터 정제 |
| OOO | CNN 모델 설계 및 학습 |
| OOO | 전처리 파이프라인, 평가 및 시각화 |

---

## 📌 프로젝트 개요

- **기간**: 2026.06.10 ~ 2026.06.16 (5일)
- **목표**: 반려동물 피부 이미지에서 7가지 질환 증상 분류
- **데이터**: AI Hub - 반려동물 피부 질환 데이터셋 (Dataset No. 561)
- **모델**: 

---

## 🏷️ 분류 클래스

| 코드 | 질환명 |
|------|--------|
| A1 | 구진/플라크 |
| A2 | 비듬/각질/상피성잔고리 |
| A3 | 태선화/과다색소침착 |
| A4 | 농포/여드름 |
| A5 | 미란/궤양 |
| A6 | 결절/종괴 |
| A7 | 무증상 (정상) |

---

## 📁 프로젝트 구조

```text
pet_disease_cnn/
├── data/
│   ├── raw/          # AI Hub 원본 (Git 제외)
│   ├── processed/    # 품질 필터링 + 샘플링 완료
│   ├── split/        # train / val / test
│   └── augmented/    # Augmentation 결과물
├── notebooks/
│   ├── 01_data_collection.ipynb
│   ├── 02_eda.ipynb
│   ├── 03_preprocessing.ipynb
│   └── 04_modeling.ipynb
├── src/
│   ├── OOO
│   ├── OOO
│   ├── OOO
│   ├── OOO
│   └── OOO
├── outputs/
│   ├── models/
│   └── figures/
└── README.md
```

---

## ⚙️ 환경 설정

### 요구 사항
- Python 3.12+

### 설치

git clone https://github.com/SAG-company/SAG.git
cd SAG

---

## 🚀 실행 방법

### 1. 데이터 준비
data/raw/ 폴더에 AI Hub에서 다운받은 라벨링 데이터를 위치시킵니다.

### 2. EDA 및 전처리
```text
notebooks/01_data_collection.ipynb 실행
notebooks/02_eda.ipynb 실행
notebooks/03_preprocessing.ipynb 실행
```

### 3. 모델 학습
python src/train.py

### 4. 평가
python src/evaluate.py --model_path outputs/models/best_model.pth

---

## 📊 실험 결과

| 모델 | Accuracy | F1-Score | AUC-ROC |
|------|----------|----------|---------|
| OOO | 00.00% | 0.000 | 0.000 |

※ 학습 완료 후 채워넣기

---

## 📈 주요 EDA 결과

- 사용 데이터: 반려견, 일반 카메라 이미지 한정
- 클래스당 샘플 수: 5,000장 (층화 샘플링)
- 제거된 저품질 이미지: 000장 (저해상도 000 / 밝기 이상 000 / 손상 000)
- 촬영 부위 분포: 몸통(B) 00% / 다리(L) 00% / 머리(H) 00%

※ EDA 완료 후 채워넣기

---

## ⚠️ 데이터 사용 유의사항

본 프로젝트는 AI Hub 반려동물 피부 질환 데이터셋을 활용합니다.
해당 데이터는 비상업적 연구/교육 목적으로만 사용 가능합니다.
데이터 파일은 저작권 보호를 위해 본 저장소에 포함되지 않습니다.
