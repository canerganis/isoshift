**1. IsoTopo: “Kimyası aynı kristalde, yalnızca izotop değiştirerek topolojik fonon geçişi”**

**Fikir:** Elektronik potansiyeli değiştirmeden atom kütlelerini değiştirerek bir kristalde Weyl fonon noktalarını oluşturmak veya yok etmek. Sonuç, aynı elementlerden oluşan iki izotopik kristal arasında farklı, hesaplanabilir bir topolojik durum olur. Güçlü başlık, keşif gerçekleşirse kullanılmalı.

**34 saatlik yürütme:**

1. **0–4 saat:** PhononDB içindeki açık kuvvet sabitlerinden, küçük hücreli ve Li, B veya C içeren kullanılabilir kristalleri seç.
2. **4–10 saat:** Phonopy ile doğal ve izotopça zenginleştirilmiş kütlelerde fonon bantlarını hesapla. Yakın bant temaslarını tara.
3. **10–19 saat:** En güçlü adaylarda kütleyi sürekli değiştirerek kritik geçişi bul. Fiziksel uç noktalar gerçek kararlı izotoplar olmalı.
4. **19–28 saat:** Weyl noktalarının çevresinde Berry akısını ve tam sayı Chern yükünü hesapla; ağ yakınsamasını doğrula.
5. **28–34 saat:** Tek aday için yeniden üretilebilir hesap, geçiş animasyonu ve deneysel sınama önerisi hazırla.

**Veri ve araçlar:** PhononDB kuvvet sabitleri, açık izotop kütleleri, Phonopy, NumPy/SciPy. Küçük dinamik matrisler sayesinde GPU zorunlu değil.

**Sert sonuç:** Gerçek iki izotop bileşimi arasında bant temasının oluşması veya yok olması ve bunu doğrulayan kuantize topolojik yük. Sadece frekans kayması başarı sayılmaz.

**Yenilik ve en yakın çalışmalar:** Topolojik fononlar, yapay fononik kristaller ve izotoplarla ısı iletimi kontrolü mevcut. Buradaki hedef, gerçek atomik kristalde **yalnızca kararlı izotop değişimiyle erişilebilir topolojik geçiş**. Bunun daha önce gösterilmediğini kendi bilgimden garanti edemem; aday bulunduğunda özel literatür kontrolü gerekir.

**Doğrulama:** Akustik toplam kuralı, dinamik kararlılık, farklı ağlar, bağımsız Berry akısı hesabı ve kuvvet sabitlerine küçük pertürbasyonlar. Saf izotop uç noktaları, rastgele izotop karışımının saçılma sorununu azaltır.

**Ana risk:** Erişilebilir kütle farkı hiçbir adayı geçişten geçirmeyebilir. Harmonik yaklaşımda görülen geçiş, anharmonik genişleme altında deneysel olarak seçilemeyebilir.

**Birincilik ihtimali:** Öznel olarak **%9**.

**2. VacuumLatch: “Casimir kuvvetiyle iki kararlı mesafe: pasif bir nanoskopik bellek tasarımı”**

**Fikir:** Bir sıvı içinde, kaplamalı iki yüzey arasında Casimir kuvvetinin uzaklığa bağlı spektral katkılarını tasarlayarak iki ayrı kararlı denge mesafesi bulmak. Hedef, elektrik veya manyetik alan uygulanmadan iki konumu koruyan bir sistemin hesaplanabilir tasarımı.

**34 saatlik yürütme:**

1. **0–5 saat:** Açık optik verisi yeterli katı ve sıvıları seç; kapsamı üç veya dört malzemeyle sınırla.
2. **5–12 saat:** Çok katmanlı, sonlu sıcaklıklı Lifshitz hesabını kur; bilinen limitlerle doğrula.
3. **12–21 saat:** Katman kalınlıklarını optimize ederek iki kararlı, aralarında bir kararsız denge ara.
4. **21–29 saat:** Optik veri belirsizliği, spektral ekstrapolasyon, kaldırma kuvveti ve Brown hareketi altında tasarımı zorla.
5. **29–34 saat:** Enerji manzarası, tolerans haritası ve yeniden üretilebilir tasarım dosyası çıkar.

**Veri ve araçlar:** refractiveindex.info içindeki açık deneysel optik veriler ve uygun açık makale ekleri; SciPy integrasyonu ve optimizasyonu. RTX 4060 gerekli değil.

**Sert sonuç:** Normal doğrultuda iki enerji minimumu, aralarında en az **20 kBT** bariyer ve veri belirsizliği altında korunan çift kararlılık. Bu, yönlendirilmiş paralel yüzey geometrisi için sonuç olur; serbest üç boyutlu levitasyon iddiası olmaz.

**Yenilik ve en yakın çalışmalar:** Lifshitz kuramı ve Munday, Capasso, Parsegian’ın sıvıda itici Casimir kuvveti deneyi temel oluşturur. Casimir dengeleri zaten çalışılıyor. Yenilik ancak gerçek malzemelerle, belirsizliğe dayanıklı ve önceki tasarımlardan ayrışan çift kararlılık bulunursa vardır.

**Doğrulama:** İki bağımsız integrasyon, bilinen çekim ve itme örnekleri, kuvvet ile enerji türevinin tutarlılığı, yüzey pürüzlülüğü duyarlılığı.

**Ana risk:** Eksik optik spektrumlar sahte denge üretebilir; elektrostatik ve yüzey kuvvetleri deneyde Casimir etkisini örtebilir.

**Birincilik ihtimali:** Öznel olarak **%6**. Bu yüzdeler yarışmacı verisine dayanmıyor.

**Tek seçimim IsoTopo.** Listedekiler arasında, “kimyayı değiştirmeden topolojik durum değiştirmek” en güçlü sürpriz ile en temiz hesaplanabilir iddiayı birleştiriyor. Yeni model eğitimi gerektirmiyor; kritik hesap küçük matrislerin özdeğerleri ve topolojik yükleri. Solo 34 saatte sağlam bir tarama ve doğrulama hattını bitirme ihtimalini yaklaşık **%80**, gerçekten yeni ve dayanıklı pozitif sonuç çıkarma ihtimalini ise **%20–35** görüyorum. Birincilik hedefi için esas bahis ikinci olasılık.