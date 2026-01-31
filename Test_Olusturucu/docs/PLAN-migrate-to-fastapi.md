# PLAN-migrate-to-fastapi.md - Modern Web Migrasyonu

> **Durum:** PLANLAMA
> **Hedef:** Performans sorunlu PyQt6 arayüzünden, yerel çalışan modern FastAPI web arayüzüne geçiş.
> **Kullanım:** Kullanıcı terminalden `run.bat/sh` diyecek, tarayıcıda uygulama açılacak. Sunucu gerekmez.

---

## 🏗️ Mimari Değişiklik (Yerel Web App)

Uygulama artık "Hibrit Masaüstü" değil, "Yerel Web Sunucusu" mimarisinde çalışacak.

| Eski (Sorunlu) | Yeni (Hızlı) |
| :--- | :--- |
| **Arayüz:** PyQt6 WebEngine | **Arayüz:** Chrome/Edge/Firefox (Kullanıcının tarayıcısı) |
| **Render:** Yavaş, eski motor | **Render:** Yerel, çok hızlı |
| **Backend:** PyQt Slotları | **Backend:** FastAPI (Python) |
| **Erişim:** `python main.py` | **Erişim:** `http://localhost:8000` |

> **Not:** Hiçbir veriniz internete gitmez. Her şey (PDF işleme, veritabanı) bilgisayarınızda kalır (`localhost`).

---

## 📅 Uygulama Adımları

### Faz 1: Altyapı Hazırlığı (Backend)
- [ ] **FastAPI Kurulumu:** `uvicorn`, `fastapi`, `jinja2`, `python-multipart` paketlerinin eklenmesi.
- [ ] **Server Dosyası:** `src/server.py` oluşturulması.
- [ ] **Statik Dosyalar:** `src/assets/web` klasörünün `static` olarak sunulması.

### Faz 2: API Endpoint'leri
Mevcut PyQt "Bridge" fonksiyonlarını HTTP endpoint'lerine dönüştüreceğiz:
- [ ] `GET /api/questions` -> Tüm soruları JSON döndür.
- [ ] `POST /api/upload-pdf` -> PDF yükle ve analiz et.
- [ ] `DELETE /api/questions/{id}` -> Soruyu sil.
- [ ] `POST /api/generate-test` -> Test PDF'i oluştur.

### Faz 3: Frontend Bağlantısı
- [ ] **HTML Düzenleme:** `window.bridge.xxx` çağrılarının `fetch('/api/xxx')` ile değiştirilmesi.
- [ ] **Navigasyon:** Tek sayfa uygulaması (SPA) hissi veya klasik link yapısının düzenlenmesi.

### Faz 4: Başlatıcı Script
- [ ] **Otomatik Başlatma:** Uygulamayı tek tıkla açan (`run_app.py`) bir script yazılması.
    - Sunucuyu başlatır.
    - Otomatik olarak tarayıcıyı açar (`webbrowser.open`).

---

## 📂 Hedef Dosya Yapısı

```text
src/
├── server.py           <-- YENİ (Backend sunucusu)
├── api/                <-- YENİ (API route'ları)
├── core/               <-- (Mevcut mantık aynen kalacak)
├── db/                 <-- (Mevcut veritabanı aynen kalacak)
└── assets/
    └── web/            
        ├── pages/      <-- HTML dosyaları
        ├── css/        <-- CSS
        └── js/         <-- Frontend logic (fetch api)
run_app.py              <-- YENİ (Başlatıcı)
```

## ⚠️ Riskler ve Önlemler
- **Tarayıcı Cache:** CSS güncellemeleri hemen görünmeyebilir. *Çözüm: Geliştirme modunda cache devre dışı bırakılır.*
- **Dosya Yolları:** HTML içindeki resim yolları (`file://`) artık çalışmaz. *Çözüm: Resimler de `static` üzerinden sunulacak (`/static/questions/img1.png`).*

---

## Sonraki Adım
Onay verirseniz `/create` komutu ile migrasyonu başlatacağız.
