# PLAN-ui-integration-polish.md - UI Integration & Cleanup

> **Durum:** PLANLAMA
> **Hedef:** Stitch ile tasarlanmış arayüzleri entegre etmek, çalışmayan özellikleri (Backend) tamamlamak ve UI temizliği yapmak.

---

## 🎯 Hedefler

1.  **Stitch Entegrasyonu:** `stitch_question_bank_management` klasöründeki HTML/CSS tasarımlarını `src/assets/web/pages` altına taşımak ve FastAPI şablon sistemine (Jinja2) uyarlamak.
2.  **PDF Yükleme Sayfası:** Stitch tasarımındaki PDF yükleme sayfasını aktif etmek ve backend'e bağlamak.
3.  **Test Oluşturma (Backend):** Test oluşturma formundaki eksik backend logic'lerini (filtreleme, rastgele seçim) tamamlamak/iyileştirmek.
4.  **Temizlik:** Çalışmayan veya mockup olarak kalan butonları/alanları kaldırmak.

---

## 📅 Uygulama Adımları

### Faz 1: Stitch Tasarımlarının Keşfi ve Taşınması
- [ ] `stitch_question_bank_management` klasörünü tara.
- [ ] İlgili HTML dosyalarını (`upload.html` vb. varsa) bul.
- [ ] Mevcut `src/assets/web/pages` içindeki dosyalarla Stitch tasarımlarını birleştir (Stitch görünümü + Mevcut JS Logic).

### Faz 2: PDF Yükleme Sayfası (Upload Page)
- [ ] `/pdf_upload.html` (veya Stitch'teki karşılığı) sayfası oluştur/düzenle.
- [ ] Sol menüdeki "PDF Yükle" butonunu bu sayfaya yönlendir (`onclick="navigateTo('pdf_upload.html')"`).
- [ ] Sayfadaki "Dosya Seç / Yükle" alanını `/api/upload-pdf` endpoint'ine bağla.
- [ ] Yükleme sonrası kullanıcıya geri bildirim ver (Yüklendi -> Soru Bankasına Git).

### Faz 3: Test Oluşturma Sayfası (Test Generator)
- [ ] `test_generator.html` sayfasındaki **çalışmayan** sol menü linklerini düzelt.
- [ ] Formdaki "Öğrenci Seçimi" bölümünü kaldır (Backend desteği yok).
- [ ] "Ders", "Zorluk", "Soru Sayısı" alanlarını koru.
- [ ] "Soru Sayısı" için input ekle (Şu an 10 sabit, kullanıcı seçebilsin).
- [ ] Backend: `/api/generate-random-test` endpoint'ini "Soru Sayısı" parametresini tam dikkate alacak şekilde güncelle.

### Faz 4: Dashboard Temizliği
- [ ] Eğer Stitch içinde bir Dashboard tasarımı varsa onu entegre et.
- [ ] Yoksa, mevcut Dashboard'daki gereksiz/bozuk widget'ları temizle.

---

## 🛠 Görev Dağılımı (Orchestration)

| Görev | Sorumlu Ajan | Detay |
| :--- | :--- | :--- |
| **Tasarım Transferi** | `frontend-specialist` | Stitch HTML -> Jinja2 Template |
| **Upload Logic** | `frontend-specialist` | JS Fetch API -> Backend bağlantısı |
| **Backend Logic** | `backend-specialist` | Test Generation algoritması + Endpoint |
| **Test** | `test-engineer` | PDF yükle -> Soru oluştu mu? Test oluştur -> PDF geldi mi? |

---

## ✅ Doğrulama Kriterleri
- [ ] Sol menüdeki "PDF Yükle" tıklayınca özel yükleme sayfası açılıyor.
- [ ] Bu sayfadan PDF atılınca sorular veritabanına ekleniyor.
- [ ] "Test Oluştur" sayfasında sadece çalışan ayarlar var (Öğrenci yok).
- [ ] Test oluştur diyince PDF iniyor.
