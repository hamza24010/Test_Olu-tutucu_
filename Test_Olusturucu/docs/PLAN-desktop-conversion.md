# PLAN: TestGen Desktop Conversion

Mevcut web tabanlı Test Oluşturucu uygulamasını, Python backend ve modern HTML/Tailwind arayüzünü koruyarak tam donanımlı bir Windows masaüstü uygulamasına dönüştürme planı.

## 🎯 Projenin Amacı
Uygulamayı bir tarayıcı sekmesinden çıkarıp, sistem tepsisi (tray), bildirimler ve yerel dosya sistemi entegrasyonu olan bağımsız bir `.exe` dosyasına dönüştürmek.

---

## 🛠 Teknoloji Seçimi & Rasyonel
- **Frontend Wrapper:** `PyWebView` (Mevcut HTML/Tailwind UI'ı kullanmak için en hafif ve Python uyumlu çözüm).
- **Backend:** `FastAPI` (Mevcut API yapısını bozmadan yerel server olarak çalışmaya devam edecek).
- **Sistem Entegrasyonu:** `pystray` (Tray icon) ve `plyer` (Bildirimler).
- **Paketleme:** `PyInstaller` (Windows için tek bir executable oluşturmak için).

---

## 📂 Dosya Yapısı Değişiklikleri
```text
Test_Olusturucu/
├── src/
│   ├── main_desktop.py       # (YENİ) Desktop wrapper entry point
│   ├── core/
│   │   └── system_tray.py    # (YENİ) Sistem tepsisi yönetimi
│   └── ...
├── build_win.py             # (YENİ) PyInstaller build scripti
└── desktop-conversion.md    # (BU PLAN)
```

---

## 📝 Görev Listesi

### Faz 1: Desktop Foundation (P0)
- **Görev ID:** `DESKTOP-001`
- **İsim:** `main_desktop.py` Oluşturma
- **Acente:** `backend-specialist`
- **Açıklama:** PyWebView kullanarak FastAPI server'ını arka planda başlatan ve ana pencereyi açan giriş dosyasının yazılması.
- **INPUT:** `src/server.py` → **OUTPUT:** `src/main_desktop.py`
- **VERIFY:** `python src/main_desktop.py` komutuyla uygulama tarayıcıdan bağımsız bir pencerede açılıyor mu?

### Faz 2: Sistem Entegrasyonu (P1)
- **Görev ID:** `DESKTOP-002`
- **İsim:** Sistem Tepsisi ve Bildirimler
- **Acente:** `backend-specialist`
- **Açıklama:** Uygulamanın sağ alt köşede (tray) çalışması ve PDF işleme tamamlandığında Windows bildirimi göndermesi.
- **INPUT:** `src/core/pdf_processor.py` → **OUTPUT:** Bildirim tetikleyicileri
- **VERIFY:** PDF yükleme bittiğinde sistem bildirimi geliyor mu?

### Faz 3: UX & Window Polishing (P2)
- **Görev ID:** `DESKTOP-003`
- **İsim:** Pencere Durumu ve Splash Screen
- **Acente:** `frontend-specialist`
- **Açıklama:** Uygulama açılırken bir yükleme ekranı gösterilmesi ve pencere boyutunun/konumunun hatırlanması.
- **INPUT:** `PyWebView settings` → **OUTPUT:** Persistent config
- **VERIFY:** Uygulama kapatılıp açıldığında son konumunda mı açılıyor?

### Faz 4: Windows Paketleme (P3)
- **Görev ID:** `DESKTOP-004`
- **İsim:** PyInstaller Konfigürasyonu
- **Acente:** `devops-engineer`
- **Açıklama:** Tüm assetlerin (`static`, `templates`, `db`) tek bir `.exe` içine gömülmesi için build scripti yazılması.
- **INPUT:** Proje dosyaları → **OUTPUT:** `dist/TestGen.exe`
- **VERIFY:** `dist/TestGen.exe` dosyası başka bir klasöre taşındığında sorunsuz çalışıyor mu?

---

## ✅ PHASE X: Final Doğrulama
- [ ] Uygulama iconu Windows taskbar'da doğru görünüyor mu?
- [ ] Tray menüsünden "Çıkış" yapılabiliyor mu?
- [ ] Offline modda (Gemini hariç) arayüz ve arşiv çalışıyor mu?
- [ ] `PyInstaller` build hatasız tamamlanıyor mu?

---

**Next Steps:**
1. Planı onaylıyorsanız `/create` komutuyla uygulamaya başlayabiliriz.
2. `PyInstaller` için gerekli bağımlılıkları (`pip install pywebview pystray plyer pyinstaller`) kurarak başlayacağım.
