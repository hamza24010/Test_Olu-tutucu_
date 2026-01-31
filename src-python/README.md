# Python AI Motoru Kurulumu

Bu proje, arka planda PDF işlemleri için Python kullanır.

## Kurulum (Geliştirici Modu)

1. Sanal ortam oluşturun:
   ```bash
   cd src-python
   python -m venv .venv
   ```

2. Aktif edin ve paketleri kurun:
   ```bash
   # Linux/Mac
   source .venv/bin/activate
   
   # Windows
   .venv\Scripts\activate
   
   # Paketler
   pip install docling torch torchvision --index-url https://download.pytorch.org/whl/cu118
   ```

3. `engine.py` betiğini düzenleyerek `Mock` veriyi kaldırıp gerçek Docling kodlarını aktifleştirin.
