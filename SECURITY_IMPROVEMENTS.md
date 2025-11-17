# Security, Performance & Features Improvements

Questo documento descrive i miglioramenti implementati per aumentare la sicurezza, le prestazioni e le funzionalità di CantiereTrack.

## 🔒 Security Improvements

### 1. SECRET_KEY Validation & Management

**Problema**: SECRET_KEY hardcoded nel codice rappresentava un grave rischio di sicurezza.

**Soluzione**:
- Aggiunto validatore automatico che impedisce l'uso di chiavi insicure in produzione
- Variabile `ENVIRONMENT` per distinguere development/staging/production
- Script helper per generare chiavi sicure
- Documentazione chiara in `.env.example`

**File modificati**:
- `backend/app/core/config.py`
- `backend/.env.example`

**Uso**:
```python
# Genera una SECRET_KEY sicura
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Configurazione**:
```env
# .env
ENVIRONMENT=production
SECRET_KEY=<your-generated-secret-key>
```

---

### 2. Rate Limiting

**Problema**: Nessuna protezione contro attacchi brute force su login/registrazione.

**Soluzione**:
- Implementato `slowapi` per rate limiting
- Limiti configurabili tramite variabili d'ambiente
- Applicato a `/api/auth/login` (5 tentativi/minuto)
- Applicato a `/api/auth/register` (3 registrazioni/minuto)

**File modificati**:
- `backend/requirements.txt` (aggiunto slowapi)
- `backend/app/main.py` (configurazione limiter)
- `backend/app/routers/auth.py` (applicazione rate limits)
- `backend/app/core/config.py` (configurazione)

**Configurazione**:
```env
RATE_LIMIT_ENABLED=True
LOGIN_RATE_LIMIT=5/minute
REGISTER_RATE_LIMIT=3/minute
```

---

### 3. Password Strength Validation

**Problema**: Password deboli accettate dal sistema.

**Soluzione**:
- Validazione automatica con Pydantic validators
- Requisiti configurabili:
  - Lunghezza minima (default: 8 caratteri)
  - Almeno 1 lettera maiuscola
  - Almeno 1 numero
  - Opzionale: caratteri speciali
- Blocco di password comuni (password, 12345678, qwerty, etc.)

**File modificati**:
- `backend/app/schemas/user.py`
- `backend/app/core/config.py`

**Configurazione**:
```env
PASSWORD_MIN_LENGTH=8
REQUIRE_UPPERCASE=True
REQUIRE_DIGIT=True
REQUIRE_SPECIAL_CHAR=False
```

**Esempi**:
```python
# ✓ Password valide
"MySecure123"
"CantiereTrack2024"

# ✗ Password rifiutate
"password"     # Troppo comune
"Short1"       # Troppo corta
"nouppercase1" # Manca maiuscola
"NODIGITS"     # Manca numero
```

---

## ⚡ Performance Improvements

### 1. N+1 Query Problem Fix

**Problema**: Nei reports, per ogni attendance veniva eseguita una query separata per recuperare employee/site, causando:
- Report con 100 attendance = 201 query (1 + 100 + 100)
- Prestazioni molto scarse su dataset grandi

**Soluzione**:
- Implementato **eager loading** con `joinedload()`
- Tutte le relazioni caricate in una singola query JOIN
- Report con 100 attendance = 1 query

**File modificati**:
- `backend/app/routers/reports.py`

**Risultato**:
```python
# Prima (N+1 problem)
attendances = query.all()  # 1 query
for att in attendances:
    site = db.query(Site).filter(Site.id == att.site_id).first()  # N query

# Dopo (eager loading)
attendances = query.options(joinedload(Attendance.site)).all()  # 1 query JOIN
for att in attendances:
    site = att.site  # Già caricato, 0 query
```

**Performance gain**: ~99% di riduzione delle query per i reports!

---

## 🎯 New Features

### 1. RBAC (Role-Based Access Control)

**Descrizione**: Sistema di autorizzazione basato su ruoli per controllare l'accesso alle funzionalità.

**Ruoli disponibili**:
- **ADMIN**: Accesso completo a tutte le funzionalità
- **MANAGER**: Gestione dipendenti, cantieri, presenze, visualizzazione reports
- **VIEWER**: Sola lettura di dati e reports

**Implementazione**:
- Enum `UserRole` nel database
- Migration automatica per aggiungere campo `role`
- Helper dependencies per proteggere endpoint
- Backward compatibility con campo `is_superuser`

**File aggiunti**:
- `backend/alembic/versions/20251117_add_user_role.py`

**File modificati**:
- `backend/app/models/user.py`
- `backend/app/schemas/user.py`
- `backend/app/core/dependencies.py`
- `backend/app/routers/auth.py`

**Uso nei router**:
```python
from app.core.dependencies import require_admin, require_manager_or_admin

# Solo admin
@router.delete("/employees/{id}", dependencies=[Depends(require_admin)])
async def delete_employee(id: int):
    ...

# Manager o Admin
@router.post("/employees/", dependencies=[Depends(require_manager_or_admin)])
async def create_employee(employee_data: EmployeeCreate):
    ...

# Tutti gli utenti autenticati
@router.get("/reports/{id}", dependencies=[Depends(get_current_active_user)])
async def get_report(id: int):
    ...
```

**Applicazione RBAC**:
Per applicare RBAC agli endpoint esistenti, aggiungere le dependencies appropriate:
```python
# Esempio per employees router
@router.post("/", dependencies=[Depends(require_manager_or_admin)])
@router.put("/{id}", dependencies=[Depends(require_manager_or_admin)])
@router.delete("/{id}", dependencies=[Depends(require_admin)])
```

---

### 2. Audit Logging

**Descrizione**: Sistema di logging per tracciare tutte le azioni critiche degli utenti.

**Informazioni tracciate**:
- User ID (chi ha fatto l'azione)
- Action (tipo di azione: login, create_employee, delete_site, etc.)
- Resource Type e ID (cosa è stato modificato)
- Details (JSON con contesto aggiuntivo)
- IP Address (da dove è stata fatta l'azione)
- User Agent (browser/client)
- Timestamp (quando)

**File aggiunti**:
- `backend/app/models/audit_log.py`
- `backend/app/core/audit.py`
- `backend/alembic/versions/20251117_add_audit_logs.py`

**File modificati**:
- `backend/app/routers/auth.py` (logging login/register)

**Uso**:
```python
from app.core.audit import log_action, AuditAction

# Log di un'azione
log_action(
    db=db,
    action=AuditAction.CREATE_EMPLOYEE,
    user=current_user,
    resource_type="employee",
    resource_id=new_employee.id,
    details={"name": new_employee.name, "role": new_employee.role},
    request=request
)
```

**Azioni predefinite**:
```python
# Authentication
AuditAction.LOGIN
AuditAction.LOGOUT
AuditAction.REGISTER
AuditAction.PASSWORD_CHANGE

# Employee management
AuditAction.CREATE_EMPLOYEE
AuditAction.UPDATE_EMPLOYEE
AuditAction.DELETE_EMPLOYEE

# Site management
AuditAction.CREATE_SITE
AuditAction.UPDATE_SITE
AuditAction.DELETE_SITE

# Attendance
AuditAction.CLOCK_IN
AuditAction.CLOCK_OUT
AuditAction.ADD_MANUAL_HOURS
AuditAction.UPDATE_ATTENDANCE
AuditAction.DELETE_ATTENDANCE

# Reports
AuditAction.EXPORT_REPORT
AuditAction.VIEW_REPORT
```

**Query audit logs**:
```python
# Tutte le azioni di un utente
logs = db.query(AuditLog).filter(AuditLog.user_id == user_id).all()

# Tutti i login
logins = db.query(AuditLog).filter(AuditLog.action == AuditAction.LOGIN).all()

# Azioni nelle ultime 24h
from datetime import datetime, timedelta
since = datetime.utcnow() - timedelta(hours=24)
recent = db.query(AuditLog).filter(AuditLog.created_at >= since).all()
```

---

### 3. Enhanced Health Check Endpoint

**Descrizione**: Endpoint `/health` migliorato per monitoring e diagnostica.

**Informazioni restituite**:
- Status generale (healthy/unhealthy)
- Timestamp della verifica
- Versione applicazione
- Environment (development/production)
- **Database connectivity** (nuovo!)
- **System metrics** (CPU, RAM, Disk - nuovo!)

**File modificati**:
- `backend/app/main.py`
- `backend/requirements.txt` (aggiunto psutil)

**Risposta esempio**:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-17T10:30:00.000000",
  "version": "1.0.0",
  "environment": "production",
  "database": "connected",
  "system": {
    "cpu_percent": 15.2,
    "memory_percent": 42.8,
    "disk_percent": 68.5
  }
}
```

**Uso per monitoring**:
```bash
# Verifica salute applicazione
curl http://localhost:8000/health

# Monitoraggio continuo (ogni 30 secondi)
watch -n 30 'curl -s http://localhost:8000/health | jq'

# Alert se database disconnesso
curl -s http://localhost:8000/health | jq -e '.database == "connected"' || echo "ALERT: DB down!"
```

---

### 4. Database Initialization Script

**Descrizione**: Script interattivo per inizializzare il database e creare utenti admin.

**Funzionalità**:
- Creazione automatica tabelle
- Creazione guidata utente admin
- Validazione input (password, email, etc.)
- Statistiche database
- Password sicura con conferma

**File aggiunti**:
- `backend/scripts/init_db.py`

**Uso**:
```bash
cd backend
python scripts/init_db.py
```

**Output esempio**:
```
==================================================
CantiereTrack Database Initialization
==================================================
Creating database tables...
✓ Tables created successfully

=== Database Statistics ===
Users: 0 (Admin: 0, Manager: 0, Viewer: 0)
Employees: 0
Sites: 0
Attendance records: 0
Audit logs: 0

Create admin user? (Y/n): y

=== Create Admin User ===
Admin username: admin
Admin email: admin@cantiere.local
Full name (optional): System Administrator
Password (min 8 chars, 1 uppercase, 1 digit):
Confirm password:

✓ Admin user 'admin' created successfully
  Email: admin@cantiere.local
  Role: admin

=== Database Statistics ===
Users: 1 (Admin: 1, Manager: 0, Viewer: 0)
Employees: 0
Sites: 0
Attendance records: 0
Audit logs: 1

✓ Initialization complete!
```

---

## 📋 Migration Checklist

Per applicare tutti i miglioramenti:

### 1. Installare nuove dipendenze
```bash
cd backend
pip install -r requirements.txt
```

### 2. Applicare migrations
```bash
cd backend
alembic upgrade head
```

Migrations applicate:
- `20251117_add_role`: Aggiunge campo `role` alla tabella `users`
- `20251117_add_audit`: Crea tabella `audit_logs`

### 3. Creare utente admin
```bash
python scripts/init_db.py
```

### 4. Configurare variabili ambiente
```bash
cp .env.example .env
# Editare .env e configurare:
# - ENVIRONMENT=production
# - SECRET_KEY=<chiave-sicura-generata>
# - RATE_LIMIT_ENABLED=True
# - PASSWORD_MIN_LENGTH=8
```

### 5. Restart applicazione
```bash
docker-compose down
docker-compose up --build
```

### 6. Verificare funzionamento
```bash
# Health check
curl http://localhost:8000/health

# Test rate limiting (dovrebbe bloccare dopo 5 tentativi)
for i in {1..10}; do
  curl -X POST http://localhost:8000/api/auth/login \
    -d "username=test&password=wrong"
  echo ""
done
```

---

## 🔐 Security Best Practices

### Produzione
1. ✅ **SECRET_KEY sicura**: Generare con `secrets.token_urlsafe(32)`
2. ✅ **ENVIRONMENT=production**: Abilita validazioni stringenti
3. ✅ **Rate limiting attivo**: Previene brute force
4. ✅ **Password forti**: Minimo 8 caratteri, maiuscola, numero
5. ✅ **HTTPS obbligatorio**: Per PWA e sicurezza
6. ⚠️ **CORS configurato**: Solo origini trusted in `CORS_ORIGINS`
7. ⚠️ **Database password**: Cambiare in `docker-compose.yml`
8. ⚠️ **Backup regolari**: Schedulare backup automatici

### Development
1. ✅ **ENVIRONMENT=development**: Permette chiavi di test
2. ✅ **DEBUG=True**: Logging dettagliato
3. ⚠️ **Non usare SECRET_KEY di produzione**: Mai!

---

## 📊 Performance Monitoring

### Query Performance
```python
# Abilitare SQL logging (development only!)
# In app/core/database.py
engine = create_engine(DATABASE_URL, echo=True)  # Mostra tutte le query
```

### Health Check Monitoring
```bash
# Setup Prometheus/Grafana per monitoring continuo
# Endpoint: /health restituisce metriche JSON

# Alert example (bash)
#!/bin/bash
HEALTH=$(curl -s http://localhost:8000/health)
STATUS=$(echo $HEALTH | jq -r '.status')
DB=$(echo $HEALTH | jq -r '.database')

if [ "$STATUS" != "healthy" ] || [ "$DB" != "connected" ]; then
    echo "ALERT: System unhealthy!"
    # Invia notifica (email, Slack, etc.)
fi
```

---

## 🚀 Future Improvements

Possibili estensioni future:

### Security
- [ ] JWT Refresh Tokens (già preparato in config)
- [ ] Two-Factor Authentication (2FA)
- [ ] Password reset via email
- [ ] Session management (revoke tokens)
- [ ] CSRF protection
- [ ] Content Security Policy headers

### Performance
- [ ] Redis caching layer per reports
- [ ] Database connection pooling optimization
- [ ] Query result pagination (offset/limit)
- [ ] Response compression (gzip)
- [ ] CDN per assets statici

### Features
- [ ] Email notifications
- [ ] Export PDF reports
- [ ] Real-time dashboard (WebSocket)
- [ ] Mobile app nativa
- [ ] Multi-tenancy support
- [ ] Advanced analytics (trends, predictions)
- [ ] Geofencing per clock-in
- [ ] Photo upload per attendance

### Testing
- [ ] Unit tests (pytest)
- [ ] Integration tests
- [ ] E2E tests (Playwright/Cypress)
- [ ] Load testing (Locust)
- [ ] Security testing (OWASP ZAP)

### DevOps
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Automated backups
- [ ] Monitoring dashboard (Grafana)
- [ ] Log aggregation (ELK stack)
- [ ] Container orchestration (Kubernetes)

---

## 📞 Support

Per domande o problemi relativi ai nuovi miglioramenti:
- Consultare la documentazione in `/docs`
- Verificare i log: `docker-compose logs -f backend`
- Controllare health check: `curl http://localhost:8000/health`
- Aprire issue su GitHub

---

**Data ultimo aggiornamento**: 2025-11-17
**Versione**: 1.1.0
