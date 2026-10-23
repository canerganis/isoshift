**Physical Review Materials için önerim: major revision (esaslı düzeltme).** Ana sayımlar ve eğimler depo verileriyle uyuşuyor. Ancak bunların fiziksel olarak güvenilir ve yeni bileşiklere aktarılabilir bir polimorf kararlılığı kuralı oluşturduğu henüz gösterilmiş değil.

İncelenen sürüm: `post-hackathon`, commit `4411a8139fbba16a0fe07c69046a5c151d065037`, [main.tex](C:/Users/can02/Projects/osi-hackathon-2026/docs/paper/main.tex). Geçici çalışma klasörü boş olduğundan, bu dalı taşıyan `C:\Users\can02\Projects\osi-hackathon-2026` deposunu kullandım. Makaleyi, ilgili kodları, sonuç tablolarını, F01–F12 içindeki ilgili bulguları, M02–M03 türetimlerini, karar kayıtlarını ve dört şekli inceledim. CSV üzerinden temel hesapları bağımsız JavaScript hesaplarıyla yeniden yaptım; fononları veya GPU hesaplarını yeniden çalıştırmadım. Hiçbir dosyayı değiştirmedim.

**1. İddiaların özeti**

Makale, hidrojen içeren inorganik polimorflar arasında tam H→D değişiminin titreşimsel serbest enerji farkına etkisini, statik enerji farkını gideren bir çift fark üzerinden inceliyor. Üç makine öğrenmesi potansiyelinin 220 çift üzerindeki harmonik hesapları, ortalama X–H bağ uzunluğu farkıyla izotop çift farkı arasında 300 K’de yaklaşık 0,11–0,13 meV/H/mÅ eğimli bir ilişki veriyor. Sonradan seçilen \(r_{\max}\geq0{,}99\) Å ve \(|\Delta d|\geq5\) mÅ koşullarında, döteryumun daha kısa O–H bağlarına sahip polimorfu tercih etmesi 212 değerlendirmenin 185’inde sağlanıyor. Mod ayrıştırması, gerilme katkısının bükülme ve librasyon tarafından yaklaşık yarı yarıya dengelendiğini; bir Al(OH)₃ yapısında bu dengenin işareti tersine çevirebildiğini gösteriyor. Kural zayıf hidrojen bağlarında ve önceden belirlenmiş prospektif testin başarı ölçütlerinde başarısız oluyor. Çalışma ayrıca diaspore–δ-AlOOH sınırı için yaklaşık +1 GPa’lık keşif niteliğinde bir izotop kayması öngörüyor ve fraksiyonlaşma deneyleriyle sınanmasını öneriyor.

**2. Sayısal doğrulama**

Aşağıdaki yollar depo köküne göredir. **Eşleşme**, makale ile belirtilen kayıt veya yeniden hesaplama arasındaki tutarlılığı ifade eder; fiziksel doğruluk veya deneysel doğrulama anlamına gelmez. Model sırası, aksi belirtilmedikçe MACE / ORB / MatterSim’dir.

| # | Makaledeki sayı | Kontrol edilen dosya ve sonuç | Karar |
|---|---|---|---|
| 1 | 220 çift, 63 formül | `results/decompose_pairs.csv`, `data/isoshift/pairs.csv`: temiz, kovalent, üç model filtresiyle yeniden sayım **220 / 63** | Eşleşme |
| 2 | 521 değerlendirme: 188 / 163 / 170 | `results/decompose_pairs.csv`: bağımsız yeniden sayım aynı | Eşleşme |
| 3 | Toplam eğimler 0,112 / 0,117 / 0,128 | Aynı CSV’den OLS: **0,1120969 / 0,1173128 / 0,1275862** meV/H/mÅ | Eşleşme |
| 4 | Pearson \(r=0{,}76/0{,}83/0{,}84\) | Aynı CSV’den **0,761843 / 0,828539 / 0,835658** | Eşleşme |
| 5 | Gerilme eğimleri +0,245 / +0,259 / +0,252 | Aynı CSV’den **0,245160 / 0,258817 / 0,251667** | Eşleşme |
| 6 | Dik katkı eğimleri −0,133 / −0,142 / −0,124 | Aynı CSV’den **−0,133064 / −0,141505 / −0,124081** | Eşleşme |
| 7 | Güçlü rejim toplam eğimleri 0,132 / 0,136 / 0,147 | `results/F01_cv.json`, `oh_strong_slopes`: **0,1318 / 0,1364 / 0,1471** | Eşleşme |
| 8 | Güçlü rejimde 97 / 97 / 99 fit satırı | Aynı JSON: **97 / 97 / 99** | Eşleşme |
| 9 | 185/212 doğru | `decompose_pairs.csv`, `decompose_structures.csv`, `stretch_check.csv` ile kodun uygunluk tanımı yeniden uygulandı: **185/212** | Eşleşme |
| 10 | Sabit işaret baseline’ı 131/212 | Aynı CSV’lerden, formül dışarıda bırakılarak eğitim katındaki çoğunluk işareti yeniden hesaplandı: **131** | Eşleşme |
| 11 | 84 çift, 28 formül | `results/F01_cv.json`, `oh_unfiltered_strong`: **84 / 28** | Eşleşme |
| 12 | Çift çoğunluğu: 74 doğru, 10 yanlış, sıfır beraberlik | CSV’den yeniden hesaplama aynı; yanlış 10 çiftin tamamı `mp-985293` içeriyor | Eşleşme |
| 13 | Model bazında 52/68, 64/73, 69/71 | `results/F01_cv.json`, `oh_unfiltered_strong.per_model` | Eşleşme |
| 14 | Zayıf rejimde 2/20; 13 çift, 7 formül | CSV’den bağımsız yeniden sayım **2/20, 13, 7** | Eşleşme |
| 15 | Nested CV: 183/210, baseline 131; 30 katmanda 1,00 Å | `results/F01_cv.json`, `nested_threshold_cv.OH_no_cut`: aynı; toplam **31** katman | Eşleşme |
| 16 | Al(OH)₃ dışarıda bırakılan katmanda 8/28; baseline 19 | Aynı JSON’un ilgili katmanı | Eşleşme |
| 17 | SevenNet 10/10; dört model toplamı 195/222 | `results/F01_cv.json`, `sevenn_sign_votes` | Eşleşme |
| 18 | 0/300/600 K’de 153/185/210 doğru | `results/post_freeze/F09_temperature.json`, `headline_accuracy_decompose` | Eşleşme |
| 19 | 600 K’de 190/212 satır temiz | Aynı JSON, `600K.rows_clean_at_T`: **190** | Eşleşme |
| 20 | H1: 98/212; medyan \(C=0{,}665/0{,}582/0{,}406\) | Aynı JSON, `H1`: tam eşleşme; kayıtlı sonuç **başarısız** | Eşleşme |
| 21 | Teller–Redlich sapması \(2{,}6\times10^{-11}\)/H | Aynı JSON, `H3.max_dev_per_H`: **\(2{,}57787865\times10^{-11}\)** | Eşleşme |
| 22 | 2000 K iz işareti testi 211/212 | Aynı JSON, `H4.n_agree`: **211** | Eşleşme |
| 23 | Libowitzky oranları 0,91 / 0,92 / 0,92 | `results/stretch_check_summary.json`, ana pencere: **0,912 / 0,922 / 0,919** | Eşleşme |
| 24 | Bu oranların %95 aralıkları 0,67–1,07; 0,82–1,01; 0,81–1,02 | Aynı JSON: **[0,668;1,071], [0,821;1,009], [0,811;1,015]** | Eşleşme |
| 25 | DFT’ye karşı ZPE MAE: 1,5 / 0,7 / 1,3 meV/H | `results/benchmark/summary.csv`, `a_dftstruct`: **1,48355 / 0,67130 / 1,34976** | Eşleşme |
| 26 | AlOOH basınç kaymaları +1,33 / +1,13 GPa | `results/card_alooh_pressure.json`: **+1,333 / +1,130**; H sınırları **8,760 / 13,001 GPa** | Eşleşme |
| 27 | Yeniden kurulan 300 K kaymaları +1,33 / +1,13 / +0,99 GPa | `results/card_alooh_temperature.json`: **1,328 / 1,125 / 0,990** | Eşleşme |
| 28 | Prospektif test: 16/111; 87 kayıp; 24 temiz | `results/post_freeze/F11_prospective.json`: **16 doğru; 69 başarısız/kararsız + 18 temiz olmayan; 24 temiz** | Eşleşme |
| 29 | Temiz prospektif satırlarda 16 doğru; sabit ters işaret 19 | `docs/findings/F11-prospective-test.md`: **16/24**, önceden belirlenen baseline **5/24**, sonradan seçilen ters işaret **19/24** | Eşleşme; baseline ayrımı önemli |
| 30 | Boehmite–diaspore, 380 °C’de +28,8‰ | `docs/findings/F12-boehmite-diaspore.md`: **−49,9−(−78,7)=+28,8‰** | Eşleşme; ikincil kaynağın aktarımı |
| 31 | \(\rho=1{,}373607\), katsayı 0,016861 | `docs/math/M03_check.py` içindeki kütle ve sabitlerle bağımsız hesap: **1,373607306**, **0,016861225** | Eşleşme |
| 32 | \(1/\sqrt2\) kullanımı “her kaymayı %7” fazla verir | Aynı M03 formülleriyle sıfır-sıcaklık farkı **%7,685**; yüksek-sıcaklık eğim farkı **%6,383** | **Uyuşmazlık:** sabit %7 genellemesi doğru değil |
| 33 | Yeniden uygulama 9/9 işaret, \(10^{-9}\) meV/atom uyum | `results/replicate_f01.json`: 9/9; maksimum fark **\(1{,}0169\times10^{-9}\)** | Yaklaşık değer olarak eşleşme; kesin üst sınır olarak değil |

**Önemli dosya tutarsızlığı:** `results/F01_rule_fit.json` hâlâ eski **177/121/43** satır sayıları ve **0,1163/0,1203/0,1471** eğimlerini içeriyor. Makaledeki güncel eğimler CSV’den doğrulanıyor; dolayısıyla bu durum makalenin eğimlerinin yanlış olduğunu göstermiyor. Ancak eski JSON açıkça arşivlenmeli veya “superseded” olarak işaretlenmeli; mevcut adıyla okuyucuyu yanlış sonuca götürüyor.

**3. Başlıca bilimsel sorunlar**

**A. “Clean” ölçütü fiziksel olarak tanımlı harmonik serbest enerji için yeterli değil.**

[main.tex:83](C:/Users/can02/Projects/osi-hackathon-2026/docs/paper/main.tex:83) bu sınırlamayı dürüstçe açıklıyor; fakat açıklamak sorunu çözmüyor. `decompose.py` sanal frekansları mutlak değere çevirirken doğrudan hesap düşük frekansları çıkarıyor. İki düzenlenmiş hesabın uyuşması, kararsız bir yapının harmonik bölüşüm fonksiyonunu fiziksel olarak geçerli kılmaz.

Ana 212 satırı `screen_pairs_refined.csv` ile birleştirdiğimde **161 satırda `soft_mode_bracketed`, 103 satırda `relax_not_converged`** bayrağı bulunuyor. Bunlar saklanmış bayraklardır; her birinin son hesapta devam eden fiziksel kararsızlığı temsil ettiğini varsaymıyorum. Tam da bu nedenle, güncel hesap durumunu gösteren bir denetim gerekli.

**İstenen kontrol:** Her ana yapı için son kuvvet, gerilme, minimum frekans, sanal modların konumu ve özvektörü verilmelidir. Yakınsamış ve dinamik olarak kararlı altkümede eğim, başarı, baseline ve kapsam yeniden raporlanmalıdır. Sorunlu yapılar silinmemeli; ayrı tabloda korunmalı ve gerekiyorsa yumuşak mod boyunca minimum aranmalı veya anharmonik serbest enerji kullanılmalıdır.

**B. MLIP doğrulaması hedef gözlenebiliri doğrulamıyor.**

Statik enerjinin çift farkta iptali doğru ve yararlı. Ancak kuvvet sabiti ve geometri hatalarının da iptal olduğunu göstermez. Üç modelin ortak eğitim kökeni nedeniyle aynı işareti vermesi bağımsız bir fizik doğrulaması değildir; makale bunu zaten kabul ediyor.

Daha önemlisi, karşılaştırma yalnız tek-yapı izotop farklarını değerlendiriyor. `benchmark/summary.csv` içinde 40 DFT kaydının **22’sinde**, DFT geometrisindeki MACE/ORB/MatterSim sonuçlarının sırasıyla **17/26/16’sında** sanal mod kaydı var. Ayrıca modelle gevşetilmiş geometrilerde ZPE MAE, MACE için **1,91**, ORB için **1,42 meV/H** oluyor; bunlar ana metindeki DFT-geometrisi değerlerinden belirgin biçimde büyük.

**İstenen kontrol:** Güçlü/zayıf rejimleri, sınır çevresini ve `mp-985293` istisnasını içeren önceden seçilmiş bir çift kümesinde doğrudan DFT \(\Delta\Delta F\) hesaplanmalıdır. Ortak geometri ve ayrı gevşetilmiş geometri karşılaştırmaları, geometri hatasını kuvvet sabiti hatasından ayırmalıdır. Özellikle sıfıra yakın işaretler için model aralığı yerine hedef gözlenebilir üzerinde hata değerlendirmesi gerekir.

**C. Anharmoniklik, küçük bir düzeltme olarak ele alınamaz.**

F05’in büyüklük hataları, F07’nin yanlış işaretleri ve δ-AlOOH’nin proton düzensizliği, eksik fiziğin tam da iddianın merkezindeki sistemlerde önemli olabileceğini gösteriyor. Bunlar bütün güçlü-rejim sonuçlarını otomatik olarak çürütmez; fakat genel bir işaret kuralını yalnız harmonik iç tutarlılıkla savunmayı engeller.

Eksik olan özellikle yakın bir çalışma, harmonik O–H modellerinin izotop fraksiyonlaşmasını fazla tahmin edebildiğini ve gerilme ile diğer hareketler arasındaki dengelemenin anharmoniklik ve sıcaklığa duyarlı olduğunu gösteriyor: [Markland ve Berne, PNAS 109, 7988–7991 (2012)](https://www.columbia.edu/cu/chemistry/groups/berne/papers/pnas_109_7988_7991_2012.pdf).

**İstenen kontrol:** Temsilî birkaç çiftte kütle integrasyonu kullanan yol-integrali hesabı veya gerekçelendirilmiş başka bir anharmonik yöntem uygulanmalıdır. Aynı potansiyelde harmonik–anharmonik fark, ardından elektronik yapı/potansiyel farkı ayrılmalıdır. Bu yapılmadan “gerçek kristaller için kural” yerine “incelenen harmonik modellerde ilişki” kapsamı korunmalıdır.

**D. Çift çoğunluğu bağımsızlık sorununu çözmüyor; istatistiksel belirsizlik eksik.**

212 değerlendirme bağımsız değil; **84 çift de bağımsız değil**, çünkü aynı yapılar farklı çiftlerde tekrar kullanılıyor. `mp-985293` ile ilişkili 10 başarısızlık bunun açık örneği. İlk üç formül ailesi AlOOH, FeOOH ve Al(OH)₃ birlikte **98/212** satır oluşturuyor.

“Daha muhafazakâr birim” olarak çift çoğunluğu kullanılabilir, fakat bundan bağımsız örneklem sonucu çıkarılmamalı. Ana eğimler için güven aralığı, aile etkisi ve yüksek etkili gözlem analizi verilmemiş.

**İstenen analiz:** Formül bazında kümelenmiş bootstrap; formüllere eşit ağırlık veren başarı; aile dışarıda bırakıldığında eğim değişimi; büyük \(|\Delta d|\) değerlerinin etkisi; yapı paylaşımını koruyan belirsizlik analizi. Üç model arasındaki aralık istatistiksel güven aralığı olarak kullanılmamalıdır.

**E. Post-hoc sınırın etkisi yalnız nested eşik seçimiyle ölçülmüş değil.**

Nested CV’nin **183/210** sonucu, yalnız seçilen eşik değerinin yeniden seçilmesini denetliyor. Rejim değişkeni, 5 mÅ kesmesi, pencere, kimyasal kapsam ve sayısal uygunluk tanımı aynı geliştirme geçmişinden geliyor. Makale bu ayrımı açıklıyor; buna rağmen [main.tex:273](C:/Users/can02/Projects/osi-hackathon-2026/docs/paper/main.tex:273) içindeki seçim etkisinin küçük olduğu ifadesi daha dar kurulmalı.

Ayrıca eşik her katmanda değerlendirilen kapsamı değiştiriyor. **183/210 ile 185/212 yalnız doğruluk üzerinden karşılaştırılamaz.**

**İstenen analiz:** Eşik boyunca doğruluk–kapsam eğrisi, formül bazında sonuçlar ve dışarıda kalan örneklerin dağılımı. “Zayıf bağlarda evrensel başarısızlık sınırı” yerine, mevcut model geometrileriyle tanımlanmış ampirik bölge denmelidir. Yeni eşikler prospektif başarısızlık görüldükten sonra doğrulanmış sayılmamalıdır.

**F. Baseline doğru hesaplanmış, fakat bilimsel olarak zayıf ve yön konvansiyonuna bağlı.**

131/212 sayısını yeniden ürettim. Yine de sabit işaretin anlamı, \(a,b\) sıralamasının nasıl belirlendiğine bağlıdır; kodda bunun kaynak enerji sırasıyla bağlantısı var. Bu sıralama makalede açıkça tanımlanmalıdır.

O–H ve O···O göstergelerinin mevcut karşılaştırması da aynı örneklem üzerinde değil: O···O sonucu hedef büyüklüğüne kesme uyguluyor. Dolayısıyla **185/212 ile 187/241**, tek başına bir göstergenin daha iyi olduğunu kanıtlamaz.

**İstenen kontrol:** Aynı uygun çiftlerde kaynak enerji sırası, yoğunluk/hacim farkı, O···O farkı ve basit O–H regresyonuyla karşılaştırma; bütün ayarlar eğitim katında seçilmelidir. Serbest kesişimli fitin katsayıları ve çift yönünü ters çevirme kontrolü de verilmelidir.

**G. Prospektif test makalenin sonuç dilinde daha belirleyici olmalı.**

F11’in başarısızlığını saklamamak önemli bir güçlü yön. Ancak **16/111**, fiziksel işaret tahmininin saf doğruluğu değildir: 87 hesap kaybını da yanlış sayan önceden tanımlı bir iş akışı başarı ölçütüdür. Öte yandan temiz 24 satırdaki **16 doğru**, aktarılabilirliği güvenceye almaz.

Burada ters yönde aşırı yorumdan da kaçınılmalı: **19/24**, sonuçlar görüldükten sonra seçilen ters sabit işarettir. Kuralın önceden belirlenen baseline’ı yenemediğinin kanıtı olarak kullanılamaz; o baseline **5/24** idi. Doğru sonuç, toplam prospektif kriterlerin karşılanmadığı ve temiz altkümede üstünlüğün sağlam biçimde gösterilemediğidir.

**İstenen analiz:** Kapsam/başarılı hesap oranı, koşullu işaret doğruluğu ve çift/formül düzeyindeki sonuçlar ayrı verilmelidir. Geliştirme kümesi ile prospektif kümenin aynı fiziksel ve sayısal uygunluk kuralları altında karşılaştırılması gerekir. Donmuş hackathon başlığını koruma kararı, makalenin genel sonucunu yeni kanıttan bağımsız tutmak için gerekçe olamaz.

**H. Analitik eğim hesabı yararlı bir açıklama; bağımsız doğrulama değil.**

M03’ün gerilme eğimi türetimi ve katsayısı doğru. Ancak deneysel girdisi olmayan, **aynı model fononlarından çıkarılmış** \(s=d\nu/dr\) ile yine aynı fononlardan hesaplanmış gerilme katkısını karşılaştırıyor. Bu, mekanistik tutarlılık gösterir; dış doğrulama göstermez. Bükülme eğiminin gözlenen dengelemeden geriye çıkarılması da net eğimi bağımsız biçimde öngörmez.

Ayrıca 0,32–0,33 tahmini O–H modeline aitken karşılaştırılan 0,25–0,31 aralığı farklı popülasyonların eğimlerini birleştiriyor.

**İstenen analiz:** Aynı O–H popülasyonu ve aynı ağırlıklandırmayla karşılaştırma; yerel gerilme ağırlıkları, gerçek izotop frekans oranları ve bağ uzunluğu dağılımları kullanılarak kalan farkın açıklanması. “Nicel doğrulama” yerine “aynı model içinde analitik açıklama” dili kullanılmalıdır.

**I. Libowitzky kontrolü, net işaretin güvenli olduğunu gösteren bir hata sınırı vermiyor.**

Harmonik frekansların deneysel temel frekanslarla karşılaştırılması ve 150–400 cm⁻¹’lik varsayımsal düzeltme açıkça belirtilmiş. Bu iyi. Ancak “işaret ancak 1,9–2,3 oranlarında değişir” sonucu, bükülme katkısının doğru veya sabit kalmasına dayanan koşullu bir duyarlılık hesabıdır. `mp-985293`, zaten net işaretin bu katkıya hassas olduğunu gösteriyor.

`stretch_check.py` içindeki periyodik komşu seçimi ve F03’te kabul edilen açı/periyodiklik sınırlamaları da geometrik kontrolü etkileyebilir.

**İstenen kontrol:** Periyodik donor–akseptör geometrisinin doğrulanması, eşleştirilmiş deneysel geometri/spektrum karşılaştırmaları ve bükülme/librasyon katkısı için ayrı doğrulama. Varsayılan anharmonik düzeltme aralığı bir güven aralığı gibi sunulmamalıdır.

**J. AlOOH öngörüsünün nicel sunumu kanıt düzeyini aşıyor.**

Üç QHA modelinin pozitif kayma vermesi ilginç. Ancak hesaplanan faz dalı, aynı basınç aralığındaki proton düzensizliği ve olası kararsız modlardan etkileniyor. Basınç ızgarası seyrek; MACE’nin H sınırı dışdeğerleme. Sıcaklık dosyasında δ-AlOOH için sanal modlar kaydedilmiş ve hesap bunları çıkarıyor.

**İstenen kontrol:** Her izotopun sınırı çevresinde daha sık basınç noktaları, kararlı faz dalları, EOS/enterpolasyon duyarlılığı ve basınçtaki \(\Delta V\). Proton düzensizliğinin dahil edilmesi veya öngörünün açıkça koşullu tutulması gerekir. Özetteki “yaklaşık 1 GPa yükseltir” cümlesi, ana metindeki “yalnız keşif niteliğinde işaret öngörüsü” ile uyumlu değil.

**K. Seyreltik fraksiyonlaşma ile tam döteryumlama arasındaki köprü tamamlanmamış.**

[main.tex:280](C:/Users/can02/Projects/osi-hackathon-2026/docs/paper/main.tex:280) ve M02, \(R\) düzeltmesini doğru biçimde açık bırakıyor. Tek eşdeğer H sitesi, kolektif titreşimlerde izotoplar arası bağlaşımı ortadan kaldırmaz. Bu nedenle özetteki fraksiyonlaşmanın kuralı “doğrudan” sınayacağı ifadesi koşulsuz kullanılamaz.

**İstenen kontrol:** En az birkaç çiftte tek-D süperhücre hesaplarıyla seyreltik sınır ve tam değişim karşılaştırılmalı; \(R\)’nin işareti ve büyüklüğü sınırlandırılmalıdır. **+359‰**, varsayılan \(\Delta V\) ve \(R=0\) ile koşullu dönüşümdür; bağımsız fraksiyonlaşma öngörüsü değildir.

**L. Yenilik daha dar ve daha güçlü biçimde konumlandırılmalı.**

- McKenzie’nin çalışmaları bağ uzunluğu, gerilme/bükülme katkıları, tünelleme ve izotop fraksiyonlaşması arasındaki ilişkiyi zaten ele alıyor. Dolayısıyla “bağ uzunluğundan izotop tercihinin yönü” tek başına yeni değil. [McKenzie ve diğerleri, 2015](https://arxiv.org/abs/1504.04939).
- Li–Walker–Michaelides, bağ kuvvetine bağlı rekabet eden kuantum etkilerini ve rejim değişimini ortaya koyuyor. Burada yeni olan bunun keşfi değil, polimorf çiftleri üzerindeki nicel kapsamı olabilir. [Li ve diğerleri, 2011](https://pmc.ncbi.nlm.nih.gov/articles/PMC3081025/).
- Bigeleisen–Mayer çerçevesi ve yüksek-sıcaklık kuvvet-sabiti izi yönü yeni değil.
- İzotopomerik polimorfizm literatürü mevcut; kristalleşmede seçilen ürün ile denge serbest enerjisinin değişimi ayrıca ayrılmalı. Örneğin ROY çalışması seçici kristalleşme gösteriyor; bu, tek başına burada hesaplanan denge çift farkının ölçümü değildir. [Falk ve diğerleri, 2018](https://journals.iucr.org/m/issues/2018/05/00/ed5015/).

**Savunulabilir yenilik:** Çok sayıda inorganik polimorf çiftinde, açık başarısızlık örnekleri ve mod ayrıştırmasıyla nicelleştirilmiş model ilişkisi. Bunun yayın değeri var; fakat bağımsız fizik kontrolü ve aktarım başarısı olmadan genel bir malzeme kuralı olduğu söylenemez. Literatür sorgu sayısı da yenilik kanıtının yerine geçmez.

**4. Küçük sorunlar, sunum ve kaynaklar**

- **Başlık kapsamı:** Veri kümesi karbon içermeyen inorganiklerle sınırlı. “Hydrogen-bonded crystals” bütün moleküler kristalleri kapsıyor gibi okunuyor; kapsam başlık veya özette belirtilmeli.
- **Yöntem ayrıntıları:** Kullanılan gerçek \(q\)-ağı formülü, kaydırma, süperhücre boyutları, kuvvet sabiti simetrizasyonu ve akustik toplam kuralı işlemleri açıklanmalı. 160 atom sınırının 9,5 Å hedefiyle çatıştığı durumlar gösterilmeli.
- **Mod notasyonu:** Denklemde \(e\)’nin kütle-ağırlıklı, normalize özvektör olduğu ve toplamın yalnız H atomları üzerinde olduğu açıkça yazılmalı. \(u\) ile \(e\) ayrımı verilmelidir.
- **Sembol çakışması:** \(f\), hem Libowitzky eğim oranı hem analitik dengeleme oranı için kullanılıyor. Dengeleme için \(C\) korunmalı.
- **Birimler:** Hücre, atom, H ve formül birimi normalizasyonları her denklemde tutarlı olmalı. Hacim izotop etkisinin \(V_H/V_D-1\) tanımı ve işaret konvansiyonu açıkça belirtilmeli.
- **Analitik hassasiyet:** “Her kayma %7” düzeltilmeli. \(5\times10^{-5}\) doğruluğun mutlak mı bağıl mı olduğu belirtilmeli; 3000 cm⁻¹, 300 K için parantezin bağıl farkı yaklaşık \(1,47\times10^{-4}\), mutlak farkı \(4,00\times10^{-5}\).
- **Şekiller:** Ana şeklin başlığı rejim koşulunu içermiyor. Üç panelli şeklin açıklaması (a), (b), (c) kullanırken paneller üzerinde bu harfler görünmüyor. SevenNet nicel fit çizgileri, “yalnız işaret oyu” ayrımını görsel olarak zayıflatıyor.
- **Akış şekli:** `fig2_pipeline_counts.png`, makalede kullanılmayan 2 ve 38’lik kalite katmanlarını gösterirken asıl 220 ve 84 çiftlik kümeleri göstermiyor. Makalenin gerçek seçim akışı çizilmeli.
- **Gerekli yeni şekil:** `mp-985293` için toplam/gerilme/dik katkının sıcaklıkla değişimi, eşik–kapsam grafiğinden daha fazla mekanistik bilgi sağlayacaktır. Prospektif başarısızlık da görsel olarak görünür olmalı.
- **F12 karşılaştırması:** Ana metin 300 K tahminlerini 380 °C ölçümü yakınında veriyor. Aynı sıcaklıktaki model değerleri **42,5/30,3/41,3‰** gösterilmeli; ölçümlerin **2 ve 4 kbar** basınç farkı da eklenmeli.
- **Deney kaynakları:** F04 ve F05’te kilit sayılar ikincil kaynaklardan geliyor. Birincil tablo/şekiller görülmeden bunlar sağlam nicel doğrulama olarak kullanılmamalı. F12’nin “inconclusive” kararı korunmalı.
- **Tekrarlanabilirlik:** `.cache/`, `results/raw/` ve MDR girdileri Git dışında. Özet CSV’den sayımın yeniden yapılması ile fonon düzeyinde yeniden üretim farklıdır. Makale sürümüne özgü arşiv, kuvvet sabitleri veya eksiksiz yeniden üretim girdileri, checkpoint kimlikleri ve dosya sağlama toplamları sağlanmalı. M03’ün eski DOI sürümünde olmadığının açıklanması doğru.
- **Metin dengesi:** AI iş akışı ve karar tarihi ana metinde uzun yer kaplıyor. Bunların çoğu eke taşınıp fiziksel doğrulama ve hata analizine alan açılmalı.

Kaynakçada bulunmayan ve doğrudan tartışılması gereken başlıca çalışmalar:

1. **Thomas E. Markland ve B. J. Berne**, “Unraveling quantum mechanical effects in water using isotopic fractionation,” *Proceedings of the National Academy of Sciences* **109**, 7988–7991 (2012), DOI: [10.1073/pnas.1203365109](https://doi.org/10.1073/pnas.1203365109). Kütle integrasyonu, rekabet eden katkılar ve harmonik model hatası açısından özellikle önemli.
2. **Sofiane Schaack, Etienne Mangaud, Erika Fallacara, Simon Huppert, Philippe Depondt ve Fabio Finocchi**, “When Quantum Fluctuations Meet Structural Instabilities: The Isotope- and Pressure-Induced Phase Transition in the Quantum Paraelectric NaOH,” *Physical Review Letters* **131**, 126101 (2023), DOI: [10.1103/PhysRevLett.131.126101](https://doi.org/10.1103/PhysRevLett.131.126101). Çalışmanın inorganik hidroksit ve zayıf-bağ başarısızlığı bağlamına doğrudan yakın; [yazarların arXiv kaydı](https://arxiv.org/abs/2310.16462) bunu doğruluyor.
3. **Harold C. Urey**, “The thermodynamic properties of isotopic substances,” *Journal of the Chemical Society*, 562–581 (1947), DOI: [10.1039/JR9470000562](https://pubs.rsc.org/en/content/articlelanding/1947/jr/jr9470000562). Bigeleisen–Mayer ile birlikte temel termodinamik çerçeve için.
4. **Qi Liu, John A. Tossell ve Yun Liu**, “On the proper use of the Bigeleisen–Mayer equation and corrections to it in the calculation of isotopic fractionation equilibrium constants,” *Geochimica et Cosmochimica Acta* **74**, 6965–6983 (2010), DOI: [10.1016/j.gca.2010.09.014](https://www.sciencedirect.com/science/article/pii/S0016703710005193). Harmonik frekans–deneysel temel frekans ayrımı için.

Mevcut `Lee2024` kaydı da yayımlanmış sürüme güncellenmeli: **Huiju Lee, Vinay I. Hegde, Chris Wolverton ve Yi Xia**, *Materials Today Physics* **53**, 101688 (2025), DOI: [10.1016/j.mtphys.2025.101688](https://doi.org/10.1016/j.mtphys.2025.101688).

**5. Özet doğru mu?**

**Sayısal olarak büyük ölçüde doğru; çıkarım ve kapsam açısından düzeltme gerekiyor.**

Doğru sunulanlar: eğim aralığı, 185/212, 131 baseline’ı, eşik seçiminin post-hoc olması, ortak istisna yapısı, zayıf rejim başarısızlığı ve prospektif testin başarısızlığı.

Düzeltilmesi gerekenler:

- **“220 çift tarandı”** yerine 220 çiftin analiz edilen temiz kovalent altküme olduğu açıklanmalı.
- 185/212 sonucunun **84 çift/28 formülden**, model bağımlı ve fiziksel kararlılığı garanti etmeyen bir uygunluk tanımıyla geldiği kısaca belirtilmeli.
- **“Prospektif ölçütü kaçırdı”** ifadesi yetersiz: yeni çiftlere aktarımın gösterilmediği açıkça söylenmeli.
- **“Yaklaşık 1 GPa yükseltir”**, koşullu QHA model sonucu olarak nitelenmeli; mevcut kanıt nicel deney öngörüsünü taşımıyor.
- **“Fraksiyonlaşma doğrudan sınar”**, seyreltik–tam değişim düzeltmesi sınırlandırılmasına bağlı olduğu için koşullu yazılmalı.
- “Literatür taramasında bulunamadı” cümlesi yerine somut katkı öne çıkarılmalı.

Az vurgulanan en değerli sonuç, aynı yapı ailesinde gerilme katkısı beklenen işareti korurken toplam izotop tercihinin sıcaklıkla değişebilmesi. Bu, genel “kısa bağ kuralı” iddiasından daha güçlü bir mekanistik çalışma çekirdeği olabilir. Ancak önce sayısal kararlılık ve anharmoniklik kontrolleri gerekir.

**6. Yayın önerisi**

**Physical Review Materials: major revision.** Sayısal kayıtların tutarlılığı, başarısız testlerin açıklığı ve ayrıştırılmış mekanizma çalışmaya değer katıyor. Kabul için en azından fiziksel olarak kararlı altkümenin analizi, doğrudan DFT çift-fark kontrolü, kümelenmiş belirsizlik değerlendirmesi ve prospektif başarısızlığın sonuç diline tam yansıtılması gerekli. Bunlar yalnız metin düzenlemesiyle giderilemez.

**Nature Communications / npj Computational Materials:** Mevcut haliyle ikisi için de **reject**; daha geniş etkiyi taşıyacak bağımsız fizik doğrulaması, güvenilir dış aktarım veya açıkça doğrulanmış yeni bir mekanizma henüz yok.