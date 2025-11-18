# Voss Taxi Web Application

Modern, secure web application for managing taxi shift reports and salary calculations with user authentication.

## 🔐 Authentication Required

All users must register and log in to access the application. The app includes:
- User registration and login
- JWT token-based authentication
- Session management
- Protected routes

## 🚀 Quick Start

### Local Development

See the complete **[SETUP_CHECKLIST.md](./SETUP_CHECKLIST.md)** for step-by-step instructions.

**Quick overview:**

1. **Start Backend:**
```bash
cd web-app/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

2. **Start Frontend:**
```bash
cd web-app/frontend
npm install
npm run dev
```

3. **Access the app:** http://localhost:3000
4. **Create your first account** via the registration page

### Production Deployment

For production deployment to Vercel, see **[SETUP_CHECKLIST.md](./SETUP_CHECKLIST.md)** which includes:
- Database setup (Supabase)
- Environment variables configuration
- Backend and frontend deployment
- Domain configuration
- First user registration

## 📚 Documentation

- **[SETUP_CHECKLIST.md](./SETUP_CHECKLIST.md)** - Complete setup and verification checklist
- **[ENVIRONMENT_VARIABLES.md](./ENVIRONMENT_VARIABLES.md)** - Environment variables reference
- **[web-app/AUTH_GUIDE.md](./web-app/AUTH_GUIDE.md)** - Authentication system guide
- **[web-app/README.md](./web-app/README.md)** - Technical documentation

**Archived guides** (for reference only): See `docs-archive/` folder

## 🛠 Development Workflow

1. **Backend** runs on `http://localhost:8000`
   - API docs at `http://localhost:8000/docs`
   - Health check at `http://localhost:8000`

2. **Frontend** runs on `http://localhost:3000` (or `http://localhost:5173` with Vite)
   - Automatically connects to backend
   - Hot reload enabled

3. **First Time:**
   - Register a new account
   - Start adding company info, drivers, and bank accounts in Settings
   - Create shift and salary reports

## ✨ Features

- **Shift Reports** - Upload Excel/DAT files, generate reports with PDF export
- **Salary Reports** - Calculate driver salaries with commission rates
- **Settings Management** - Manage company info, drivers, bank accounts
- **Dark Mode** - Full dark mode support
- **Responsive** - Works on desktop, tablet, and mobile
- **PDF Generation** - Professional PDF reports
- **Real-time Updates** - Live data synchronization

## 🏗 Architecture

```
Frontend (React + Vite)
    ↓
Backend (FastAPI)
    ↓
Database (PostgreSQL via Supabase)
```

**Frontend:** https://voss-taxi.app
**Backend API:** https://api.voss-taxi.app
**API Docs:** https://api.voss-taxi.app/docs

## 📦 Technology Stack

### Backend
- FastAPI - Modern Python web framework
- SQLAlchemy - SQL database ORM
- PostgreSQL - Production database
- Pandas - Data processing
- FPDF - PDF generation

### Frontend
- React 18 - UI library
- Vite - Build tool
- Tailwind CSS - Styling
- React Router - Routing
- Axios - HTTP client

## 🔐 Security

- HTTPS enforced (automatic with Vercel)
- Environment variables for secrets
- CORS protection
- SQL injection prevention (SQLAlchemy ORM)
- Input validation (Pydantic schemas)

## 📊 Database Schema

- **companies** - Company information
- **drivers** - Driver profiles with commission rates
- **bank_accounts** - Bank account details
- **templates** - Report templates
- **shift_reports** - Shift report data
- **salary_reports** - Salary calculations

## 🚦 Deployment Status

Once deployed, check status:

- [ ] Backend deployed to Vercel
- [ ] Frontend deployed to Vercel
- [ ] Custom domains configured
- [ ] DNS records added
- [ ] SSL certificates issued
- [ ] Database connected
- [ ] Application tested

## 🐛 Troubleshooting

**Can't connect to API?**
- Check CORS settings in backend
- Verify VITE_API_URL in frontend
- Ensure DNS has propagated

**Database errors?**
- Check DATABASE_URL format
- Use pooler connection (port 6543)
- Verify Supabase is connected

**Build failures?**
- Check all environment variables are set
- Review deployment logs in Vercel
- Ensure correct root directory

## 📞 Support

- Check deployment guides in this repository
- Review Vercel deployment logs
- Check browser console for frontend errors
- Verify environment variables are set correctly

## 🎯 Next Steps After Deployment

1. Visit https://voss-taxi.app
2. Go to Settings
3. Add your company information
4. Add drivers and their commission rates
5. Add bank accounts
6. Start creating shift and salary reports!

## 📝 License

Proprietary - Voss Taxi

---

**Need help?** See [DEPLOYMENT_GUIDE_voss-taxi-app.md](./DEPLOYMENT_GUIDE_voss-taxi-app.md) for detailed instructions.
