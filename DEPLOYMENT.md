# QuantDash Deployment Guide

## 🚀 Render.com Deployment

### Option A: Manual Deployment (Recommended)

#### Backend Deployment:
1. **Create Web Service** on Render.com
2. **Connect GitHub Repository**
3. **Configure Service:**
   - **Name**: `quantdash-backend`
   - **Environment**: `Python 3`
   - **Region**: Choose closest to your users
   - **Branch**: `master`
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r ../requirements.txt`
   - **Start Command**: `python src/api/server.py`

4. **Environment Variables:**
   ```
   PYTHONPATH=/opt/render/project/src/backend/src
   PORT=8000
   ```

#### Frontend Deployment:
1. **Create Static Site** on Render.com
2. **Connect Same GitHub Repository**
3. **Configure Service:**
   - **Name**: `quantdash-frontend`
   - **Environment**: `Static Site`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm ci && npm run build`
   - **Publish Directory**: `dist`

4. **Environment Variables:**
   ```
   VITE_API_BASE_URL=https://quantdash-backend.onrender.com/api
   ```

### Option B: Infrastructure as Code

1. **Push render.yaml** to your repository
2. **Connect to Render** via Blueprint
3. **Deploy both services** automatically

---

## 🐳 Docker Deployment

### Local Testing:
```bash
# Build and run with Docker Compose
docker-compose up --build

# Access application
open http://localhost
```

### Production Docker:
```bash
# Build backend
docker build -f Dockerfile.backend -t quantdash-backend .

# Build frontend
docker build -f Dockerfile.frontend -t quantdash-frontend .

# Run containers
docker run -d -p 8000:8000 quantdash-backend
docker run -d -p 80:80 quantdash-frontend
```

---

## 🔧 Environment Configuration

### Development (.env.local):
```
VITE_API_BASE_URL=http://localhost:8000/api
```

### Production (.env.production):
```
VITE_API_BASE_URL=https://quantdash-backend.onrender.com/api
```

---

## 📋 Pre-Deployment Checklist

### Backend Ready:
- [ ] All dependencies in requirements.txt
- [ ] CORS configured for production domains
- [ ] Environment variables support
- [ ] Health check endpoints added
- [ ] Error handling implemented

### Frontend Ready:
- [ ] Production build working (`npm run build`)
- [ ] Environment variables configured
- [ ] API URLs pointing to production
- [ ] Static assets optimized
- [ ] Mobile responsiveness tested

### General:
- [ ] All secrets removed from code
- [ ] Database/cache strategy defined
- [ ] Monitoring/logging configured
- [ ] Performance optimized
- [ ] Security headers added

---

## 🚦 Testing Deployment

### 1. Local Production Test:
```bash
# Test backend
cd backend && python src/api/server.py

# Test frontend build
cd frontend && npm run build && npm run preview
```

### 2. Verify API Endpoints:
```bash
curl https://quantdash-backend.onrender.com/health
curl https://quantdash-backend.onrender.com/api/tickers
```

### 3. Frontend Verification:
- [ ] Application loads
- [ ] API calls work
- [ ] Charts render correctly
- [ ] Mobile responsive
- [ ] All strategies functional

---

## 🔒 Security Considerations

1. **CORS**: Restrict to production domains only
2. **HTTPS**: Ensure all API calls use HTTPS
3. **Rate Limiting**: Consider adding API rate limits
4. **Environment Variables**: Never commit secrets
5. **Input Validation**: Validate all user inputs

---

## 📊 Monitoring & Maintenance

### Health Checks:
- Backend: `https://quantdash-backend.onrender.com/health`
- Frontend: Monitor loading time and functionality

### Performance:
- Monitor API response times
- Track memory usage
- Monitor error rates

### Updates:
1. Test changes locally
2. Deploy to staging (if available)
3. Deploy to production
4. Verify functionality

---

## 🆘 Troubleshooting

### Common Issues:

**"Module not found" errors:**
- Check PYTHONPATH environment variable
- Verify all imports use relative paths

**CORS errors:**
- Update allowed origins in server.py
- Check environment variable URLs

**Build failures:**
- Check Node.js version compatibility
- Verify all dependencies are listed
- Clear cache and rebuild

**API connection failures:**
- Verify backend URL in environment variables
- Check backend service logs
- Test endpoints manually

---

## 📞 Support

- **Documentation**: See main README.md
- **Issues**: GitHub Issues
- **Logs**: Check Render service logs for debugging
