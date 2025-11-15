# Backend Setup Guide

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Verify .env configuration (already configured)
cat .env

# 3. Run the server
python run.py

# OR using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Environment Variables

The `.env` file is already configured with:
- `MONGO_API_KEY`: MongoDB connection string

Additional optional settings (in `app/config/settings.py`):
- `DATABASE_NAME`: Database name (default: farmer_assessment_db)
- `DEBUG`: Debug mode (default: False)
- `CORS_ORIGINS`: Allowed origins for CORS

## Testing the API

### Health Check
```bash
curl http://localhost:8000/health
```

### Create a Farmer
```bash
curl -X POST http://localhost:8000/api/v1/farmers/ \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Ion",
    "last_name": "Popescu",
    "cnp": "1800101123456",
    "email": "ion@example.com",
    "phone": "0712345678",
    "age": 45,
    "experience_years": 20,
    "experience_level": "advanced",
    "total_parcels": 3,
    "total_land_area": 15.5,
    "has_equipment": true,
    "has_irrigation": true,
    "has_storage": true,
    "county": "Ilfov",
    "city": "Bucuresti",
    "address": "Str. Agricultorilor nr. 10"
  }'
```

### Get All Farmers
```bash
curl http://localhost:8000/api/v1/farmers/
```

### Create Assessment
```bash
# First, get a farmer_id from the previous step
curl -X POST http://localhost:8000/api/v1/assessments/ \
  -H "Content-Type: application/json" \
  -d '{"farmer_id": "YOUR_FARMER_ID_HERE"}'
```

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

## Database Structure

The backend automatically creates indexes on:
- Farmers: `cnp` (unique), `email`, `created_at`
- Documents: `farmer_id`, `document_type`, `status`
- Assessments: `farmer_id`, `created_at`
- Applications: `farmer_id`, `application_type`, `status`

## Troubleshooting

### MongoDB Connection Issues
- Verify the `MONGO_API_KEY` in `.env`
- Check network connectivity
- Ensure MongoDB Atlas IP whitelist includes your IP

### Import Errors
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Use Python 3.9+

### Port Already in Use
- Change the port in `run.py`: `uvicorn.run(app, port=8001)`
- Or kill the process using port 8000: `lsof -ti:8000 | xargs kill`

## Development

### Project Structure
```
Backend/
├── app/
│   ├── config/       # Configuration
│   ├── models/       # Pydantic models
│   ├── services/     # Business logic
│   ├── routes/       # API endpoints
│   ├── utils/        # Utilities
│   └── main.py       # FastAPI app
├── requirements.txt
├── run.py           # Quick start script
└── .env             # Environment variables
```

### Adding New Features

1. **New Model**: Add to `app/models/`
2. **New Service**: Add to `app/services/`
3. **New Route**: Add to `app/routes/` and include in `main.py`

### Code Style
- Follow PEP 8
- Use type hints
- Document functions with docstrings
- Keep functions focused and modular

## Production Deployment

### Using Gunicorn
```bash
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Environment Variables for Production
```env
DEBUG=False
MONGO_API_KEY=your_production_mongodb_url
CORS_ORIGINS=["https://yourdomain.com"]
```

### Docker (Optional)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```
