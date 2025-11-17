# Voss Taxi Web Application

Modern web application for managing taxi shift reports and salary calculations.

## 🚀 Quick Deploy to voss-taxi.app

Your application is ready to deploy with:
- **Domain:** voss-taxi.app
- **Database:** Supabase (connected in Vercel)
- **Hosting:** Vercel

### Deploy Now (15 minutes)

Follow this guide: **[DEPLOYMENT_GUIDE_voss-taxi-app.md](./DEPLOYMENT_GUIDE_voss-taxi-app.md)**

Or follow these quick steps:

#### 1. Deploy Backend
1. Import to Vercel: [vercel.com/new](https://vercel.com/new)
2. Root Directory: `web-app/backend`
3. Add environment variables (see [ENVIRONMENT_VARIABLES.md](./ENVIRONMENT_VARIABLES.md))
4. Deploy
5. Add custom domain: `api.voss-taxi.app`

#### 2. Deploy Frontend
1. Import to Vercel again: [vercel.com/new](https://vercel.com/new)
2. Root Directory: `web-app/frontend`
3. Add env var: `VITE_API_URL=https://api.voss-taxi.app`
4. Deploy
5. Add custom domain: `voss-taxi.app`

#### 3. Configure DNS

Add these records to your domain registrar:

| Type  | Name | Value                 |
|-------|------|-----------------------|
| A     | @    | 76.76.21.21          |
| CNAME | www  | cname.vercel-dns.com |
| CNAME | api  | cname.vercel-dns.com |

Done! Visit https://voss-taxi.app 🎉

## 📚 Documentation

- **[DEPLOYMENT_GUIDE_voss-taxi-app.md](./DEPLOYMENT_GUIDE_voss-taxi-app.md)** - Complete deployment guide
- **[ENVIRONMENT_VARIABLES.md](./ENVIRONMENT_VARIABLES.md)** - All environment variables explained
- **[VERCEL_DEPLOYMENT.md](./VERCEL_DEPLOYMENT.md)** - General Vercel deployment guide
- **[web-app/README.md](./web-app/README.md)** - Technical documentation
- **[web-app/CONVERSION_SUMMARY.md](./web-app/CONVERSION_SUMMARY.md)** - Desktop to web conversion details

## 🛠 Local Development

### Backend
```bash
cd web-app/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend
```bash
cd web-app/frontend
npm install
npm run dev
```

Visit http://localhost:3000

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
