# IsoShift

- Bu repo kökünde `git status --short`, `git log -1`, `START.md`, `DECISION.md`, `state/LEDGER.md` ve yalnız ilgili güncel spec/kararı oku. Eski etkinlik saatlerini yeni görev sayma.
- P12: `docs/predictions/P12_pimd.md`, `docs/specs/pimd-p12*.md`, `docs/specs/p12-score.md` ve güncel sonuç JSON'larını eşleştir. `complete` etiketi beklenen nokta/kimlik/ölçütler tamam olmadan başarı değildir.
- Tek repo/GPU yazıcısı; çalışan kuyruk/pool'u yeniden başlatma. Üretim yöntemi, bead/chunk veya kabul kapısı değişikliği onaylı amendment gerektirir. `.venv` ve `.venv-sevenn` ortamlarını karıştırma.
- CPU kontrolü: `& '.\.venv\Scripts\python.exe' -B -m pytest tests/test_p12_score.py -q`. İlgili regression/sayısal kontrolü seç; belge işi için içerik/yol/diff yeterli. GPU/production sweep başlatma.
- Başarısız prospective test başarısız kalır; sentetik kontrol deneysel validasyon değildir. Önceki nitel çalışma ile nicel katkıyı ayır; kaynak, birim ve belirsizliği koru.
- Sırları ve kullanıcı değişikliklerini koru. Yalnız kendi farkını yerel commit et; push, submission, public görünürlük ve dış mesaj ayrıca yetki ister. Sonuç, doğrulama ve kalan işi kısa bildir.
