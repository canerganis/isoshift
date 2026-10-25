# IsoShift çalışma rehberi

- Kullanıcıyla Türkçe konuş; bilimsel çıktı ve ürün dilini mevcut belgeyle tutarlı koru. Bu repo kökünde çalış; önce `git status --short` ve `git log -1` kontrol et. Kullanıcı değişikliklerini ve çalışan işleri koru.
- İlk rota: `START.md`, `DECISION.md`, `state/LEDGER.md`, sonra yalnız ilgili güncel `docs/decisions/` ve `docs/specs/` belgesi. Eski etkinlik saatlerini veya ledger ilerleme satırını bugünün görevi olarak yeniden başlatma.
- P12/PIMD için `docs/predictions/P12_pimd.md`, ilgili `docs/specs/pimd-p12*.md`, `docs/specs/p12-score.md` ve güncel sonuç JSON'larını kontrol et. `status: complete` ancak beklenen noktalar/kimlikler/ölçütler de tam ise geçerlidir.
- Tek repo/GPU yazıcısı kullan; başka kuyruğu veya pool worker'ı otomatik başlatma. GPU üretim yöntemi, bead/chunk veya kabul kapısı değişikliği güncel onaylı amendment gerektirir. Ortam/method değerini hafızadan tahmin etme.
- Başarısız prospective test başarısız kalır. Sentetik test yazılım davranışını sınar; deneysel veya fiziksel validasyon yerine geçmez. Nitel önceki çalışmayla nicel katkıyı ayır; belirsizlik ve geçerlilik sınırlarını koru.
- `.env` ve anahtarları okuma/çıktıya basma/commit etme. Submission, yayın, dış mesaj ve public görünürlük değişikliği açık kullanıcı yetkisi ister.

## Ortam ve doğrulama

- Mevcut `.venv` ana bilimsel ortamdır; `.venv-sevenn` farklı potansiyeller içindir. Çalıştırılacak yorumlayıcıyı görevin bağımlılıklarına göre seç; sistem Python'una paket kurarak ortamı sessizce değiştirme.
- CPU-only P12 karar testi: repo kökünde PowerShell `& '.\.venv\Scripts\python.exe' -B -m pytest tests/test_p12_score.py -q`.
- Pair curation için `tests/test_pairs.py`; pool ve GPU testleri için önce ilgili test dosyasını ve kaynağın ortam gereksinimini oku. Tüm suite'in CPU-only olduğunu varsayma.
- Kod değişikliğinde dar regression testi ve ilgili sayısal sözleşmeyi doğrula; mümkünse önce hatayı göster. Belge değişikliğinde içerik, kaynak/yol ve diff kontrolü yeterlidir. Production/GPU sweep bu rehber değişikliğinin kabul testi değildir.
- Tamamlanma: gerçek sonuç/exit ve PASS/FAIL/SKIP ayrımı, açık kalan nokta, yalnız kendi değişikliklerini içeren yerel commit. Push ayrıca yetki ister.
