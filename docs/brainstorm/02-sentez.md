---
title: OSI brainstorm tur 2 sentezi
created: 2026-10-20
modified: 2026-10-20
type: note
status: active
tags: [hackathon, brainstorm]
---
# Tur 2 sentezi (kriter odaklı, Metalliksa yok)

Brief: [01-brief-kriter.md](01-brief-kriter.md). Cevaplar: [Opus](r2-opus-5-5.md), [GPT-6 Astra](r2-codex-gpt6-astra.md), [Gemini 4 Argon](r2-gemini-4-argon.md). Üçü birbirini görmedi. Opus temiz agy örneği, bu sohbetin bağlamı yok.

## Her modelin seçimi

| Model | Seçim | Claude değerlendirmesi |
| --- | --- | --- |
| Opus 5.5 | HiddenHull: frontier agent'lar gizlenmiş DFT kristallerini ne kadar yeniden buluyor, yeni aday çıkarıyor mu | Kriterlere en iyi uyan. Ağır mühendislik, API maliyeti, sızıntı riski. |
| GPT-6 Astra | Gizli auxetic: MP elastik tensörlerinde yönsel negatif Poisson | Büyük ihtimalle yapılmış (Dagdelen ve ark. 2017, Nat. Commun.). Düşür. |
| Gemini 4 Argon | EigenDrop: "kararlı" MP kristallerinde MLIP fononla sanal mod bul, gerçek taban durumunu çıkar | Güçlü keşif hikâyesi. MACE-MP-0 sistematik yumuşama ile sahte sanal mod üretebilir; ikinci MLIP şart. LLM rolü zayıf. Gemini'nin sayıları tahmin. |

## Yakınsama

Üç model ayrı ayrı "agent keşif benchmark'ı" önerdi: Opus #1, Gemini #4 DiscoveryGym, Codex #4. Sitede öne çıkan konuşma da bu konuda. Can'ın eval uzmanlığıyla doğrudan örtüşüyor.

## Önerilen konu

Temel: kapalı havuz geri dönük keşif. WBM (Matbench Discovery) DFT etiketleri gizli, agent'lar sabit bütçeyle aday seçer, random, substitution ve ML surrogate baseline'larına karşı. Etiketler bilindiği için metrik her zaman temiz, MLIP gerekmez.
Genişleme: açık uçlu öneri ve MLIP oracle ile yeni aday listesi (Opus planı).
Ek bulgu: sızıntı ölçümü (model aracsız ne kadar hatırlıyor).
