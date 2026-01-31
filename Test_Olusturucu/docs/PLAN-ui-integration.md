# PLAN-ui-integration.md - Stitch UI Entegrasyonu

> **Durum:** PLANLAMA
> **Hedef:** Stitch ile oluşturulan HTML/CSS arayüzünü PyQt6 Desktop uygulamasına entegre etmek.
> **Yöntem:** PyQt6 `QWebEngineView` + `QWebChannel` (Hybrid App)

---

## 🏗️ Mimari Yaklaşım

Mevcut "Native Widget" yapısı yerine, modern web teknolojilerini (Stitch çıktıları) render eden bir **Hybrid** yapıya geçeceğiz.

1.  **Frontend (Görünüm):** Stitch tarafından üretilen HTML/CSS/JS dosyaları.
2.  **Backend (Mantık):** Mevcut Python (`src/core`, `src/db`) kodları.
3.  **Köprü (Bridge):** `QWebChannel` teknolojisi ile JS'in Python fonksiyonlarını çağırması.

### Bileşenler

| Katman | Teknoloji | Görev |
| :--- | :--- | :--- |
| **View** | `QWebEngineView` | HTML dosyalarını görüntüler. |
| **Logic** | Python Class (`Bridge`) | JS'den gelen istekleri karşılar (örn. `addQuestion`, `getTests`). |
| **Data** | SQLite / Python Objects | Veri saklama ve işleme. |

---

## 📅 Uygulama Planı

### Faz 1: Hazırlık ve Altyapı
- [ ] **Bağımlılık Kontrolü:** `PyQt6-WebEngine` paketinin kurulu olduğundan emin olunması.
- [ ] **Varlık Yönetimi:** `stitch_question_bank_management` altındaki dosyaların `src/assets/web` klasörüne taşınması ve organize edilmesi (css, js, html klasörleri).
- [ ] **Bridge Tasarımı:** Python ve JS arası veri akış şemasının belirlenmesi.

### Faz 2: Backend Köprüsü (Bridge)
- [ ] **API Tanımlama:** JS'in ihtiyaç duyduğu fonksiyonların Python tarafında `pyqtSlot` olarak tanımlanması.
    - `get_questions()`, `save_question(data)`, `delete_question(id)`
    - `generate_test(config)`, `get_dashboard_stats()`
- [ ] **QWebChannel Kurulumu:** `api.py` veya `bridge.py` dosyasının oluşturulması.

### Faz 3: UI Entegrasyonu
- [ ] **WebEngine Entegrasyonu:** `ModernMainWindow` içindeki `ContentStack` yerine tam ekran veya çerçeveli `QWebEngineView` yerleştirilmesi.
- [ ] **Sayfa Yönlendirme:** Menü butonlarının HTML sayfaları arasında geçiş yapacak şekilde güncellenmesi (`load(QUrl(...))`).

### Faz 4: Frontend Adaptasyonu (Stitch Dosyaları)
- [ ] **QWebChannel.js Entegrasyonu:** HTML dosyalarına `qwebchannel.js` eklenmesi.
- [ ] **Mock Verilerin Kaldırılması:** HTML'deki statik verilerin silinip, sayfa yüklendiğinde Python'dan veri çekecek JS kodlarının yazılması.
- [ ] **Olay Bağlama:** Buton tıklamalarının (Örn: "Kaydet") Python köprüsünü çağırması.

---

## 📂 Dosya Yapısı Değişikliği

```text
src/
├── ui/
│   ├── bridge.py       <-- YENİ (JS-Python iletişimi)
│   ├── web_view.py     <-- YENİ (QWebEngineView sarmalayıcı)
│   ├── ... (eski bank_tab, test_tab silinebilir veya pasife alınabilir)
assets/
└── web/                <-- YENİ (Stitch dosyaları buraya)
    ├── index.html
    ├── question_bank.html
    ├── style.css
    └── script.js
```

## ⚠️ Riskler ve Çözümler
- **CORS / Dosya Yolu Sorunları:** Yerel dosyalar çalışırken bazen JS modülleri sorun çıkarabilir.
    - *Çözüm:* Gerekirse Python içinde basit bir yerel HTTP sunucusu thread'i başlatılabilir veya Qt'nin kaynak sistemi (qrc) kullanılabilir. Şimdilik direkt dosya yüklemeyi deneyeceğiz.
- **Asenkron İletişim:** JS -> Python çağrıları asenkrondur.
    - *Çözüm:* JS tarafında Promise yapısı veya callback kullanarak verilerin gelmesi beklenecek.

---

## Sonraki Adım
Plan onaylandıktan sonra `/create` komutu ile uygulamaya başlayacağız.
