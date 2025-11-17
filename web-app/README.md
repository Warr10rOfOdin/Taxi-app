# Voss Taxi Web App

A modern web application for managing taxi shift reports and salary calculations, converted from the desktop PySide6 application.

## Features

- **Shift Reports**: Upload Excel/DAT files and generate shift reports with cash adjustments
- **Salary Reports**: Calculate driver salaries based on commission percentages
- **Settings Management**: Configure company info, drivers, bank accounts, and templates
- **PDF Generation**: Export reports to professional PDF documents
- **Dark Mode**: Full dark mode support for comfortable viewing
- **Responsive Design**: Works on desktop, tablet, and mobile devices

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: SQL database ORM
- **SQLite**: Lightweight database (easily upgradable to PostgreSQL)
- **Pandas**: Data processing and analysis
- **FPDF**: PDF generation

### Frontend
- **React**: UI library
- **Vite**: Build tool and dev server
- **Tailwind CSS**: Utility-first CSS framework
- **React Router**: Client-side routing
- **Axios**: HTTP client

## Project Structure

```
web-app/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── database.py          # Database configuration
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── crud.py              # Database operations
│   ├── services.py          # Business logic
│   ├── requirements.txt     # Python dependencies
│   └── .env.example         # Environment variables template
│
└── frontend/
    ├── src/
    │   ├── api/             # API client
    │   ├── components/      # React components
    │   ├── context/         # React contexts
    │   ├── pages/           # Page components
    │   ├── App.jsx          # Main app component
    │   └── main.jsx         # Entry point
    ├── package.json         # Node dependencies
    └── vite.config.js       # Vite configuration
```

## Installation

### Prerequisites
- Python 3.9 or higher
- Node.js 18 or higher
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
```bash
cd web-app/backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```bash
cp .env.example .env
```

5. Update `.env` with your settings:
```
DATABASE_URL=sqlite:///./taxi_app.db
SECRET_KEY=your-secret-key-here
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd web-app/frontend
```

2. Install dependencies:
```bash
npm install
```

## Running the Application

### Start Backend

From the `backend` directory:
```bash
# With virtual environment activated
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`
API documentation at `http://localhost:8000/docs`

### Start Frontend

From the `frontend` directory:
```bash
npm run dev
```

The web app will be available at `http://localhost:3000`

## Usage Guide

### 1. Initial Setup

1. Go to **Settings** page
2. Add company information (name, org number, address)
3. Add drivers with their commission percentages
4. Add bank accounts (optional)
5. Create templates for reports (optional)

### 2. Creating Shift Reports

1. Go to **Shift Report** page
2. Select a driver (optional)
3. Upload Excel or DAT file
4. Review the preview
5. Click "Upload and Create Report"
6. Download PDF when ready

### 3. Creating Salary Reports

1. Go to **Salary Report** page
2. Select a driver (required)
3. Enter report period (optional)
4. Upload one or more Excel/DAT files
5. Click "Upload and Calculate Salary"
6. Review calculations and download PDF

### 4. Dark Mode

- Toggle dark mode from the sidebar
- Preference is saved in browser local storage

## API Endpoints

### Companies
- `GET /api/companies` - List all companies
- `POST /api/companies` - Create company
- `PUT /api/companies/{id}` - Update company
- `DELETE /api/companies/{id}` - Delete company

### Drivers
- `GET /api/drivers` - List all drivers
- `POST /api/drivers` - Create driver
- `PUT /api/drivers/{id}` - Update driver
- `DELETE /api/drivers/{id}` - Delete driver

### Bank Accounts
- `GET /api/bank-accounts` - List all bank accounts
- `POST /api/bank-accounts` - Create bank account
- `PUT /api/bank-accounts/{id}` - Update bank account
- `DELETE /api/bank-accounts/{id}` - Delete bank account

### Templates
- `GET /api/templates` - List all templates
- `POST /api/templates` - Create template
- `PUT /api/templates/{id}` - Update template
- `DELETE /api/templates/{id}` - Delete template

### Shift Reports
- `GET /api/reports/shift` - List shift reports
- `POST /api/reports/shift` - Create shift report
- `POST /api/reports/shift/{id}/pdf` - Generate PDF
- `DELETE /api/reports/shift/{id}` - Delete report

### Salary Reports
- `GET /api/reports/salary` - List salary reports
- `POST /api/reports/salary` - Create salary report
- `POST /api/reports/salary/{id}/pdf` - Generate PDF
- `DELETE /api/reports/salary/{id}` - Delete report

## Development

### Backend Development

```bash
# Run with auto-reload
uvicorn main:app --reload

# Run tests (to be implemented)
pytest
```

### Frontend Development

```bash
# Development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Production Deployment

### Backend

1. Update `.env` with production settings
2. Use PostgreSQL instead of SQLite for production
3. Set `SECRET_KEY` to a secure random string
4. Deploy using:
   - **Docker**: Create Dockerfile
   - **Heroku**: Use Procfile
   - **AWS/GCP**: Use cloud-specific deployment

### Frontend

1. Build the production bundle:
```bash
npm run build
```

2. Serve the `dist` folder using:
   - **Nginx**: Static file server
   - **Vercel**: Automatic deployment
   - **Netlify**: Automatic deployment

## Migration from Desktop App

The web app maintains all core functionality from the desktop application:

| Desktop Feature | Web App Status |
|----------------|----------------|
| Shift Reports | ✅ Implemented |
| Salary Reports | ✅ Implemented |
| Company Settings | ✅ Implemented |
| Driver Management | ✅ Implemented |
| Bank Accounts | ✅ Implemented |
| Templates | ✅ Implemented |
| Dark Mode | ✅ Implemented |
| PDF Generation | ✅ Implemented |
| Edit Tracking | ✅ Implemented |
| Schedule Management | ❌ Not implemented (was placeholder in desktop) |

## Troubleshooting

### Backend won't start
- Check Python version (3.9+)
- Ensure all dependencies are installed
- Check database file permissions

### Frontend won't start
- Check Node.js version (18+)
- Delete `node_modules` and run `npm install` again
- Check port 3000 is not in use

### CORS errors
- Ensure backend is running on port 8000
- Check CORS middleware configuration in `main.py`

### File upload fails
- Check file format (Excel or DAT)
- Ensure file is not corrupted
- Check backend logs for parsing errors

## Contributing

This is a company-internal application. For changes or improvements, please contact the development team.

## License

Proprietary - Voss Taxi

## Support

For technical support, please contact the system administrator.
