const pptxgen = require("pptxgenjs");

// ─── 색상 ───────────────────────────────
const NAVY = "0D1B2A", GOLD = "F5A623", WHITE = "FFFFFF", LIGHT = "F4F6F8";
const MUTED = "8899AA", TEAL = "028090", TEAL2 = "00A896";
const SUCCESS = "16A34A", WARN = "D97706", SLATE = "334155";
const BASE = "C:/Users/금정산2-PC02/SAG_project";

const shadow = () => ({ type: "outer", color: "000000", blur: 8, offset: 3, angle: 45, opacity: 0.12 });

let p = new pptxgen();
p.layout = "LAYOUT_16x9";
p.title = "AI 수의사 — 반려동물 피부질환 분류 AI 서비스";
p.author = "SAG Team";

function header(s, title, sub) {
  s.addShape(p.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 1.0, fill: { color: NAVY }, line: { color: NAVY } });
  s.addText(title, { x: 0.4, y: 0.08, w: 9.2, h: sub ? 0.6 : 0.84, fontSize: 25, color: WHITE, bold: true, fontFace: "Calibri", valign: "middle" });
  if (sub) s.addText(sub, { x: 0.42, y: 0.62, w: 9.2, h: 0.32, fontSize: 11, color: "9FB3C8", fontFace: "Calibri" });
}
function conclusion(s, text) {
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: 0.3, y: 4.85, w: 9.4, h: 0.6, fill: { color: NAVY }, line: { color: NAVY }, rectRadius: 0.08 });
  s.addText("결론  " + text, { x: 0.45, y: 4.85, w: 9.1, h: 0.6, fontSize: 12, color: GOLD, bold: true, align: "left", valign: "middle", fontFace: "Calibri" });
}

// ════════════════ SLIDE 1 — 프로젝트 소개 ════════════════
{
  let s = p.addSlide();
  s.background = { color: NAVY };
  s.addShape(p.shapes.OVAL, { x: 7.4, y: -0.6, w: 4.0, h: 4.0, fill: { color: "1A2D42" }, line: { color: "1A2D42" } });
  s.addShape(p.shapes.OVAL, { x: 8.6, y: 2.9, w: 1.9, h: 1.9, fill: { color: GOLD, transparency: 70 }, line: { color: GOLD, transparency: 70 } });
  s.addText("AI 기반 반려동물 피부질환 분석 서비스", { x: 0.55, y: 0.8, w: 7, h: 0.4, fontSize: 13, color: GOLD, fontFace: "Calibri" });
  s.addText("AI 수의사", { x: 0.5, y: 1.2, w: 8, h: 1.4, fontSize: 70, color: WHITE, bold: true, fontFace: "Calibri" });
  s.addText("반려동물 피부 사진 한 장으로 병변 유형과 진료 필요도를 분석하는\nAI 기반 초기 선별 보조 서비스", {
    x: 0.55, y: 2.75, w: 8.2, h: 0.7, fontSize: 16, color: "CADCFC", fontFace: "Calibri", lineSpacingMultiple: 1.1
  });
  s.addShape(p.shapes.RECTANGLE, { x: 0.55, y: 3.55, w: 2.6, h: 0.04, fill: { color: GOLD }, line: { color: GOLD } });
  s.addText([
    { text: "다루는 문제: ", options: { bold: true, color: WHITE } },
    { text: "보호자가 \"지금 병원에 가야 하나?\"를 사진으로 빠르게 가늠하도록 돕기", options: { breakLine: true } },
    { text: "팀 SAG  ·  2026.06.10 ~ 06.16  ·  Python · TensorFlow · EfficientNetB3 · Streamlit" },
  ], { x: 0.55, y: 3.75, w: 8.6, h: 1.0, fontSize: 12.5, color: MUTED, fontFace: "Calibri", lineSpacingMultiple: 1.15 });
  s.addText("🐾", { x: 8.85, y: 4.75, w: 1, h: 0.6, fontSize: 34 });
  s.addNotes("1장. 안녕하세요, 팀 SAG입니다. 저희가 만든 'AI 수의사'를 발표하겠습니다. 반려동물 피부 사진 한 장으로 병변 유형과 진료 필요도를 분석하는 AI 보조 서비스입니다. 핵심은 진단이 아니라, 보호자가 '지금 병원에 가야 하나?'를 빠르게 판단하도록 돕는 초기 선별 도구라는 점입니다.");
}

// ════════════════ SLIDE 2 — 문제 정의 ════════════════
{
  let s = p.addSlide();
  s.background = { color: LIGHT };
  header(s, "왜 이 서비스가 필요한가?");
  const boxes = [
    { x: 0.4, icon: "😟", t: "누구의 문제인가", b: "반려동물 보호자. 피부에 이상이 보여도 단순 상처인지, 병원이 필요한 상태인지 스스로 판단하기 어렵습니다." },
    { x: 3.65, icon: "🏥", t: "왜 필요한가", b: "확신이 없어 진료를 미루거나, 반대로 불필요하게 자주 방문합니다. 적절한 시점 판단이 어렵습니다." },
    { x: 6.9, icon: "🎯", t: "우리의 목표", b: "사진 기반 예측으로 피부 이상 가능성과 위험도를 빠르게 확인해, 보호자의 다음 행동 결정을 보조합니다." },
  ];
  boxes.forEach(bx => {
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: bx.x, y: 1.25, w: 2.7, h: 2.95, fill: { color: WHITE }, line: { color: "D0D8E4" }, rectRadius: 0.12, shadow: shadow() });
    s.addText(bx.icon, { x: bx.x + 1.0, y: 1.42, w: 0.7, h: 0.6, fontSize: 28, align: "center" });
    s.addText(bx.t, { x: bx.x + 0.15, y: 2.05, w: 2.4, h: 0.4, fontSize: 15, bold: true, color: NAVY, align: "center", fontFace: "Calibri" });
    s.addText(bx.b, { x: bx.x + 0.2, y: 2.5, w: 2.3, h: 1.55, fontSize: 12, color: SLATE, align: "center", fontFace: "Calibri", lineSpacingMultiple: 1.12 });
  });
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: 1.0, y: 4.3, w: 8.0, h: 0.5, fill: { color: "FEF3C7" }, line: { color: WARN }, rectRadius: 0.08 });
  s.addText("\"질병 확정 진단이 아닌, 초기 선별을 돕는 보조 도구\"로서의 AI", { x: 1.0, y: 4.3, w: 8.0, h: 0.5, fontSize: 13, color: "92400E", bold: true, align: "center", valign: "middle", fontFace: "Calibri" });
  s.addText("AI를 '만들었다'가 아니라, 왜 필요했는지가 출발점입니다.", { x: 0.4, y: 4.92, w: 9.2, h: 0.4, fontSize: 12, color: GOLD, bold: true, align: "center", fontFace: "Calibri" });
  s.addNotes("2장. 반려동물 보호자라면 누구나 겪는 상황입니다. 피부에 뭔가 이상한데, 지금 병원을 가야 할지 더 지켜봐도 될지 모르는 거죠. 그래서 진료를 미루거나, 반대로 불필요하게 자주 가게 됩니다. 저희는 이 판단을 사진으로 보조하려 했습니다. 진단을 대체하는 게 아니라 초기 선별을 돕는 보조 도구라는 점이 핵심입니다.");
}

// ════════════════ SLIDE 3 — 데이터 소개 ════════════════
{
  let s = p.addSlide();
  s.background = { color: LIGHT };
  header(s, "어떤 데이터를 썼는가?");
  const metrics = [["34,987", "총 학습 이미지"], ["7", "병변 클래스"], ["70 / 15 / 15", "Train/Val/Test(%)"], ["~5,000장", "클래스별 균등 샘플"]];
  metrics.forEach((m, i) => {
    const x = 0.4 + i * 2.32;
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y: 1.15, w: 2.1, h: 1.15, fill: { color: NAVY }, line: { color: NAVY }, rectRadius: 0.1 });
    s.addText(m[0], { x, y: 1.2, w: 2.1, h: 0.66, fontSize: 19, color: GOLD, bold: true, align: "center", valign: "bottom", fontFace: "Calibri" });
    s.addText(m[1], { x, y: 1.83, w: 2.1, h: 0.42, fontSize: 10, color: MUTED, align: "center", fontFace: "Calibri" });
  });
  const rows = [
    [{ text: "코드", options: { bold: true, color: WHITE, fill: { color: NAVY } } }, { text: "병변 유형", options: { bold: true, color: WHITE, fill: { color: NAVY } } }],
    ["A1", "구진 / 플라크"], ["A2", "비듬 / 각질"], ["A3", "태선화 / 색소침착"], ["A4", "농포 / 여드름"],
    ["A5", "미란 / 궤양"], ["A6", "결절 / 종괴"],
    [{ text: "A7", options: { color: SUCCESS } }, { text: "무증상 (정상)", options: { color: SUCCESS } }],
  ];
  s.addTable(rows, { x: 0.4, y: 2.5, w: 4.0, colW: [1.0, 3.0], border: { pt: 0.5, color: "D0D8E4" }, fontSize: 11.5, fontFace: "Calibri", align: "left", valign: "middle", fill: { color: WHITE }, rowH: 0.27 });
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: 4.8, y: 2.5, w: 4.9, h: 1.9, fill: { color: WHITE }, line: { color: "D0D8E4" }, rectRadius: 0.12, shadow: shadow() });
  s.addText("데이터 출처 · 입력 · 처리", { x: 4.95, y: 2.6, w: 4.6, h: 0.4, fontSize: 13, bold: true, color: NAVY, fontFace: "Calibri" });
  s.addText([
    { text: "출처: ", options: { bold: true, color: NAVY } }, { text: "AI Hub 반려동물 피부 질환 데이터 (No.561)", options: { breakLine: true } },
    { text: "입력: ", options: { bold: true, color: NAVY } }, { text: "피부 이미지 + 동물 종류·부위(메타정보)", options: { breakLine: true } },
    { text: "Target: ", options: { bold: true, color: NAVY } }, { text: "7개 병변 유형 / 정상 여부", options: { breakLine: true } },
    { text: "처리: ", options: { bold: true, color: NAVY } }, { text: "MD5 중복제거 · 품질 스크리닝 · 층화 샘플링", options: {} },
  ], { x: 4.95, y: 3.05, w: 4.6, h: 1.3, fontSize: 12, color: SLATE, fontFace: "Calibri", lineSpacingMultiple: 1.15 });
  conclusion(s, "이미지와 메타정보로 7개 병변 클래스를 예측하도록 데이터를 구성했습니다.");
  s.addNotes("3장. 데이터는 AI Hub의 반려동물 피부 질환 데이터입니다. 약 3만 5천 장, 7개 병변 클래스를 클래스당 약 5천 장씩 균등하게 맞췄고, 70/15/15로 나눴습니다. 중복 제거와 품질 스크리닝, 층화 샘플링을 거쳤습니다. 정리하면 이미지와 동물·부위 정보로 7개 병변 클래스를 예측하는 구성입니다.");
}

// ════════════════ SLIDE 4 — EDA 인사이트 ════════════════
{
  let s = p.addSlide();
  s.background = { color: LIGHT };
  header(s, "데이터에서 무엇을 발견했는가?");
  s.addChart(p.charts.PIE, [{ name: "축종", labels: ["강아지 88.6%", "고양이 11.4%"], values: [31003, 3984] }], {
    x: 0.3, y: 1.2, w: 3.7, h: 2.9, chartColors: ["1C3D6E", GOLD], showPercent: true, showLegend: true, legendPos: "b",
    dataLabelColor: WHITE, dataLabelFontSize: 12, showTitle: true, title: "축종 분포", titleFontSize: 13, titleColor: NAVY,
  });
  const ins = [
    { y: 1.2, c: NAVY, t: "축종 불균형", b: "강아지 88.6% vs 고양이 11.4%.", k: "→ 단순 정확도는 고양이 성능을 가릴 수 있어 클래스·축종별로 따로 확인" },
    { y: 2.45, c: TEAL, t: "클래스 균등 · 부위 편중", b: "7개 클래스는 균형. 단 일부 병변은 귀·발 등에 집중.", k: "→ Accuracy보다 클래스별 Precision·Recall·F1 확인이 필수" },
    { y: 3.7, c: WARN, t: "A2(비듬) ↔ A3(태선화) 유사", b: "육안으로도 구분이 어려운 외형.", k: "→ Confusion Matrix로 혼동 패턴을 미리 파악" },
  ];
  ins.forEach(it => {
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: 4.2, y: it.y, w: 5.5, h: 1.12, fill: { color: WHITE }, line: { color: "D0D8E4" }, rectRadius: 0.1, shadow: shadow() });
    s.addText(it.t, { x: 4.35, y: it.y + 0.08, w: 5.2, h: 0.3, fontSize: 12.5, bold: true, color: it.c, fontFace: "Calibri" });
    s.addText(it.b, { x: 4.35, y: it.y + 0.4, w: 5.2, h: 0.3, fontSize: 11, color: SLATE, fontFace: "Calibri" });
    s.addText(it.k, { x: 4.35, y: it.y + 0.72, w: 5.2, h: 0.34, fontSize: 11, color: GOLD, bold: true, fontFace: "Calibri" });
  });
  conclusion(s, "불균형·클래스 유사성 때문에, 단순 정확도보다 클래스별 지표 확인이 중요했습니다.");
  s.addNotes("4장. EDA는 그래프 자랑이 아니라 모델링 근거입니다. 첫째, 강아지 88.6%, 고양이 11.4%로 불균형합니다. 전체 정확도만 보면 고양이 성능이 가려질 수 있어 클래스·축종별로 따로 봤습니다. 둘째, 클래스 수는 균등하지만 촬영 부위가 편중돼 클래스별 Precision·Recall·F1이 필요했습니다. 셋째, 비듬과 태선화는 육안으로도 비슷해 Confusion Matrix로 혼동을 미리 확인하기로 했습니다.");
}

// ════════════════ SLIDE 5 — 모델링 방법 ════════════════
{
  let s = p.addSlide();
  s.background = { color: LIGHT };
  header(s, "어떤 방식으로 모델링했는가?");
  const steps = [
    { x: 0.4, c: "1C3D6E", t: "직접 설계 CNN", v: "42.0%", d: "Conv2D ×4 · 128px" },
    { x: 3.35, c: TEAL, t: "EfficientNetB0 (frozen)", v: "50.3%", d: "전이학습 · 224px" },
    { x: 6.5, c: WARN, t: "EfficientNetB3 (2단계)", v: "57.6%", d: "fine-tuning · 최종·서비스 연결" },
  ];
  steps.forEach((e, i) => {
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: e.x, y: 1.2, w: 3.0, h: 1.25, fill: { color: WHITE }, line: { color: e.c }, rectRadius: 0.1, shadow: shadow() });
    s.addText(e.t, { x: e.x + 0.15, y: 1.3, w: 2.7, h: 0.34, fontSize: 12.5, bold: true, color: e.c, fontFace: "Calibri" });
    s.addText(e.v, { x: e.x + 0.15, y: 1.62, w: 2.7, h: 0.42, fontSize: 22, bold: true, color: NAVY, fontFace: "Calibri" });
    s.addText(e.d, { x: e.x + 0.15, y: 2.08, w: 2.7, h: 0.3, fontSize: 10, color: MUTED, fontFace: "Calibri" });
    if (i < 2) s.addText("▶", { x: e.x + 3.0, y: 1.66, w: 0.35, h: 0.35, fontSize: 15, color: MUTED, align: "center" });
  });
  const t = [
    [{ text: "항목", options: { bold: true, color: WHITE, fill: { color: NAVY } } }, { text: "설계", options: { bold: true, color: WHITE, fill: { color: NAVY } } }],
    ["문제 유형", "이미지 다중 분류 (7개 병변 / 정상)"],
    ["모델", "EfficientNetB3 전이학습 — Phase1 백본 고정(헤드 학습) → Phase2 fine-tuning"],
    ["입력 / 전처리", "224×224, EfficientNet 정규화(0~255 그대로 입력)"],
    ["평가 지표", "Accuracy · Precision · Recall · F1 · Confusion Matrix"],
  ];
  s.addTable(t, { x: 0.4, y: 2.65, w: 9.3, colW: [1.9, 7.4], border: { pt: 0.5, color: "D0D8E4" }, fontSize: 11.5, fontFace: "Calibri", align: "left", valign: "middle", fill: { color: WHITE }, rowH: 0.42 });
  conclusion(s, "정확도만이 아니라 '어떤 병변을 놓치는지' 보려고 클래스별 지표·CM을 함께 봤습니다.");
  s.addNotes("5장. 코드를 줄줄이 설명하지 않겠습니다. 이미지가 들어오면 7개 병변 클래스를 예측하는 분류 문제입니다. 직접 설계 CNN 42%에서 출발해, 사전학습 EfficientNetB0 전이학습으로 50.3%, 최종적으로 더 큰 EfficientNetB3를 2단계로 학습했습니다. 1단계는 백본 고정 후 분류기만, 2단계는 백본을 풀어 미세조정해 57.6%까지 올렸습니다. 어떤 질환을 놓치는지 보려고 Confusion Matrix와 클래스별 지표를 함께 확인했습니다.");
}

// ════════════════ SLIDE 6 — 모델 결과 ════════════════
{
  let s = p.addSlide();
  s.background = { color: LIGHT };
  header(s, "결과는 어땠고, 어떻게 해석하는가?");
  s.addImage({ path: BASE + "/outputs/figures/eval_confusion_matrix.png", x: 0.35, y: 1.15, w: 3.35, h: 2.96 });
  s.addText("테스트셋 5,246장 · EfficientNetB3", { x: 0.35, y: 4.08, w: 3.35, h: 0.25, fontSize: 9.5, color: MUTED, align: "center", fontFace: "Calibri" });
  const m = [["57.6%", "Accuracy"], ["0.571", "F1 (macro)"], ["85.4%", "Top-3 정확도"], ["67.7% > 56.2%", "고양이 > 강아지"]];
  m.forEach((mm, i) => {
    const x = 3.95 + (i % 2) * 2.95, y = 1.15 + Math.floor(i / 2) * 0.86;
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y, w: 2.8, h: 0.74, fill: { color: NAVY }, line: { color: NAVY }, rectRadius: 0.08 });
    s.addText(mm[0], { x: x + 0.1, y: y + 0.05, w: 2.6, h: 0.42, fontSize: 17, bold: true, color: GOLD, fontFace: "Calibri" });
    s.addText(mm[1], { x: x + 0.1, y: y + 0.46, w: 2.6, h: 0.24, fontSize: 9.5, color: "9FB3C8", fontFace: "Calibri" });
  });
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: 3.95, y: 2.95, w: 5.75, h: 1.78, fill: { color: WHITE }, line: { color: "D0D8E4" }, rectRadius: 0.1, shadow: shadow() });
  s.addText("해석", { x: 4.1, y: 3.02, w: 5, h: 0.3, fontSize: 12, bold: true, color: NAVY, fontFace: "Calibri" });
  s.addText([
    { text: "• 잘 분류: A5 미란/궤양(F1 0.74), A6 결절/종괴(0.72) — 외형이 뚜렷", options: { breakLine: true } },
    { text: "• 가장 약함: A2 비듬/각질(0.44) — 여러 클래스가 A2로 오인됨", options: { breakLine: true } },
    { text: "• 최다 혼동: A2 ↔ A3(태선화) — 실제 A3의 21%를 A2로 예측", options: { breakLine: true } },
    { text: "• A7 정상은 재현율이 낮음 → '이상' 쪽으로 보수적 (선별엔 안전)", options: {} },
  ], { x: 4.1, y: 3.34, w: 5.45, h: 1.35, fontSize: 10.5, color: SLATE, fontFace: "Calibri", lineSpacingMultiple: 1.12 });
  conclusion(s, "57.6%는 가능성을 보였지만 A2↔A3 혼동은 적용 전 개선 필요 → 낮은 신뢰도 클래스는 보수적 안내.");
  s.addNotes("6장. 숫자만 말하지 않겠습니다. 전체 정확도 57.6%, 정답이 상위 3개 안에 드는 비율 85.4%. 흥미롭게도 데이터가 훨씬 적은 고양이가 67.7%로 강아지 56.2%보다 더 정확했습니다 — EDA 우려와 정반대였습니다. 왼쪽 혼동행렬에서 A5 미란/궤양, A6 결절/종괴는 대각선이 진해 잘 맞히고, A2 비듬이 가장 약하며 A3와 가장 많이 혼동합니다. 정상(A7)은 재현율이 낮아 이상 쪽으로 보수적인데, 선별 도구로는 안전한 방향입니다. 그래서 낮은 신뢰도 클래스는 보수적으로 안내하도록 설계했습니다.");
}

// ════════════════ SLIDE 7 — 서비스 시연 ════════════════
{
  let s = p.addSlide();
  s.background = { color: LIGHT };
  header(s, "실제로 어떻게 작동하는가?", "Streamlit 서비스 · sagproject.streamlit.app");
  const flow = ["① 업로드 / 샘플 선택", "② AI 예측 (7클래스 확률)", "③ 위험도 4단계", "④ 맞춤 행동 가이드", "⑤ Grad-CAM 시각화"];
  flow.forEach((f, i) => {
    const x = 0.4 + i * 1.9;
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y: 1.2, w: 1.78, h: 0.7, fill: { color: i === 0 ? GOLD : WHITE }, line: { color: i === 0 ? GOLD : "D0D8E4" }, rectRadius: 0.08, shadow: shadow() });
    s.addText(f, { x: x + 0.05, y: 1.2, w: 1.68, h: 0.7, fontSize: 9.5, bold: true, color: i === 0 ? NAVY : SLATE, align: "center", valign: "middle", fontFace: "Calibri" });
  });
  const samp = [
    { f: "/assets/samples/sample_A5.jpg", cap: "A5 미란/궤양 · 97%", risk: "빠른 진료 권장", rc: "DC2626" },
    { f: "/assets/samples/sample_A3.jpg", cap: "A3 태선화/색소 · 88%", risk: "진료 권장", rc: WARN },
    { f: "/assets/samples/sample_A7.jpg", cap: "A7 정상 · 72%", risk: "정상 가능성 높음", rc: SUCCESS },
  ];
  samp.forEach((sp, i) => {
    const x = 0.7 + i * 3.0;
    s.addImage({ path: BASE + sp.f, x, y: 2.2, w: 2.6, h: 1.46 });
    s.addText(sp.cap, { x, y: 3.7, w: 2.6, h: 0.3, fontSize: 11, bold: true, color: NAVY, align: "center", fontFace: "Calibri" });
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: x + 0.55, y: 4.02, w: 1.5, h: 0.32, fill: { color: sp.rc }, line: { color: sp.rc }, rectRadius: 0.06 });
    s.addText(sp.risk, { x: x + 0.55, y: 4.02, w: 1.5, h: 0.32, fontSize: 9, bold: true, color: WHITE, align: "center", valign: "middle", fontFace: "Calibri" });
  });
  s.addText("업로드 없이 샘플 이미지로 바로 체험 가능 · Home/About/Detection/Model Performance/Data Analysis 5개 페이지", {
    x: 0.4, y: 4.55, w: 9.3, h: 0.28, fontSize: 10.5, color: SLATE, align: "center", fontFace: "Calibri"
  });
  conclusion(s, "사진을 넣으면 실제 EfficientNetB3 추론으로 위험도·행동 가이드·Grad-CAM을 제공합니다.");
  s.addNotes("7장. 이 장은 말보다 화면입니다. 다섯 단계입니다. 사진을 업로드하거나 준비된 샘플을 누릅니다. AI가 7개 클래스 확률을 예측하고, 위험도를 4단계로 보여주고, 동물·부위·증상에 맞춘 행동 가이드를 주고, Grad-CAM으로 모델이 어디를 봤는지 시각화합니다. 아래 세 샘플은 실제 모델 결과입니다 — 미란/궤양 97% 빠른 진료, 태선화 88% 진료, 정상 72% 정상 안내. 업로드 없이 샘플만 눌러도 바로 체험됩니다.");
}

// ════════════════ SLIDE 8 — 한계와 개선 방향 ════════════════
{
  let s = p.addSlide();
  s.background = { color: NAVY };
  s.addShape(p.shapes.OVAL, { x: 7.6, y: -0.5, w: 3.4, h: 3.4, fill: { color: "1A2D42" }, line: { color: "1A2D42" } });
  s.addText("무엇이 부족하고, 다음은 무엇인가", { x: 0.5, y: 0.25, w: 9, h: 0.7, fontSize: 27, color: WHITE, bold: true, fontFace: "Calibri" });
  s.addShape(p.shapes.RECTANGLE, { x: 0.5, y: 0.95, w: 2.2, h: 0.04, fill: { color: GOLD }, line: { color: GOLD } });
  const cols = [
    { x: 0.4, c: WARN, t: "현재 한계", items: ["정확도 57.6% — 임상 진단엔 부족", "A2↔A3 등 시각적 유사 병변 혼동", "고양이 데이터 부족 (11.4%)", "이미지 단일 입력 (증상·부위 미반영)"] },
    { x: 3.55, c: TEAL2, t: "원인", items: ["학습량·데이터 규모의 한계", "두 병변의 외형 차이가 미세함", "고양이 원본 수집 자체가 적음", "메타정보가 모델 입력에 미반영"] },
    { x: 6.7, c: SUCCESS, t: "개선 방향", items: ["추가 학습·증강으로 성능 향상", "A2·A3 특화 손실 / 부위 정보 활용", "고양이 데이터 보강", "이미지+증상 멀티모달 입력"] },
  ];
  cols.forEach(col => {
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: col.x, y: 1.2, w: 2.85, h: 3.0, fill: { color: "1A2D42" }, line: { color: "2A4060" }, rectRadius: 0.12 });
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: col.x, y: 1.2, w: 2.85, h: 0.5, fill: { color: col.c }, line: { color: col.c }, rectRadius: 0.12 });
    s.addShape(p.shapes.RECTANGLE, { x: col.x, y: 1.45, w: 2.85, h: 0.25, fill: { color: col.c }, line: { color: col.c } });
    s.addText(col.t, { x: col.x + 0.1, y: 1.22, w: 2.65, h: 0.46, fontSize: 13, bold: true, color: WHITE, valign: "middle", fontFace: "Calibri" });
    col.items.forEach((it, i) => {
      s.addText("• " + it, { x: col.x + 0.15, y: 1.85 + i * 0.56, w: 2.6, h: 0.52, fontSize: 10.5, color: "CADCFC", fontFace: "Calibri", lineSpacingMultiple: 1.05 });
    });
  });
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: 0.4, y: 4.4, w: 9.2, h: 0.92, fill: { color: GOLD }, line: { color: GOLD }, rectRadius: 0.1 });
  s.addText([
    { text: "다음 단계:  고양이·A2/A3 데이터 보강  →  멀티모달(이미지+증상)  →  추가 학습  →  임상 검증\n", options: { bold: true, color: NAVY, fontSize: 12.5 } },
    { text: "AI 수의사는 질병을 확정하지 않습니다. 빠른 초기 판단을 도와 보호자의 다음 행동을 안내합니다.", options: { color: "5A4300", fontSize: 10.5 } },
  ], { x: 0.4, y: 4.4, w: 9.2, h: 0.92, align: "center", valign: "middle", fontFace: "Calibri", lineSpacingMultiple: 1.1 });
  s.addNotes("8장. 마지막은 감사 인사 대신 한계와 다음 단계로 마칩니다. 한계는 셋입니다. 정확도 57.6%는 임상 진단으로 쓰기엔 부족하고, A2와 A3처럼 유사한 병변을 혼동하며, 고양이 데이터가 부족하고 이미지만 입력합니다. 원인은 학습량·데이터 한계와 메타정보 미반영입니다. 개선 방향은 데이터 보강, A2·A3 특화 처리, 이미지에 증상을 더한 멀티모달입니다. 다음 단계는 데이터 보강, 멀티모달, 추가 학습, 임상 검증입니다. AI 수의사는 진단을 확정하지 않고, 빠른 초기 판단으로 보호자의 다음 행동을 돕습니다. 이상입니다.");
}

p.writeFile({ fileName: BASE + "/SAG_발표자료.pptx" })
  .then(() => console.log("OK: SAG_발표자료.pptx (8슬라이드) 생성 완료"))
  .catch(e => { console.error("ERR", e); process.exit(1); });
