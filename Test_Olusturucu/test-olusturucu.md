# Test Oluşturucu Uygulama Planı

## Hedef
Öğretmenlerin PDF dosyalarından soruları otomatik olarak ayıklayıp bir soru bankası oluşturabileceği ve bu bankadan yeni testler üretebileceği Python (PyQt6) tabanlı bir masaüstü uygulaması geliştirmek.

## Görevler

### Faz 1: Altyapı ve Hazırlık
- [ ] Görev 1: Python venv oluşturulması ve paketlerin (`PyQt6`, `google-generativeai`, `pdf2image`, `pillow`, `PyMuPDF`) kurulması → Doğrulama: `pip list` içinde paketlerin görünmesi.
- [ ] Görev 2: Proje dizin yapısının (`src/`, `assets/questions/`, `data/`) oluşturulması → Doğrulama: Klasörlerin varlığı.
- [ ] Görev 3: SQLite veritabanı şemasının (`questions`, `tests`) oluşturulması → Doğrulama: `data/test_olusturucu.db` dosyasının oluşması.

### Faz 2: Çekirdek Mantık (Core Logic)
- [ ] Görev 4: PDF sayfalarını yüksek çözünürlüklü görsellere (PNG) dönüştüren modülün yazılması → Doğrulama: Örnek bir PDF'in sayfa sayfa resim olarak kaydedilmesi.
- [ ] Görev 5: Gemini 1.5 Flash ile sayfa analizi ve soru tespiti modülünün yazılması → Doğrulama: Görselden koordinat ve metin içeren JSON çıktısı alınması.
- [ ] Görev 6: Koordinatlara göre görseli kırpan ve hem metni hem görseli DB'ye kaydeden mantığın kurulması → Doğrulama: DB'de yeni kayıt ve klasörde kırpılmış resim.

### Faz 3: Arayüz (PyQt6 UI)
- [ ] Görev 7: Ana pencere ve "Soru Ayıkla" (PDF Yükleme) ekranının yapılması → Doğrulama: `python main.py` ile pencerenin açılması.
- [ ] Görev 8: "Soru Bankası" ekranının (Soruları listeleme, silme, arama) yapılması → Doğrulama: DB'deki soruların listede görünmesi.
- [ ] Görev 9: "Test Oluşturma" ve PDF Dışa Aktarma ekranının yapılması → Doğrulama: Seçilen sorulardan yeni bir PDF üretilmesi.

### Faz 4: Gelişmiş Özellikler ve Final Kontrol
- [ ] Görev 10: **Çok Sayfalı PDF Desteği**: Dosyaları 5'er sayfalık parçalar (chunks) halinde Gemini'ye gönderme ve işlem durumunu progress bar ile gösterme. → Doğrulama: 10+ sayfalık PDF'lerin sorunsuz işlenmesi.
- [ ] Görev 11: Uygulamanın uçtan uca test edilmesi ve hata yönetimi (API hata kontrolü vb.) eklenmesi → Doğrulama: Tüm akışın hatasız çalışması.


## Tamamlandığında
- [ ] PDF'den soruları hatasız ayıklayan, veritabanında saklayan ve yeni testler üretebilen bitmiş bir masaüstü uygulaması.

## Notlar
- Gemini API anahtarı `.env` dosyasında saklanacaktır.
- `poppler-utils` sistemde kurulu olmalıdır (pdf2image için).
