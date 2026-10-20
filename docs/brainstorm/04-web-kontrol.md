---
title: Finalistler için web özgünlük ve veri kontrolü
created: 2026-10-20
modified: 2026-10-20
type: note
status: active
tags: [hackathon, prior-work]
---
# Web kontrolü (Claude, 2026-10-20)

Snippet ve özet düzeyinde, tam metin okunmadı.

## Agent keşif benchmark'ı: özgünlük düştü
- MADE: Benchmark Environments for Closed-Loop Materials Discovery, ICML 2026. Sınırlı oracle bütçesiyle konveks hull'a göre kararlı bileşik bulma, agent ve sabit pipeline kıyası. Bizim fikrin neredeyse aynısı. https://arxiv.org/abs/2601.20996
- MatLLMSearch (2025): LLM ve evrimsel arama ile kristal keşfi. https://arxiv.org/pdf/2502.20933

## EigenDrop: araç zaten var
- VibroML (2026): MLIP ile sanal mod tarama, özvektör boyunca bozma ve daha düşük enerjili polimorf bulma toolkit'i. https://arxiv.org/pdf/2604.27685
- MACE-MP-0 dinamik kararlılık: %95 gerçek pozitif ama kararsızlarda %73, eğitim verisiyle örtüşme var; MACE-OMAT önerilmiş. https://arxiv.org/pdf/2511.22504
- Sonuç: yöntem yeni değil. MP genelinde katalog ve literatür eşleşmesi hâlâ yeni olabilir, VibroML iş yükünü azaltır.

## Veri doktoru: özgünlük sağlam, kritik veri bulgusu
- Ajanla deneysel veri seti denetimi yapan yayın bulunamadı. En yakını Yang ve ark. 2023 (LLM ile bant aralığı çıkarımı). https://arxiv.org/html/2311.13778v1
- Zhuo expt_gap: 6354 giriş, **giriş başına kaynak yok** (matsci.org forumu, matminer geliştiricileri). Aynı bileşim için çelişen ölçümler çok. https://matsci.org/t/references-for-expt-gap-dataset/3516
- matbench_expt_gap (4604): 0.1 eV'den fazla yayılan grupları atmış, kalanlarda ortalamaya en yakın değeri seçmiş. Yani çelişkiler kanıtla değil istatistikle çözülmüş. https://matbench.materialsproject.org/Leaderboards%20Per-Task/matbench_v0.1_matbench_expt_gap/
- Yang ve ark.: matbench_expt_gap'te MP'de de olan metal olmayanların %17'si MP'de metal etiketli; sıfır gap'ler literatürden değil MP'den gelmiş.
- Yeni açı: "6354 değer, sıfır kaynak. Agent kaynakları geri buldu, çelişkileri kanıtla çözdü." Bond'a bağımlılık artar.

## Literatür çelişki mahkemesi
- Çapraz makale çelişki çözümü yapan ajan bulunamadı. İlgili: SPOT benchmark (makale doğrulama), kaynak izli çıkarım çalışmaları. https://arxiv.org/pdf/2505.11855 , https://arxiv.org/pdf/2510.05142
- Veri doktoruyla birleşebilir: expt_gap'teki çelişen gruplar hazır çelişki listesi.
