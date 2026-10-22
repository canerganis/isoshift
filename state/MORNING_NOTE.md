# Sabah notu (Can için, 22 Ekim)

## Durum: hesap bitti, sayılar dondu, metinler hazır
- GPU işleri tamam: 4 model (MACE, ORB, MatterSim, SevenNet), 220 çift. Freeze yapıldı, sayılar konsey 07 kararıyla yazıldı.
- Başlık bulgusu (F01): H-bağı orta/güçlü olduğunda döteryum O-H bağı kısa olan polimorfu tercih ediyor: 212 değerlendirmede 185 doğru (baz çizgi 131). 10 çift ters çıktı, hepsi tek bir Al(OH)3 yapısını (mp-985293) içeriyor; bunu açıkça yazdık, çıkarmadık.
- Deneyle karşılaştırmalar: gerilme frekansı ölçülmüş spektrumla uyumlu (F03); bir çiftte spektroskopi işareti tutuyor (F04); mineral D/H fraksiyonlanmasında sıra doğru, büyüklük 5 ile 10 kat fazla (F05); bağımsız yeniden yazım 1e-9 ile aynı sonuç (F06); buz Ih sınırlarında tahmin tutmadı, II-III tuttu (F07). Hepsi önceden commit edilmiş tahminlerle.
- Somut tahmin: döteryum diaspor -> delta-AlOOH sınırını yukarı itiyor, 1000 K civarında +0.7 ile +0.9 GPa (3 model). Test eden deney yazılı.
- DFT benchmark 4 model: izotop ZPE hatası 0.7 ile 1.5 meV.

## Hazır olanlar
- Tek sayfalık özet: docs/story/writeup.md (549 kelime). Uzun hali writeup_long.md.
- Başlık figürü: figures/fig_headline.png.
- Video senaryosu v3: docs/story/video_script.md (458 kelime, ~3:40), Türkçe okuma taslağı içinde.
- marimo uygulaması: F01, Check a pair, How we know, Benchmark sekmeleri. Çalıştırma: `.venv/Scripts/python.exe -m marimo run app/isoshift_app.py`
- Kanıt dizini: docs/INDEX.md. Kararlar: docs/decisions/00 ile 07.

## Senden lazım olanlar (sırayla)
1. Moment'e giriş yap, formun alanlarını ve metin uzunluk sınırını kontrol et; bana sınırı söyle, özeti ona göre kırparım.
2. Repo public onayı: onay verince gizli bilgi taramasını yapıp public yapacağım (github.com/canerganis/isoshift).
3. Prova (senaryo + uygulama + figür), sonra OBS ile çekim; YouTube'a Public yükleme. İstersen slaytları ve altyazı (SRT) dosyasını öğleden önce hazırlarım.
4. Moment teslim: video linki, özet + figür, repo linki, Valency Bond ve marimo kutuları, öncesi/sonrası açıklaması (README'de hazır).
