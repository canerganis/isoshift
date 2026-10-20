---
title: OSI tur 4 sentez
created: 2026-10-20
modified: 2026-10-20
type: note
status: active
tags: [hackathon, brainstorm]
---
# Tur 4: geniş kapsam ve cesur fikirler

Briefler: [06-brief-genis.md](06-brief-genis.md), [06b-brief-bold.md](06b-brief-bold.md) (cesurluk turu). Cevaplar: r4-* (geniş), r4b-* (cesur), her model için codex, gemini, opus dosyaları. Web kontrolü snippet düzeyinde, tam metin okunmadı. Codex cevapları Türkçe geldi.

## 8 finalist

| Fikir | Kaynak | Özgünlük (kaynak) | Solo 34 s | Veri | Kriter uyumu |
| --- | --- | --- | --- | --- | --- |
| IsoFlip: izotop değişimiyle polimorf taban durumu tersine döner (D2O, 6Li, 10B) | Gemini (r4b) | Açık: inorganik için sistematik tarama bulunamadı. Organik izotopomerik polimorfi var ([ORNL](https://impact.ornl.gov/en/publications/origins-of-isotopomeric-polymorphism/)), mass-substitution eigenvektör etkisi ZIF-8 üzerinde ([arXiv 2602.20907](https://arxiv.org/abs/2602.20907)) | Yüksek (hesap hafif). Sonuç riski: ZPE farkı 5 ila 25 meV/atom, az sayıda gerçek flip çıkabilir. Çift polimorfin ikisinde de fonon gerekir | Kyoto PhononDB, MP fonon | Yenilik ve etki çok güçlü, deney bir D2O sentezi kadar kolay, kimya alakası yüksek |
| HabitZero: lambda2=1 koşulu ile batarya elektrotlarında sıfır gerilmeli faz sınırı | Gemini (r4b) | Kısmen yapılmış: lambda2=1 ve histerezis Li2Mn2O4 için gösterilmiş ([arXiv 2505.22628](https://www.arxiv.org/abs/2505.22628)), hacim değişimi yüksek verimli tarama var ([arXiv 2603.10631](https://arxiv.org/pdf/2603.10631)) ama lambda2 taraması yok | Orta, yazılım basit. Deneysel histerez verisi derlemesi zor | MP Battery Explorer | Etki yüksek (batarya), yenilik orta |
| HyperbolicScout: fonon ve Born yüklerinden IR geçirgenlik tensörü, doğal hiperbolik malzemeler, RRUFF IR ile doğrulama | Gemini (r4) | Kısmen yapılmış: DFPT BEC veritabanı var ([Petretto](https://perso.uclouvain.be/xavier.gonze/wp-content/papercite-data/pdf/petretto2018a.pdf)), JARVIS 5015 metal olmayan IR ([arXiv 1910.01183](https://arxiv.org/pdf/1910.01183)). Hiperbolik tarama yayını bulunamadı. Not: "8000 kristal" iddiası şişkin, BEC kapsamı ~1.5k (MP) ve 5k (JARVIS) | Orta ila yüksek. RRUFF yansıma doğrulaması zor, tek tük örnek | MP, JARVIS, RRUFF | Fizik katkısı güçlü, nanofotonik topluluğu ilgilenir |
| MissingMinerals: DFT veritabanındaki hull'a yakın fazlardan henüz tanımlanmamış mineral listesi, zaman bölmeli geri test | Opus (r4b) | Kısmen yapılmış: Hazen ve mineral birliktelik modelleri yerleri ve sayıyı tahmin ediyor ([PNAS Nexus](https://pmc.ncbi.nlm.nih.gov/articles/PMC10187660)). Yapı seviyesinde, zaman doğrulamalı tahmin bulunamadı | Orta (%60 temiz liste). IMA ad eşleme zahmetli | IMA/RRUFF, MP, Alexandria | Basın dostu, harita ve liste, jeoloji ve malzeme birleşimi |
| IsoTopo: yalnızca izotop değişimiyle fonon Weyl noktası oluşumu veya yok oluşu | Codex (r4b) | Kısmen: topolojik fonon taraması 5014 aday ([PMC7900202](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7900202/)), grafende izotopla topolojik fonon (APL 2025). Gerçek kristalde izotop kaynaklı geçiş taraması bulunamadı | Yüksek hesap, pozitif sonuç %20 ila 35 | PhononDB kuvvet sabitleri | Yenilik yüksek, deneysel erişim zayıf (anharmonik, karışım saçılması) |
| NextInSpace: 2018 öncesi tespitlerden sonrakileri geri tahmin, rotasyonel sabitli hedef listesi | Opus (r4b) | Kısmen yapılmış: gömme tabanlı sıralama ve tespit edilebilirlik ([arXiv 2608.18221](https://arxiv.org/pdf/2608.18221)). Katı zaman bölmesi bulunamadı ama çok yakın | Orta, xtb 50k aday hafif | CDMS, xtb | Alaka düşük (astrokimya), yenilik orta |
| ChronoCSP: model eğitim tarihinden sonra yayımlanan kristal yapıları dizüstüyle tahmin etme | Opus (r4) | Kısmen: MLIP ile CSP ve kör testler var ([alphaXiv 2605.28905](https://www.alphaxiv.org/abs/2605.28905.md)), eğitim tarihi sonrası inorganik retrospektif bulunamadı | Düşük ila orta, CSP 34 saatte zor | MP, ICSD yerine COD | Etki yüksek, risk yüksek |
| AmorphousLimit at scale: Aykol amorf sınırını 3 ila 5 kat fazla sistemde MLIP ile sınama | Opus (r4) | Büyük ölçüde açık: ML uzantısı bulunamadı, orijinal 41 sistem ([Science Advances 2018](https://pmc.ncbi.nlm.nih.gov/articles/PMC5930398)) | Orta (%60). MLIP hatası 30 meV üzerindeyse çöker | MP, MACE | Doğrudan GNoME adayı filtresi, etki iyi |

Ele alınan ama ilk 8 dışında kalanlar: Hidrojen kinetik ikizleri (Codex, %8), XRD ikizleri (%6), CrysRUM, AtropoScope, AntiHammond, WignerLaw, AlchemGrad, VacuumLatch (Casimir çift kararlılık, Codex), InvariantFuzz.

## Cesurluk turunda modellerin "wow" cevapları
- Gemini: IsoFlip. "D2O'da kristallendirince farklı yapı", Born-Oppenheimer kuvvet sabitleri kütleden bağımsız olduğu için kesin teoremle sıfır ML yaklaşımı. Tamamlama %75 ila 85, en az üç ambient çift %35 ila 45. Kendi birincilik tahmini %38 (öznel, şişkin).
- Codex: IsoTopo. Kimyayı değiştirmeden topolojik durum. Tarama bitirme %80, yeni ve dayanıklı pozitif %20 ila 35.
- Opus: MissingMinerals. Adlandırılmış, test edilebilir mineral listesi ve harita. Zaman bölmesi recall'ı %75, temiz liste %60, recall >%20 top %1'de yalnızca %35.
- Geniş tur wow cevapları: Gemini HyperbolicScout, Opus AmorphousLimit at scale (%60), Codex kinetik ikizler.

## Gözlem
Üç modelin cesurluk turunda iki ayrı model (Gemini, Codex) izotop temelli fikri seçti. Ortak çekirdek: PhononDB kuvvet sabitleri ile kütle matrisi yeniden diagonalizasyonu, GPU gerektirmez. IsoFlip ve IsoTopo aynı altyapıyı paylaşıyor, tek hat iki sonuç verebilir (serbest enerji ve topoloji).
