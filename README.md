# RIGEL Brief AI

RIGEL Brief AI, proje fikirlerini düzenli bir brief haline getiren Streamlit tabanlı MVP uygulamasıdır.

## v8 final polish

- Boş görünen üst satırlar kaldırıldı.
- Başlıklar doğrudan kendi kartlarıyla birleşti.
- “adım adım brief akışı” rozeti kaldırıldı.
- Modern/Canva benzeri tema korundu.
- Adım adım brief ayarları korundu.
- Textarea köşe kusurları ve gereksiz kart boşlukları temizlendi.
- PDF Türkçe karakter desteği korundu.

## Kurulum

```bash
cd rigel_brief_ai
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Windows PowerShell:

```powershell
cd rigel_brief_ai
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```
