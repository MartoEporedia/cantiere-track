# RBAC & Audit Logging - Complete Implementation Guide

Questa guida documenta l'implementazione completa del sistema di Role-Based Access Control (RBAC) e Audit Logging per CantiereTrack.

---

## 📋 Indice

1. [Panoramica Sistema RBAC](#panoramica-sistema-rbac)
2. [Ruoli e Permessi](#ruoli-e-permessi)
3. [Matrice dei Permessi](#matrice-dei-permessi)
4. [Audit Logging](#audit-logging)
5. [Testing RBAC](#testing-rbac)
6. [Troubleshooting](#troubleshooting)

---

## 🎯 Panoramica Sistema RBAC

Il sistema RBAC implementato protegge **tutti** gli endpoint CRUD delle risorse critiche:
- 👤 **Employees** (dipendenti)
- 🏗️ **Sites** (cantieri)
- ⏰ **Attendance** (presenze)

### Architettura

```
Request → JWT Token → Authentication → RBAC Check → Endpoint → Audit Log
```

**Flusso:**
1. Client invia richiesta con JWT token
2. Sistema autentica l'utente (`get_current_user`)
3. Sistema verifica il ruolo utente (`require_admin`, `require_manager_or_admin`)
4. Se autorizzato, esegue operazione
5. Operazione loggata in `audit_logs` table

---

## 👥 Ruoli e Permessi

### ADMIN 🔑
**Accesso**: Completo e illimitato

**Capacità:**
- ✅ Tutte le operazioni CRUD su employees, sites, attendance
- ✅ DELETE di qualsiasi risorsa
- ✅ Gestione utenti (future)
- ✅ Accesso a tutti i report e audit logs

**Utenti tipici:**
- System Administrator
- IT Manager
- Company Owner

---

### MANAGER 👔
**Accesso**: Gestione operativa completa

**Capacità:**
- ✅ CREATE, READ, UPDATE employees
- ✅ CREATE, READ, UPDATE sites
- ✅ Clock-in/Clock-out employees
- ✅ CREATE, READ, UPDATE attendance (incluso manual hours)
- ✅ Generare e scaricare reports
- ❌ DELETE di qualsiasi risorsa (solo ADMIN)

**Utenti tipici:**
- Site Manager
- HR Manager
- Operations Manager
- Team Lead

---

### VIEWER 👁️
**Accesso**: Solo lettura

**Capacità:**
- ✅ READ employees (visualizzare lista e dettagli)
- ✅ READ sites (visualizzare cantieri)
- ✅ READ attendance (visualizzare presenze)
- ✅ Visualizzare reports
- ❌ Nessuna operazione di scrittura
- ❌ Clock-in/Clock-out
- ❌ Modifiche o eliminazioni

**Utenti tipici:**
- Accountant (contabile - solo lettura per payroll)
- External Auditor
- Client/Customer (con accesso limitato)
- Reporting Dashboard Users

---

## 📊 Matrice dei Permessi

### Employees Endpoints

| Endpoint | Metodo | ADMIN | MANAGER | VIEWER | Descrizione |
|----------|--------|-------|---------|--------|-------------|
| `/api/employees/` | POST | ✅ | ✅ | ❌ | Crea nuovo dipendente |
| `/api/employees/` | GET | ✅ | ✅ | ✅ | Lista dipendenti |
| `/api/employees/{id}` | GET | ✅ | ✅ | ✅ | Dettagli dipendente |
| `/api/employees/{id}` | PUT | ✅ | ✅ | ❌ | Modifica dipendente |
| `/api/employees/{id}` | DELETE | ✅ | ❌ | ❌ | Elimina dipendente |

**Audit Actions:**
- `CREATE_EMPLOYEE`: Logs nome, cognome, badge_code, ruolo
- `UPDATE_EMPLOYEE`: Logs campi modificati, old_values, new_values
- `DELETE_EMPLOYEE`: Logs dati dipendente eliminato

---

### Sites Endpoints

| Endpoint | Metodo | ADMIN | MANAGER | VIEWER | Descrizione |
|----------|--------|-------|---------|--------|-------------|
| `/api/sites/` | POST | ✅ | ✅ | ❌ | Crea nuovo cantiere |
| `/api/sites/` | GET | ✅ | ✅ | ✅ | Lista cantieri |
| `/api/sites/{id}` | GET | ✅ | ✅ | ✅ | Dettagli cantiere |
| `/api/sites/{id}` | PUT | ✅ | ✅ | ❌ | Modifica cantiere |
| `/api/sites/{id}` | DELETE | ✅ | ❌ | ❌ | Elimina cantiere |

**Audit Actions:**
- `CREATE_SITE`: Logs nome, indirizzo, città, stato
- `UPDATE_SITE`: Logs campi modificati, old_values, new_values
- `DELETE_SITE`: Logs dati cantiere eliminato

---

### Attendance Endpoints

| Endpoint | Metodo | ADMIN | MANAGER | VIEWER | Descrizione |
|----------|--------|-------|---------|--------|-------------|
| `/api/attendance/clock-in` | POST | ✅ | ✅ | ❌ | Clock-in dipendente |
| `/api/attendance/{id}/clock-out` | PUT | ✅ | ✅ | ❌ | Clock-out dipendente |
| `/api/attendance/` | POST | ✅ | ✅ | ❌ | Aggiungi ore manualmente |
| `/api/attendance/` | GET | ✅ | ✅ | ✅ | Lista presenze |
| `/api/attendance/{id}` | GET | ✅ | ✅ | ✅ | Dettagli presenza |
| `/api/attendance/{id}` | PUT | ✅ | ✅ | ❌ | Modifica presenza |
| `/api/attendance/{id}` | DELETE | ✅ | ❌ | ❌ | Elimina presenza |
| `/api/attendance/employee/{id}/active` | GET | ✅ | ✅ | ✅ | Presenza attiva dipendente |

**Audit Actions:**
- `CLOCK_IN`: Logs employee_id, employee_name, site_id, site_name, timestamp
- `CLOCK_OUT`: Logs employee_id, site_id, timestamp_out, hours_worked
- `ADD_MANUAL_HOURS`: Logs employee_id, site_id, timestamp_in, timestamp_out, hours
- `UPDATE_ATTENDANCE`: Logs campi modificati, old_values
- `DELETE_ATTENDANCE`: Logs dati presenza eliminata

---

### Reports Endpoints

| Endpoint | Metodo | ADMIN | MANAGER | VIEWER | Descrizione |
|----------|--------|-------|---------|--------|-------------|
| `/api/reports/employee/{id}` | GET | ✅ | ✅ | ✅ | Report dipendente |
| `/api/reports/site/{id}` | GET | ✅ | ✅ | ✅ | Report cantiere |
| `/api/reports/employee/{id}/csv` | GET | ✅ | ✅ | ✅ | Export CSV dipendente |
| `/api/reports/site/{id}/csv` | GET | ✅ | ✅ | ✅ | Export CSV cantiere |

**Nota:** I reports sono accessibili a tutti gli utenti autenticati (incluso VIEWER).

---

## 📝 Audit Logging

### Struttura Audit Log

Ogni azione critica viene registrata nella tabella `audit_logs`:

```sql
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(100) NOT NULL,              -- es. "create_employee", "delete_site"
    resource_type VARCHAR(50),                 -- es. "employee", "site", "attendance"
    resource_id INTEGER,                       -- ID della risorsa modificata
    details JSON,                              -- Dettagli specifici dell'azione
    ip_address VARCHAR(45),                    -- IP dell'utente (IPv4/IPv6)
    user_agent TEXT,                           -- Browser/client info
    created_at TIMESTAMP WITH TIME ZONE NOT NULL
);
```

### Informazioni Tracciate

Per **ogni azione** viene salvato:

| Campo | Descrizione | Esempio |
|-------|-------------|---------|
| `user_id` | ID utente che ha eseguito l'azione | `42` |
| `action` | Tipo di azione | `"create_employee"` |
| `resource_type` | Tipo di risorsa | `"employee"` |
| `resource_id` | ID risorsa modificata | `123` |
| `details` | JSON con dettagli specifici | `{"name": "Mario", "badge": "EMP001"}` |
| `ip_address` | IP client | `"192.168.1.100"` |
| `user_agent` | Browser/app | `"Mozilla/5.0 ..."` |
| `created_at` | Timestamp UTC | `"2025-11-17T14:30:00Z"` |

### Query Audit Logs Utili

```python
from app.models.audit_log import AuditLog
from app.core.audit import AuditAction

# Tutte le azioni di un utente
logs = db.query(AuditLog).filter(AuditLog.user_id == user_id).all()

# Tutti i login degli ultimi 30 giorni
from datetime import datetime, timedelta
since = datetime.utcnow() - timedelta(days=30)
logins = db.query(AuditLog).filter(
    AuditLog.action == AuditAction.LOGIN,
    AuditLog.created_at >= since
).all()

# Tutte le eliminazioni (azioni sensibili)
deletions = db.query(AuditLog).filter(
    AuditLog.action.in_([
        AuditAction.DELETE_EMPLOYEE,
        AuditAction.DELETE_SITE,
        AuditAction.DELETE_ATTENDANCE
    ])
).all()

# Azioni su una risorsa specifica
employee_logs = db.query(AuditLog).filter(
    AuditLog.resource_type == "employee",
    AuditLog.resource_id == 123
).order_by(AuditLog.created_at.desc()).all()

# Azioni da un IP specifico (sicurezza)
suspicious = db.query(AuditLog).filter(
    AuditLog.ip_address == "192.168.1.100"
).all()
```

### Dashboard Audit (Future Implementation)

Endpoints suggeriti per un dashboard audit:

```python
# GET /api/audit/logs?user_id=X&action=Y&date_from=Z
# GET /api/audit/stats  # Statistiche aggregate
# GET /api/audit/timeline/{resource_type}/{resource_id}  # Timeline risorsa
```

---

## 🧪 Testing RBAC

### Setup Test Users

Creare 3 utenti di test con ruoli diversi:

```bash
cd backend
python scripts/init_db.py

# Oppure via API:
# User 1: ADMIN
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@test.com",
    "password": "Admin123",
    "role": "admin"
  }'

# User 2: MANAGER
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "manager",
    "email": "manager@test.com",
    "password": "Manager123",
    "role": "manager"
  }'

# User 3: VIEWER
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "viewer",
    "email": "viewer@test.com",
    "password": "Viewer123",
    "role": "viewer"
  }'
```

### Test Cases

#### Test 1: VIEWER non può creare dipendente

```bash
# Login come viewer
TOKEN=$(curl -s -X POST "http://localhost:8000/api/auth/login" \
  -d "username=viewer&password=Viewer123" | jq -r '.access_token')

# Tentativo di creare dipendente (dovrebbe fallire)
curl -X POST "http://localhost:8000/api/employees/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test",
    "surname": "Employee",
    "badge_code": "TEST001"
  }'

# Atteso: HTTP 403 Forbidden
# Response: {"detail": "Manager or Admin access required"}
```

#### Test 2: MANAGER può creare ma non eliminare

```bash
# Login come manager
TOKEN=$(curl -s -X POST "http://localhost:8000/api/auth/login" \
  -d "username=manager&password=Manager123" | jq -r '.access_token')

# Creazione dipendente (dovrebbe funzionare)
EMPLOYEE_ID=$(curl -s -X POST "http://localhost:8000/api/employees/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Mario",
    "surname": "Rossi",
    "badge_code": "EMP001"
  }' | jq -r '.id')

echo "Employee created with ID: $EMPLOYEE_ID"

# Tentativo di eliminazione (dovrebbe fallire)
curl -X DELETE "http://localhost:8000/api/employees/$EMPLOYEE_ID" \
  -H "Authorization: Bearer $TOKEN"

# Atteso: HTTP 403 Forbidden
# Response: {"detail": "Admin access required"}
```

#### Test 3: ADMIN può tutto

```bash
# Login come admin
TOKEN=$(curl -s -X POST "http://localhost:8000/api/auth/login" \
  -d "username=admin&password=Admin123" | jq -r '.access_token')

# Creazione dipendente
EMPLOYEE_ID=$(curl -s -X POST "http://localhost:8000/api/employees/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Giuseppe",
    "surname": "Verdi",
    "badge_code": "EMP002"
  }' | jq -r '.id')

# Modifica dipendente
curl -X PUT "http://localhost:8000/api/employees/$EMPLOYEE_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "Capo cantiere"
  }'

# Eliminazione dipendente
curl -X DELETE "http://localhost:8000/api/employees/$EMPLOYEE_ID" \
  -H "Authorization: Bearer $TOKEN"

# Atteso: Tutte le operazioni completate con successo
```

#### Test 4: Verifica Audit Logs

```bash
# Dopo i test sopra, controllare audit logs nel database:
docker-compose exec db psql -U cantieretrack -d cantieretrack -c "
SELECT
    u.username,
    al.action,
    al.resource_type,
    al.resource_id,
    al.details->>'name' as employee_name,
    al.created_at
FROM audit_logs al
JOIN users u ON al.user_id = u.id
ORDER BY al.created_at DESC
LIMIT 10;
"
```

**Output atteso:**
```
 username |      action       | resource_type | resource_id | employee_name |       created_at
----------+-------------------+---------------+-------------+---------------+---------------------
 admin    | delete_employee   | employee      | 2           | Giuseppe      | 2025-11-17 15:30:00
 admin    | update_employee   | employee      | 2           |               | 2025-11-17 15:29:45
 admin    | create_employee   | employee      | 2           | Giuseppe      | 2025-11-17 15:29:30
 manager  | create_employee   | employee      | 1           | Mario         | 2025-11-17 15:28:00
```

---

## 🚨 Troubleshooting

### Errore: 403 Forbidden

**Sintomo:**
```json
{
  "detail": "Manager or Admin access required"
}
```

**Cause possibili:**
1. ✅ User ha ruolo `VIEWER` ma tenta operazione di scrittura
2. ✅ Token JWT non contiene informazioni corrette sul ruolo
3. ✅ Database non ha campo `role` aggiornato

**Soluzioni:**
```bash
# 1. Verificare ruolo utente
docker-compose exec db psql -U cantieretrack -d cantieretrack -c "
SELECT id, username, role FROM users WHERE username = 'your_username';
"

# 2. Aggiornare ruolo manualmente se necessario
docker-compose exec db psql -U cantieretrack -d cantieretrack -c "
UPDATE users SET role = 'manager' WHERE username = 'your_username';
"

# 3. Verificare migrations applicate
cd backend
alembic current
alembic upgrade head
```

---

### Errore: Migration Failed

**Sintomo:**
```
sqlalchemy.exc.ProgrammingError: (psycopg2.errors.UndefinedColumn) column "role" does not exist
```

**Soluzione:**
```bash
cd backend

# Verificare status migrations
alembic current

# Se mancano migrations, applicarle
alembic upgrade head

# Se problemi persistono, fare downgrade e re-apply
alembic downgrade -1
alembic upgrade head
```

---

### Audit Logs Non Vengono Salvati

**Cause possibili:**
1. ❌ Tabella `audit_logs` non esiste
2. ❌ Import mancante in router
3. ❌ Request object non passato

**Verifiche:**
```bash
# 1. Verificare tabella esiste
docker-compose exec db psql -U cantieretrack -d cantieretrack -c "\dt audit_logs"

# 2. Verificare import nel router
grep "from ..core.audit import" backend/app/routers/employees.py

# 3. Controllare logs backend
docker-compose logs -f backend | grep -i error
```

---

### Utente Registrato Senza Ruolo

**Sintomo:** Nuovo utente non ha campo `role` valorizzato.

**Causa:** Migration `20251117_add_user_role` non applicata prima della registrazione.

**Soluzione:**
```bash
# Aggiornare ruolo utenti esistenti
docker-compose exec db psql -U cantieretrack -d cantieretrack -c "
UPDATE users SET role = 'viewer' WHERE role IS NULL;
"
```

---

## 📚 Best Practices

### Per Developers

1. **Sempre testare con 3 ruoli**: ADMIN, MANAGER, VIEWER
2. **Loggare tutte le operazioni sensibili**: Ogni CREATE, UPDATE, DELETE
3. **Dettagli specifici nei logs**: Salvare old_values, new_values per updates
4. **IP e User Agent**: Utili per sicurezza e troubleshooting
5. **JSON per details**: Permette query flessibili e analisi

### Per Admins

1. **Monitorare audit logs regolarmente**
2. **Alert su azioni sensibili** (es. bulk deletions)
3. **Backup regolari** della tabella `audit_logs`
4. **Retention policy**: Decidere per quanto tenere i logs (es. 2 anni)
5. **GDPR compliance**: Audit logs possono contenere dati personali

### Per Product Managers

1. **Dashboard audit**: Implementare visualizzazione logs per admins
2. **Export audit logs**: Funzionalità per compliance/auditing
3. **User activity timeline**: Mostrare azioni utente specifico
4. **Resource history**: Timeline modifiche per ogni risorsa
5. **Anomaly detection**: Alert su comportamenti sospetti

---

## 🔄 Migration da Sistema Precedente

Se il sistema era già in produzione senza RBAC:

### Step 1: Backup

```bash
# Backup database completo
docker-compose exec db pg_dump -U cantieretrack cantieretrack > backup_pre_rbac.sql
```

### Step 2: Apply Migrations

```bash
cd backend
alembic upgrade head
```

### Step 3: Assegnare Ruoli Utenti Esistenti

```sql
-- Identificare admin (es. primi utenti o is_superuser)
UPDATE users SET role = 'admin' WHERE is_superuser = true;

-- Assegnare manager (es. users con email @company.com)
UPDATE users SET role = 'manager' WHERE email LIKE '%@company.com' AND role IS NULL;

-- Tutti gli altri = viewer
UPDATE users SET role = 'viewer' WHERE role IS NULL;
```

### Step 4: Test

Testare con utenti reali prima di deployment completo.

### Step 5: Comunicazione

Informare utenti dei nuovi permessi e ruoli assegnati.

---

## 📈 Future Improvements

Possibili estensioni del sistema RBAC:

1. **Custom Permissions**: Granularità maggiore (es. "can_export_reports")
2. **Site-Based Access**: Manager può gestire solo "suoi" cantieri
3. **Time-Based Access**: Permessi validi solo in certi orari
4. **2FA for Admins**: Two-Factor Authentication per operazioni critiche
5. **Approval Workflows**: Richieste di modifica che richiedono approvazione
6. **Role Hierarchy**: ADMIN eredita automaticamente permessi MANAGER
7. **Dynamic Roles**: Assegnazione ruoli basata su gruppo AD/LDAP

---

## 📞 Support

Per problemi con RBAC o Audit Logging:

1. ✅ Verificare migrations applicate
2. ✅ Controllare logs backend: `docker-compose logs -f backend`
3. ✅ Query database per verificare ruoli: `SELECT username, role FROM users;`
4. ✅ Consultare questa documentazione
5. ✅ Aprire issue su GitHub

---

**Ultima revisione:** 2025-11-17
**Versione:** 1.1.0
