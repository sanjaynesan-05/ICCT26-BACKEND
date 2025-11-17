# 📁 Testing Directory

This directory contains all testing scripts and tools for the ICCT26 Backend API.

## 🧪 Test Files

### Unit & Integration Tests
- **`test_backend_complete.py`** - Comprehensive unit tests (23 tests)
  - Tests imports, Cloudinary functions, file validation
  - Tests error handlers, FastAPI config, database setup
  - Run: `python testing/test_backend_complete.py`

- **`test_integration_live.py`** - Live integration tests (14 tests)
  - Tests actual HTTP endpoints with running server
  - Tests CORS, admin endpoints, error handling
  - Run: `python testing/test_integration_live.py`

### Frontend Compatibility Tests
- **`test_frontend_compatibility.py`** - Frontend integration test (10 tests)
  - Tests backend-frontend compatibility
  - Validates CORS configuration
  - Run: `python testing/test_frontend_compatibility.py`

- **`test_frontend_browser.html`** - Browser-based visual test
  - Interactive web interface for testing
  - Auto-runs compatibility tests
  - Open in browser to use

### Legacy Test Files (Old)
- `test_admin_urls.py` - Admin endpoint tests
- `test_cloudinary_integration.py` - Cloudinary integration tests
- `test_production_endpoints.py` - Production endpoint tests
- `test_production_render.py` - Render deployment tests
- `test_render_api.py` - Render API tests
- `test_cors.sh` - CORS configuration test script
- `test_quick.sh` - Quick test script

## 🚀 Quick Start

### Run All Tests
```bash
# Unit tests
python testing/test_backend_complete.py

# Integration tests (requires server running)
python testing/test_integration_live.py

# Frontend compatibility
python testing/test_frontend_compatibility.py
```

### Test Results Summary
- **Unit Tests**: 23/23 passed ✅
- **Integration Tests**: 14/14 passed ✅
- **Frontend Compatibility**: 10/10 passed ✅
- **Total**: 47/47 tests passed (100%)

## 📊 Test Coverage

### Tested Components
✅ FastAPI application initialization  
✅ Database connections (async + sync)  
✅ Cloudinary integration  
✅ File upload and validation  
✅ Error handling  
✅ CORS configuration  
✅ API endpoints  
✅ Response formats  
✅ Admin panel routes  

## 🔧 Requirements

All test files require:
- Python 3.13+
- Active virtual environment
- Backend server running (for integration tests)
- All dependencies installed: `pip install -r requirements.txt`

## 📝 Notes

- Run unit tests first (no server needed)
- Start server before running integration tests
- Frontend compatibility tests validate CORS and endpoints
- Browser test provides visual feedback
