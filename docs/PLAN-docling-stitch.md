# PLAN-docling-stitch: Docling & Stitch ile PDF Soru Ayrıştırma Asistanı

> **Durum**: Planlandı
> **Hedef**: Rust (Tauri) ve Python (Docling) hibrit mimarisi ile yüksek performanslı, Google Stitch tasarım diline sahip masaüstü sorusu ayrıştırma uygulaması.

---

## 🏗️ Mimari ve Teknoloji Yığını

| Katman | Teknoloji | Açıklama |
|/---|---|---|
| **Frontend** | React, Tailwind CSS, Framer Motion | Google Stitch (Material 3) tasarım dili, akıcı animasyonlar. |
| **Backend** | Rust (Tauri), SQLx (SQLite) | Sistem entegrasyonu, veri yönetimi, Sidecar orkestrasyonu. |
| **AI Engine** | Python, Docling, PyTorch | PDF Layout analizi, soru tespiti. (RTX 3050 CUDA / CPU Fallback). |
| **Data** | SQLite | Ayrıştırılan soruların ve test taslaklarının yerel veritabanı. |

---

## 🚀 Uygulama Fazları

### Faz 1: Kurulum ve Temel Yapılandırma
> **Amaç**: Temiz bir Tauri + React projesi oluşturmak ve mevcut tasarım dosyalarını entegre etmek.

1.  **Tasarım Dosyalarını Koruma**:
    -   Mevcut klasördeki tasarım dosyalarını (`Project design files`) geçici bir `_design_backup` klasörüne taşı.
2.  **Proje Başlatma**:
    -   `npm create tauri-app@latest . -- -t react-ts` komutu ile projeyi oluştur.
    -   `_design_backup` içindeki stil ve bileşenleri `src` klasörüne geri taşı ve React bileşenlerine dönüştür.
3.  **Frontend Bağımlılıkları**:
    -   `npm install tailwindcss postcss autoprefixer framer-motion lucide-react clsx tailwind-merge`
    -   `npx tailwindcss init -p`
    -   `tailwind.config.js` dosyasını Stitch renk paleti ve `border-radius: 16px` gibi kurallarla yapılandır.
4.  **Veritabanı Kurulumu**:
    -   Proje kökünde `db.sqlite` oluştur.
    -   Rust tarafında `sqlx` ve `tokio` bağımlılıklarını ekle.

### Faz 2: Python AI Motoru (Sidecar)
> **Amaç**: Docling kullanarak PDF analizi yapan ve JSON çıktısı veren Python motorunu hazırlamak.

1.  **Python Ortamı**:
    -   `src-python/` klasörü oluştur.
    -   `python -m venv .venv` ile sanal ortam kur.
    -   CUDA desteği için: `pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118`
    -   Docling kurulumu: `pip install docling`
2.  **Motor Scripti (`engine.py`)**:
    -   `src-python/engine.py` dosyasını oluştur.
    -   **Girdi**: Komut satırı argümanı olarak PDF dosya yolu.
    -   **İşlem**:
        -   GPU kontrolü yap (`torch.cuda.is_available()`). RTX 3050 yoksa CPU moduna geç ve log mesajı bas.
        -   `Docling` ile belgeyi analiz et.
        -   Soru bloklarını (Bounding Box) tespit et.
        -   Görüntüleri kırp ve geçici klasöre kaydet.
    -   **Çıktı**: Standart çıktıya (stdout) JSON formatında bas:
        ```json
        [{"id": "uuid", "bbox": [x,y,w,h], "image": "path/to/crop.png", "text": "..."}]
        ```
3.  **Sidecar Yapılandırması (Local Dev)**:
    -   Geliştirme aşamasında Python scriptini doğrudan çağıracak bir Shell Wrapper (`engine.sh` / `engine.bat`) oluştur ve Tauri `externalBin` olarak tanımla.

### Faz 3: Rust Backend Köprüsü
> **Amaç**: React ile Python arasındaki iletişimi ve veri yönetimini sağlamak.

1.  **Veri Modelleri (Structs)**:
    -   `Question` struct'ını tanımla (id, bbox, image_path, tags).
2.  **Command Modülü**:
    -   `analyze_pdf(path: String)` komutunu yaz.
    -   Bu komut `Command::new_sidecar("engine")` (veya geliştirme için direkt path) kullanarak Python sürecini başlatmalı.
    -   Gelen `stdout` verisini parse edip Frontend'e `Result<Vec<Question>>` dönmeli.
3.  **Veritabanı İşlemleri**:
    -   `save_questions(questions: Vec<Question>)` komutunu yaz.
4.  **Sidecar Yönetimi**:
    -   Python süreci hata verirse veya çökerse (örn. VRAM yetersizliği) durumu yakala ve Frontend'e anlamlı hata mesajı ("GPU Yetersiz, CPU'ya geçiliyor...") ilet.

### Faz 4: Stitch UI & Kullanıcı Deneyimi
> **Amaç**: "Google Stitch" tasarım dilini React üzerinde canlandırmak.

1.  **Layout & Dashboard**:
    -   Ekranı dikey olarak ikiye böl: **PDF Önizleme** (Sol) | **Soru Kartları** (Sağ).
    -   Geniş beyaz alanlar ve yumuşak gölgeler kullan.
2.  **Sürükle & Bırak (Drag & Drop)**:
    -   Uygulama açılışında şık bir dosya yükleme alanı tasarla.
    -   Dosya bırakıldığında "Analyzing with Docling..." animasyonlu yükleme ekranını göster.
3.  **Soru Kartları**:
    -   Sağ panelde analiz edilen soruları kartlar halinde listele.
    -   Her kartta soru görseli ve "Sil/Düzenle" butonları olsun.
4.  **Placeholder Yönetimi**:
    -   "Gelişmiş Filtreleme", "Bulut Senkronizasyonu" gibi özellikleri UI'da göster ancak "Devre Dışı" (Disabled) duruma getir veya tıklandığında "Yakında" toast mesajı göster.

### Faz 5: Entegrasyon ve Optimizasyon
> **Amaç**: Hataları gidermek ve son kullanıcı deneyimini iyileştirmek.

1.  **Hata Yönetimi**: Sidecar başlatılamazsa kullanıcıya manuel Python yolu seçtirme veya hata raporlama ekranı.
2.  **Performans**: Büyük PDF'lerde arayüzün donmaması için Rust tarafında işlemlerin `async` olmasını garanti et.
3.  **Linter ve Format**: Kodun temiz kalması için `cargo clippy` ve `eslint` çalıştır.

---

## ⚠️ Riskler ve Çözümler
- **Python Bağımlılık Boyutu**: `torch` ve `docling` çok büyük.
    - *Çözüm*: İlk aşamada kullanıcıdan `venv` kurmasını isteyeceğiz. İleride PyInstaller ile tek dosya haline getireceğiz.
- **GPU Bellek Hataları (OOM)**: RTX 3050 (4GB/6GB) sınırlı belleğe sahip.
    - *Çözüm*: `engine.py` içinde `batch_size` kontrolü yap ve OOM hatasında otomatik CPU'ya düş.
