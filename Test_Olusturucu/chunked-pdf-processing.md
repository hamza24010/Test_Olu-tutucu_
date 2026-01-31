# Görev: Çok Sayfalı PDF'leri Parçalı İşleme (Chunked Processing)

Bu görev, büyük PDF dosyalarının Gemini API limitlerine takılmadan ve daha güvenilir bir şekilde işlenmesini sağlamak için dosyayı 5 sayfalık parçalar halinde gönderme özelliğini eklemeyi kapsar.

## Değişiklikler

### 1. `src/core/gemini_service.py`
- Sohbet oturumu (Chat Session) desteği eklenecek.
- `analyze_chunk` metodu eklenecek: 5 görseli aynı anda gönderip analiz edecek.
- Önceki parçalardaki soruları hatırlaması için `history` yönetilecek.

### 2. `src/core/pdf_processor.py`
- Mevcut `convert_pdf_to_images` metodunun sayfa sırasını garanti ettiğinden emin olunacak.

### 3. `main.py`
- `process_pdf` metodu yeniden yapılandırılacak:
    - Görsel listesini 5'erli gruplara bölecek.
    - `QProgressDialog` kullanarak "1/4. parça işleniyor..." şeklinde geri bildirim verecek.
    - Hata durumunda ilgili parçayı yeniden deneme opsiyonu sunacak (veya hata verip devam edecek).

## Uygulama Adımları

1. `gemini_service.py` güncellemesi.
2. `main.py` üzerinde chunking mantığının ve progress bar'ın eklenmesi.
3. Test ve doğrulama.

## Başarı Kriterleri
- [ ] 10 sayfalık bir PDF'in 2 parça halinde işlenmesi.
- [ ] Arayüzde parça bilgisinin gösterilmesi.
- [ ] Sohbet geçmişi sayesinde bağlamın korunması.
- [ ] Hatalı parçaların izole edilmesi.
