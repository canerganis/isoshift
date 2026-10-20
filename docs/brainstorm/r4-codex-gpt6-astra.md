Aşağıdaki yenilik iddiaları **literatür taramasıyla doğrulanmış değil**. Yüzdeler de rakipleri bilmeden verdiğim öznel birincilik tahminleri. Her plan, teslim hazırlığı dahil 34 saat; hesaplanan bulguyu deneysel keşif olarak sunmamak temel sınır.

### 1. XRD İkizleri: Farklı kristallerin ayırt edilemediği koşulları kanıtla

**Adımlar:** ① Açık yapılardan aynı bileşimli polimorfları seç, 4 saat. ② Toz desenlerini üret; genişleme, tercihli yönelim ve gürültüyü modelle, 6 saat. ③ Benzer çiftleri bul ve hangi ölçüm koşullarında ayrılabildiklerini hesapla, 10 saat. ④ İkinci hesaplayıcıyla doğrula, 8 saat. ⑤ Demo ve teslim, 6 saat.

**Veri ve araçlar:** COD, pymatgen, Gemmi, SciPy. Başlangıçta birkaç bin inorganik yapı yeterli.

**Sert sonuç:** Yapısal olarak farklı fakat belirtilen cihaz çözünürlüğünde istatistiksel olarak ayırt edilemeyen çiftler; her çift için gerekli çözünürlük veya ek ölçüm önerisi. Jüri CIF dosyalarından sonucu yeniden üretebilir.

**Yenilik:** Homometri ve toz kırınımının tekillik sorunları biliniyor. Önerilen katkı, gerçek kristaller üzerinde ölçüm koşullarına bağlı, yeniden üretilebilir bir ayırt edilebilirlik atlası.

**Doğrulama:** Eşdeğer hücreleri ve yinelenen yapıları ele; ikinci simülatör kullan; farklı gürültü ve genişleme modellerinde sonucu koru. Simülasyon benzerliği deneysel özdeşlik değildir.

**Risk:** Bulunan çiftler yalnızca kötü cihaz koşullarında benzer çıkar veya bilinen örneklerden oluşur.

**Birincilik:** %6.

### 2. Hidrojenin Kinetik İkizleri: Aynı deneyleri açıklayan iki mekanizma, farklı gelecek

**Adımlar:** ① Küçük bir hidrojen yanma mekanizması ve açık deney serisi seç, 4 saat. ② Duyarlı birkaç reaksiyon hızını belirle, 6 saat. ③ Deneyleri aynı hata sınırında açıklayan iki parametre kümesini ara, 10 saat. ④ Ayrışmayı bağımsız koşullarda sınayıp en ayırt edici deneyi seç, 8 saat. ⑤ Teslim, 6 saat.

**Veri ve araçlar:** Cantera’nın `h2o2.yaml` mekanizması, ReSpecTh açık yanma verileri, SciPy.

**Sert sonuç:** Aynı tutuşma gecikmelerini açıklayan, fakat başka bir sıcaklık veya basınçta belirgin biçimde ayrışan iki açık mekanizma dosyası. Yanlarında bu belirsizliği en ucuza azaltacak ölçüm koşulu.

**Yenilik:** Kinetik belirsizlik, özdeşlenebilirlik ve deney tasarımı yerleşik alanlar. Katkı, belirli gerçek veri üzerinde açık bir karşıörnek ve bağımsız verilerle sınanmış ayrıştırma önerisi.

**Doğrulama:** Ters hızları termodinamik tutarlılıkla hesapla; parametreleri gerekçeli sınırlarla kısıtla; kullanılmayan deneyleri sakla; çözücü toleranslarını daralt.

**Risk:** Büyük ayrışma yalnızca deneylerin çok dışındaki koşullarda veya fiziksel açıdan savunulamaz hızlarla bulunur.

**Birincilik:** %8.

### 3. Kaç Mesaj Yeter? Moleküler grafik modellerine hesaplanabilir hata tabanı

**Adımlar:** ① QM9’u ve hedef özellikleri hazırla, 4 saat. ② Farklı mesajlaşma derinliklerinde ayırt edilemeyen grafik sınıflarını çıkar, 6 saat. ③ Her sınıfın hedef farklarından zorunlu hata tabanını hesapla, 10 saat. ④ Grafik eşitliğini ve karşıörnekleri bağımsız doğrula, 8 saat. ⑤ Teslim, 6 saat.

**Veri ve araçlar:** QM9; gerekirse Alchemy; RDKit, NetworkX, PyTorch Geometric.

**Sert sonuç:** Belirtilen atom ve bağ özelliklerini kullanan, belirli derinlikteki standart mesajlaşmalı modeller için veri üzerindeki minimum mümkün hata. Yanında özelliği farklı ama modelin ayıramayacağı gerçek molekül çiftleri.

**Yenilik:** Weisfeiler–Lehman sınırları ve GNN ifade gücü zaten biliniyor. Katkı, kimyasal hedeflere göre sayısal hata sertifikası ve derinliğin sağladığı kazanımın açık haritası.

**Doğrulama:** Hash çakışmasını gerçek yapısal eşdeğerlikten ayır; toplam yüklere, stereokimyaya ve hidrojen gösterimine dikkat et. İddia yalnızca tanımlanan model sınıfına uygulanır.

**Risk:** İki veya üç katmandan sonra anlamlı çakışma kalmaz. Bu da yararlı bir sınır sonucu olabilir; tek başına güçlü yayın garantisi değildir.

**Birincilik:** %4.

### 4. Aynı Malzeme, Farklı Sıra: Cam kaplamalarında sağlam optimumu bul

**Adımlar:** ① Optik sabitleri ve tasarım uzayını sabitle, 4 saat. ② Altı SiO₂ ve altı TiO₂ tabakasının 924 sıralamasını hesapla, 6 saat. ③ Görünür geçirgenlik kısıtı altında yakın kızılötesi yansımayı karşılaştır, 10 saat. ④ Kalınlık hatası ve geliş açısıyla optimumun dayanıklılığını sına, 8 saat. ⑤ Teslim, 6 saat.

**Veri ve araçlar:** refractiveindex.info, açık ASTM G173 güneş spektrumu, `tmm`, NumPy.

**Sert sonuç:** Sabit malzeme miktarı, tabaka kalınlıkları ve altlık için bütün sıralamaların performans haritası. İdeal koşullarda kazananın üretim toleranslarında kaybedip kaybetmediği ve en sağlam alternatif.

**Yenilik:** Çok katmanlı filtre tasarımı ve sağlam optimizasyon yeni değil. Değer, küçük fakat tamamen taranmış bir uzayda açık optimum sertifikası ve varsa şaşırtıcı sıralama değişimi.

**Doğrulama:** Bağımsız transfer matrisi hesabı, enerji korunumu, farklı optik sabit kaynakları, açı ve polarizasyon taraması.

**Risk:** Kazanç küçük kalır veya sonuç standart Bragg tasarımının yeniden bulunması olur. En güvenilir teslimlerden biri, yenilik bakımından en zayıflardan biri.

**Birincilik:** %2.

### 5. Tek Konformer Yanılsaması: Molekül içi hidrojen bağı gerçekten baskın mı?

**Adımlar:** ① GEOM’dan yönetilebilir bir molekül altkümesi seç, 4 saat. ② Konformerlerde molekül içi hidrojen bağlarını çıkar, 6 saat. ③ Minimum enerjili yapı ile ağırlıklı topluluğun kararlarını karşılaştır, 10 saat. ④ Enerji ve geometrik eşik belirsizliğini uygula, 8 saat. ⑤ Teslim, 6 saat.

**Veri ve araçlar:** Açık GEOM konformerleri ve xTB enerjileri, RDKit, NumPy.

**Sert sonuç:** En düşük enerjili yapısı hidrojen bağı gösterdiği halde örneklenmiş topluluğunda bu durumun azınlıkta kaldığı moleküller ve tersi. Her örnek için belirsizlik altında korunabilen popülasyon aralığı.

**Yenilik:** Konformer toplulukları ve molekül içi hidrojen bağları yoğun çalışılmış konular. Katkı, tek yapıdan verilen kararların hangi moleküllerde sağlam biçimde tersine döndüğünü gösteren açık bir test kümesi.

**Doğrulama:** Yinelenen konformerleri ele; enerji türlerini karıştırma; farklı geometrik eşikler kullan; seçili örnekleri yeniden optimize et. Sonuç, çözelti popülasyonu değil, kullanılan enerji modeli ve örneklenmiş topluluk içindir.

**Risk:** Enerji belirsizliği karşıörnekleri siler veya konformer örneklemesi yetersiz kalır.

**Birincilik:** %3.

### 6. Aynı Kristal, Farklı Cevap: Atomistik yazılımlara matematiksel eşdeğerlik testi

**Adımlar:** ① Küçük, çeşitli bir kristal kümesi ve iki potansiyel kur, 4 saat. ② Eşdeğer hücre, atom sırası, öteleme ve dönme dönüşümleri üret, 6 saat. ③ Enerji, kuvvet ve gerilme uyuşmazlıklarını tara, 10 saat. ④ En küçük karşıörnekleri çıkar ve sayısal yakınsamayı doğrula, 8 saat. ⑤ Teslim, 6 saat.

**Veri ve araçlar:** COD veya JARVIS yapıları; ASE, pymatgen, MACE, CHGNet. Modeller sırayla çalıştırılır.

**Sert sonuç:** Fiziksel olarak aynı sistemi farklı gösterdiğinde sonuç değiştiren doğrulanmış yazılım veya model durumları; her biri için kısa yeniden üretim betiği. Sorun bulunmazsa tolerans ve kapsamı açık bir uyumluluk tablosu.

**Yenilik:** Metamorfik test ve fiziksel değişmezlik testleri biliniyor. Katkı ancak yaygın bir araçta yeni, etkili ve açıklanabilir bir karşıörnek bulunursa güçlü olur.

**Doğrulama:** Atom eşleştirmesi, kuvvet ve gerilme dönüşümleri, süperhücre normalizasyonu, hassasiyet ve kesim yarıçapı kontrolleri. Beklenen yuvarlama hatası bulgu sayılmaz.

**Risk:** Araçlar düzgün çalışır; geriye yararlı ama keşif etkisi düşük bir test paketi kalır.

**Birincilik:** %5.

**Uzman jüriye “vay” dedirtecek tek seçimim kinetik ikizler.** Aynı gerçek deneyleri açıklayan iki makul mekanizmanın başka bir koşulda ayrışması, ardından saklanan deneyin bunları ayırması güçlü bir bilimsel hikâye olur: yalnızca belirsizlik göstermiyorsun, hangi ölçümün bilgi sağlayacağını buluyorsun. Küçük hidrojen mekanizması, birkaç serbest parametre ve tek deney ailesiyle solo 34 saatte uygulanabilir. Ancak büyük ayrışma garanti değil; ilk 8 saatte makul sınırlar içinde umut verici bir çift çıkmazsa iddiayı daraltmak gerekir.