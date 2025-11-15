# 🌾 Farmer Assessment System - Sistem de Evaluare Fermieri

Sistem modular complet pentru evaluarea fermierilorși generarea automatică de cereri de finanțare agricolă (CHM).

## 📋 Descriere

Acest sistem implementează un workflow complet pentru:
- 📝 Colectare date fermieri (profil, experiență, resurse)
- 📄 Procesare OCR documente (CNI, certificate, parcele)
- 📊 Scoring automat (bonitate teren, experiență fermier, risc)
- 🎯 Evaluare eligibilitate pentru programe de finanțare
- 📑 Generare automată CHM și rapoarte

## 🏗️ Arhitectură

```
├── Backend/          # FastAPI + MongoDB
│   ├── app/
│   │   ├── config/   # Configurare DB și settings
│   │   ├── models/   # Modele date (Pydantic)
│   │   ├── services/ # Business logic
│   │   ├── routes/   # API endpoints
│   │   └── utils/    # Utilități
│   └── requirements.txt
│
├── AI/               # Modul AI pentru procesare
│   ├── ocr/          # Extractoare OCR
│   │   ├── document_processor.py
│   │   ├── cni_extractor.py
│   │   ├── certificate_extractor.py
│   │   └── parcel_extractor.py
│   ├── document_generation/
│   │   ├── chm_generator.py
│   │   └── report_generator.py
│   ├── processor.py  # Main AI processor
│   └── requirements.txt
│
└── Frontend/         # React + TypeScript
    └── src/
```

## 🚀 Setup Rapid

### 1. Backend Setup

```bash
cd Backend

# Instalare dependințe
pip install -r requirements.txt

# Configurare variabile de mediu (.env este deja configurat cu MongoDB)
# MONGO_API_KEY=mongodb+srv://...

# Pornire server
python -m app.main
# SAU
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend va rula pe: `http://localhost:8000`
- API Docs: `http://localhost:8000/api/docs`
- ReDoc: `http://localhost:8000/api/redoc`

### 2. AI Module Setup

```bash
cd AI

# Instalare dependințe
pip install -r requirements.txt

# Instalare Tesseract OCR (necesar pentru OCR)
# macOS:
brew install tesseract tesseract-lang

# Ubuntu/Debian:
sudo apt-get install tesseract-ocr tesseract-ocr-ron

# Windows: Download de pe https://github.com/UB-Mannheim/tesseract/wiki
```

### 3. Frontend Setup

```bash
cd Frontend

# Instalare dependințe
npm install

# Pornire dev server
npm run dev
```

Frontend va rula pe: `http://localhost:5173`

## 📊 Colecții MongoDB

### 1. **farmers** - Date fermieri
```javascript
{
  _id: ObjectId,
  first_name: String,
  last_name: String,
  cnp: String (unique),
  email: String,
  phone: String,
  age: Number,
  experience_years: Number,
  experience_level: Enum,
  total_parcels: Number,
  total_land_area: Number,
  has_equipment: Boolean,
  has_irrigation: Boolean,
  has_storage: Boolean,
  county: String,
  city: String,
  address: String,
  created_at: DateTime,
  updated_at: DateTime
}
```

### 2. **documents** - Documente uploadate
```javascript
{
  _id: ObjectId,
  farmer_id: String,
  document_type: Enum, // cni, certificate, parcel, cadastral
  filename: String,
  file_path: String,
  file_size: Number,
  mime_type: String,
  status: Enum, // uploaded, processing, processed, failed
  extracted_data: Object,
  ocr_confidence: Number,
  created_at: DateTime,
  processed_at: DateTime
}
```

### 3. **assessments** - Evaluări și scoruri
```javascript
{
  _id: ObjectId,
  farmer_id: String,
  bonitate_score: {
    soil_quality: Number,
    irrigation_access: Number,
    location_score: Number,
    infrastructure_score: Number,
    overall_score: Number
  },
  farmer_score: {
    experience_score: Number,
    education_score: Number,
    equipment_score: Number,
    financial_score: Number,
    overall_score: Number
  },
  risk_assessment: {
    risk_level: String, // low, medium, high
    risk_factors: [String],
    mitigation_suggestions: [String],
    confidence_score: Number
  },
  overall_rating: String, // excellent, good, average, poor
  eligibility_score: Number,
  recommendations: [String],
  created_at: DateTime
}
```

### 4. **applications** - Cereri CHM
```javascript
{
  _id: ObjectId,
  farmer_id: String,
  assessment_id: String,
  application_type: Enum, // subsidies, development_funds, young_farmer, etc.
  application_number: String (unique),
  requested_amount: Number,
  description: String,
  status: Enum, // draft, generated, submitted, approved, rejected
  chm_file_path: String,
  supporting_docs: [String],
  eligibility_check: Object,
  generated_at: DateTime,
  submitted_at: DateTime,
  created_at: DateTime
}
```

## 🔌 API Endpoints

### Farmers
- `POST /api/v1/farmers/` - Creare fermier
- `GET /api/v1/farmers/{id}` - Obtinere fermier
- `GET /api/v1/farmers/` - Listare fermieri
- `PUT /api/v1/farmers/{id}` - Update fermier
- `DELETE /api/v1/farmers/{id}` - Ștergere fermier
- `GET /api/v1/farmers/statistics/overview` - Statistici

### Documents
- `POST /api/v1/documents/upload` - Upload document
- `GET /api/v1/documents/{id}` - Obtinere document
- `GET /api/v1/documents/farmer/{farmer_id}` - Documente fermier
- `PATCH /api/v1/documents/{id}/status` - Update status
- `DELETE /api/v1/documents/{id}` - Ștergere document

### Assessments
- `POST /api/v1/assessments/` - Creare evaluare
- `GET /api/v1/assessments/{id}` - Obtinere evaluare
- `GET /api/v1/assessments/farmer/{farmer_id}/latest` - Ultima evaluare
- `GET /api/v1/assessments/farmer/{farmer_id}` - Toate evaluările

### Applications
- `POST /api/v1/applications/` - Creare cerere
- `GET /api/v1/applications/{id}` - Obtinere cerere
- `GET /api/v1/applications/farmer/{farmer_id}` - Cereri fermier
- `POST /api/v1/applications/{id}/generate` - Generare CHM
- `POST /api/v1/applications/{id}/submit` - Trimitere cerere
- `PATCH /api/v1/applications/{id}/status` - Update status

## 🤖 Utilizare AI Module

```python
from AI.processor import AIProcessor

# Inițializare processor
processor = AIProcessor()

# Procesare CNI
result = processor.process_document('path/to/cni.pdf', 'cni')
print(result['data']['extracted_data'])

# Generare CHM
chm_result = processor.generate_chm(
    output_path='output/CHM-2024-001.pdf',
    farmer_data={...},
    assessment_data={...},
    application_data={...}
)

# Generare raport evaluare
report_result = processor.generate_assessment_report(
    output_path='output/report.pdf',
    farmer_data={...},
    assessment_data={...}
)
```

## 🎯 Workflow Complet

1. **Înregistrare Fermier**
   ```
   POST /api/v1/farmers/
   → Creare profil în DB
   ```

2. **Upload Documente**
   ```
   POST /api/v1/documents/upload
   → Salvare fișier
   → Procesare OCR (automat sau manual)
   → Extragere date structurate
   ```

3. **Evaluare Automată**
   ```
   POST /api/v1/assessments/
   → Calculare bonitate teren
   → Scoring experiență fermier
   → Analiză risc
   → Generare recomandări
   ```

4. **Creare Cerere CHM**
   ```
   POST /api/v1/applications/
   → Verificare eligibilitate
   → Generare număr cerere
   ```

5. **Generare Documente**
   ```
   POST /api/v1/applications/{id}/generate
   → Generare PDF CHM
   → Anexare documente suport
   ```

6. **Trimitere Cerere**
   ```
   POST /api/v1/applications/{id}/submit
   → Validare finală
   → Schimbare status → SUBMITTED
   ```

## 📈 Scoring System

### Bonitate Teren (0-100)
- **Calitate sol** (30%): Bazat pe suprafață și clasificare
- **Acces irigații** (30%): Infrastructură apă
- **Locație** (20%): Proximitate urban, căi acces
- **Infrastructură** (20%): Echipamente, depozitare

### Scor Fermier (0-100)
- **Experiență** (30%): Ani de experiență
- **Educație** (25%): Nivel pregătire
- **Echipament** (25%): Dotări existente
- **Capacitate financiară** (20%): Resurse disponibile

### Rating Final
- **Excellent**: 85-100 - Eligibil pentru toate programele
- **Good**: 70-84 - Eligibil pentru majoritatea programelor
- **Average**: 50-69 - Necesită îmbunătățiri
- **Poor**: <50 - Nu recomandabil pentru finanțare

## 🔧 Configurare Avansată

### Custom Tesseract Path
```python
# În AI/processor.py
processor = AIProcessor(tesseract_path='/custom/path/to/tesseract')
```

### Custom MongoDB Settings
```python
# În Backend/.env
MONGO_API_KEY=your_connection_string
DATABASE_NAME=custom_db_name
```

### CORS Configuration
```python
# În Backend/app/config/settings.py
CORS_ORIGINS = [
    "http://localhost:3000",
    "https://yourdomain.com"
]
```

## 📝 Exemple de Utilizare

Vezi documentația API completă la:
- Swagger UI: `http://localhost:8000/api/docs`
- ReDoc: `http://localhost:8000/api/redoc`

## 🔐 Securitate

- Validare CNP românesc (13 cifre + control digit)
- Sanitizare fișiere uploadate
- Rate limiting (poate fi configurat)
- CORS configurat pentru domenii specifice

## 🐛 Debugging

```bash
# Backend cu debug mode
cd Backend
DEBUG=True python -m app.main

# Vezi logs MongoDB
# Logs sunt automat în consolă

# Test AI module
cd AI
python -c "from processor import AIProcessor; p = AIProcessor(); print('OK')"
```

## 📚 Dependințe Principale

**Backend:**
- FastAPI 0.115.0
- Motor (async MongoDB) 3.6.0
- Pydantic 2.9.2
- Uvicorn 0.32.0

**AI:**
- Pytesseract 0.3.13
- OpenCV 4.10.0
- ReportLab 4.2.5
- Pillow 10.4.0

**Frontend:**
- React 18.3.1
- TypeScript 5.8.3
- TailwindCSS 3.4.17
- shadcn/ui components

## 🚀 Deployment

### Docker (Recomandat)
```bash
# Coming soon - Dockerfile-uri pentru fiecare componentă
```

### Manual
1. Setup MongoDB Atlas sau local
2. Deploy Backend pe Railway/Render/DigitalOcean
3. Deploy Frontend pe Vercel/Netlify
4. Configurare variabile de mediu

## 📄 Licență

MIT License - Liber de utilizat pentru proiecte personale și comerciale.

## 👥 Contributors

Dezvoltat pentru Unihack 2025 - Future Farmers

---

**Note:** Sistemul este modular și poate fi extins cu:
- Integrări AI avansate (Computer Vision pentru analiză teren)
- Dashboard analytics
- Notificări email/SMS
- Portal fermieri
- Sistem de plăți
