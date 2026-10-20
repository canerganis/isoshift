# Claude Science danışması (2026-10-20 23:48, Opus 5.5, ayrı oturum "MDRI Hackathon: Ambitious Materials Discovery")

## Ortamı (kendi beyanı)
- Materials Project, Alexandria, JARVIS, OQMD, PubChem gibi kaynaklar ağ izin listesinde; her biri erişim onayı istiyor, MP ayrıca ücretsiz anahtar (Customize > Credentials).
- Bağlı konnektör yok, malzemeye özel skill yok. Faydalı skill'ler: literature-review, pdf-explore, paper-narrative, figure-composer, compute-env-setup.
- Uzak compute yok. Makine 16 çekirdek, 31 GB RAM, GPU görmüyor (RTX 4060'ı compute target olarak kaydedebilir).

## Önerdiği 3 konu
A. Hızlı sodyum iyon iletkenleri: ~2000 kararlı Na bileşiğinde MLIP (MACE/ORB) MD, oda sıcaklığında >1 mS/cm tahmini 5 ila 10 test edilmemiş aday. Doğrulama: NASICON, Na3PS4, Na3SbS4 gibi bilinenler doğru sıralanmalı, iki potansiyel uyuşmalı, literatürde iletken olarak raporlanmamış olmalı. (Kendi seçimi.)
B. Yeni üçlü nitrürler: MatterGen ile kimyasal sistem koşullu üretim, üç MLIP ile gevşetme, dinamik kararlılık, bilinen yapılarla kıyas. Doğrulama: 2019 sonrası keşfedilenleri gizleyip yeniden bulma.
C. Refrakter HEA süneklik haritası: Nb, Ta, Ti, V, Zr, Hf, Mo, W uzayında ~1000 alaşım, yüzey enerjisi / kararsız istifleme hatası enerjisi oranı, >2200 °C erime. Doğrulama: ~20 ölçülmüş alaşımın sünek/gevrek sıralaması. En riskli (MLIP istifleme hatası doğruluğu).

## Karar: Claude Science çekirdekte kullanılmayacak
- Beta, malzeme konnektörü yok, GPU'yu görmüyor; her şeyi Claude Code ve kendi kodumuzla zaten yapabiliyoruz.
- Can'ın Claude kotasını ayrıca harcar; yarın uygulama yazımı için kota korunmalı.
- Jüri açık, tekrar üretilebilir kod istiyor; çekirdeğin bir arayüz içinde kalması dezavantaj.
- Opsiyonel kullanım: literature-review skill'i ile elle doğrulama aşamasında tek tek kaynak kontrolü.
