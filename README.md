# CantiereTrack

A complete full-stack application for managing employee attendance across multiple construction sites.

## Features

- **Employee Management**: Create, update, and manage employee profiles with badge codes and roles
- **Construction Site Management**: Track multiple construction sites with detailed information
- **Attendance Tracking**: Clock-in and clock-out functionality with automatic hour calculation
- **Reporting**: Generate detailed reports per employee or site with CSV export capability
- **JWT Authentication**: Secure authentication system
- **PWA Support**: Progressive Web App capabilities for offline use and mobile installation
- **Modern UI**: Clean, responsive interface built with Next.js and Tailwind CSS

## Technology Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Migrations**: Alembic
- **Authentication**: JWT (JSON Web Tokens)
- **Validation**: Pydantic

### Frontend
- **Framework**: Next.js 14 (React)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **PWA**: next-pwa
- **HTTP Client**: Axios

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Database**: PostgreSQL 15

## Project Structure

```
cantiere-track/
├── backend/
│   ├── app/
│   │   ├── core/           # Configuration, database, security
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── routers/        # API endpoints
│   │   └── main.py         # FastAPI application
│   ├── alembic/            # Database migrations
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── app/                # Next.js pages (App Router)
│   ├── components/         # React components
│   ├── lib/                # Utilities and API client
│   ├── public/             # Static files and PWA assets
│   ├── Dockerfile
│   └── package.json
└── docker-compose.yml
```

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Git

### Installation & Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd cantiere-track
   ```

2. **Configure environment variables**

   Backend:
   ```bash
   cd backend
   cp .env.example .env
   # Edit .env and change SECRET_KEY to a secure random string
   ```

   Frontend:
   ```bash
   cd ../frontend
   cp .env.example .env
   # Adjust NEXT_PUBLIC_API_URL if needed (default: http://localhost:8000)
   ```

3. **Start the application**
   ```bash
   cd ..
   docker-compose up --build
   ```

   This will start:
   - PostgreSQL database on port 5432
   - Backend API on http://localhost:8000
   - Frontend web app on http://localhost:3000

4. **Create your first user**

   Open your browser and go to http://localhost:3000

   The app will redirect you to the login page. First, you need to create a user account:

   You can use the FastAPI interactive docs at http://localhost:8000/docs to register:
   - Navigate to `/api/auth/register`
   - Click "Try it out"
   - Fill in the registration details
   - Execute the request

   Or use curl:
   ```bash
   curl -X POST "http://localhost:8000/api/auth/register" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "admin",
       "email": "admin@example.com",
       "password": "admin123",
       "full_name": "Admin User"
     }'
   ```

5. **Login and start using the app**

   Go to http://localhost:3000/login and use your credentials to log in.

## Development

### Running Backend Separately

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env

# Run migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload
```

### Running Frontend Separately

```bash
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env

# Start development server
npm run dev
```

### Database Migrations

Create a new migration:
```bash
cd backend
alembic revision --autogenerate -m "Description of changes"
```

Apply migrations:
```bash
alembic upgrade head
```

Rollback migration:
```bash
alembic downgrade -1
```

## API Documentation

Once the backend is running, you can access:
- **Interactive API docs (Swagger)**: http://localhost:8000/docs
- **Alternative API docs (ReDoc)**: http://localhost:8000/redoc

## Main API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token

### Employees
- `GET /api/employees/` - List all employees
- `POST /api/employees/` - Create new employee
- `GET /api/employees/{id}` - Get employee by ID
- `PUT /api/employees/{id}` - Update employee
- `DELETE /api/employees/{id}` - Delete employee

### Sites
- `GET /api/sites/` - List all construction sites
- `POST /api/sites/` - Create new site
- `GET /api/sites/{id}` - Get site by ID
- `PUT /api/sites/{id}` - Update site
- `DELETE /api/sites/{id}` - Delete site

### Attendance
- `POST /api/attendance/clock-in` - Clock in an employee
- `PUT /api/attendance/{id}/clock-out` - Clock out an employee
- `GET /api/attendance/` - List attendance records
- `GET /api/attendance/employee/{id}/active` - Get active attendance for employee

### Reports
- `GET /api/reports/employee/{id}` - Get employee attendance report
- `GET /api/reports/site/{id}` - Get site attendance report
- `GET /api/reports/employee/{id}/csv` - Download employee report as CSV
- `GET /api/reports/site/{id}/csv` - Download site report as CSV

## PWA Features

The frontend is a Progressive Web App (PWA) that supports:

- **Offline Caching**: Core functionality available offline
- **Installable**: Can be installed on mobile devices and desktops
- **App-like Experience**: Runs in standalone mode without browser UI

To install on mobile:
1. Open http://localhost:3000 (or your production URL) in a mobile browser
2. Look for "Add to Home Screen" or "Install" prompt
3. Follow the installation steps

**Note**: For PWA to work properly in production, you need HTTPS.

## Production Deployment

### Environment Variables

Make sure to set secure values for production:

Backend (.env):
```env
SECRET_KEY=<generate-a-secure-random-string-min-32-chars>
DEBUG=False
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

Frontend (.env):
```env
NEXT_PUBLIC_API_URL=https://your-api-domain.com
```

### Building for Production

```bash
# Build images
docker-compose build

# Run in production mode
docker-compose up -d
```

### Security Considerations

1. **Change default passwords** in docker-compose.yml for PostgreSQL
2. **Generate a secure SECRET_KEY** for JWT tokens (min 32 characters)
3. **Use HTTPS** in production (required for PWA)
4. **Set up proper CORS origins** in backend/app/core/config.py
5. **Enable firewall** and limit database access
6. **Regular backups** of PostgreSQL database

## Database Backup & Restore

### Backup
```bash
docker-compose exec db pg_dump -U cantieretrack cantieretrack > backup.sql
```

### Restore
```bash
docker-compose exec -T db psql -U cantieretrack cantieretrack < backup.sql
```

## Troubleshooting

### Backend not connecting to database
- Ensure PostgreSQL is running: `docker-compose ps`
- Check database logs: `docker-compose logs db`
- Verify DATABASE_URL in backend/.env

### Frontend can't connect to API
- Check NEXT_PUBLIC_API_URL in frontend/.env
- Verify backend is running on the correct port
- Check CORS settings in backend/app/core/config.py

### Migrations failing
- Ensure database is accessible
- Check alembic/env.py configuration
- Try: `docker-compose down -v` and restart (WARNING: deletes data)

## Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

[Your License Here]

## Support

For issues and questions, please open an issue on GitHub.
