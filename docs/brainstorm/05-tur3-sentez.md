---
title: OSI tur 3 çapraz değerlendirme sentezi
created: 2026-10-20
modified: 2026-10-20
type: note
status: active
tags: [hackathon, brainstorm]
---
# Tur 3: çapraz değerlendirme ve yeni buluş konuları

Brief: [03-brief-capraz.md](03-brief-capraz.md). Cevaplar: [Opus](r3-opus-5-5.md), [GPT-6 Astra](r3-codex-gpt6-astra.md), [Gemini 4 Argon](r3-gemini-4-argon.md). Web kontrolü: [04-web-kontrol.md](04-web-kontrol.md).

## Sıralama

| Model | Sıra |
| --- | --- |
| GPT-6 Astra | A > E > D > B > C |
| Opus 5.5 | A (~%35) > C > E > B > D |
| Gemini 4 Argon | A > E > C > B > D |

Üçü de A (DataDoctor) birinci. Benchmark (B) üçünde de 4. Web: B'nin neredeyse aynısı MADE (ICML 2026).

## A'nın keskinleştirilmiş hali (üç modelin ortak noktaları)
- Bir veri setinin tutarlı bir dilimi. Görünürlük için matbench_expt_gap, kaynağı olan ikinci set olarak deneysel oluşum entalpisi (Kingsbury) önerildi.
- Bayrak ancak bağımsız sinyaller (MP DFT, farklı ailelerden iki ML modeli, kimyasal aile trendi) uyuşunca.
- Kaynağa git, hata türünü ayır: aktarım, kimlik/polimorf, koşul, çözülemeyen. Belirsizde çekimser kal.
- 30 girişi elle doğrula, precision raporla.
- Etkiyi bayraklamada kullanılmayan bir modelle, dondurulmuş bir test setinde ölç. Döngüsellikten kaçın.
- Çıktı: sürümlü düzeltme defteri, marimo uygulaması.
- Kritik risk: expt_gap'te giriş başına kaynak yok (web ile doğrulandı). Kaynak arama bileşim ile yapılacak, Bond tam metin mi özet mi bilinmiyor.

## Yeni buluş konuları (9 aday)
Opus: N1 GNoME, Alexandria ve MP birleşik hull uzlaştırması. N2 GNoME tahminlerinden kaç tanesi 2024 ile 2026 arasında sentezlendi. N3 COD inorganik yapılarda kimyasal tutarlılık denetimi.
Gemini: SpinGhost (MP'de metal görünen ama deneysel olarak AFM yalıtkan bileşikler). ThermoGhost (termoelektrik veri setlerinde katkılı numunelerin saf diye etiketlenmesi). HydrateTrap (deneysel oluşum entalpisinde yanlış polimorf eşleşmesi).
Codex: JARVIS elastik tensörlerinde negatif lineer sıkıştırılabilirlik. NIST adsorpsiyon verisinde sıcaklıkla sıralama dönmesi. Seyreltik çözünen difüzyonunda kompanzasyon etkisi.
Ortak desen: en güvenilir 34 saatlik buluş türü "herkesin kullandığı veride sistematik hata bulmak".
