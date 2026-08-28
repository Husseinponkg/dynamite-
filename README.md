# Dynamite Networks — Modern ISP Hotspot Billing System

Black & yellow themed billing platform for MikroTik hotspot / ISP operators.

## Features

- **Dashboard** — live stats for packages, routers, vouchers
- **Packages** — create/edit plans (price, validity, bandwidth, data limit)
- **Vouchers** — bulk generate, print tickets, redeem, cancel, filter by status
- **Routers** — manage MikroTik devices (API / REST)
- **Payments** — mobile money (AzamPay: M-Pesa, Airtel, Tigo, HaloPesa, Yas)
- **Captive Portal** — buy package or redeem voucher code
- **Sessions** — active user connections
- **Income** — revenue reports
- **Withdraws** — payout requests
- **Branches** — multi-location management
- **Settings** — company / currency / theme

## Stack

| Layer    | Tech                                      |
|----------|-------------------------------------------|
| Backend  | FastAPI, psycopg (async), PostgreSQL, JWT |
| Frontend | React 19, Vite, React Router              |
| Payments | AzamPay integration                       |
| Routers  | MikroTik API (netmiko)                    |

## Quick Start

### Backend

```bash
cd BACKEND
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
# Configure .env (DB_HOST, DB_USER, DB_PASS, DB_NAME, DB_PORT, JWT secrets, AzamPay keys)
# Apply schema: psql -f models/tables.sql
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# Open http://localhost:5173
```

## Voucher API

| Method | Path                    | Description              |
|--------|-------------------------|--------------------------|
| POST   | `/vouchers/generate`    | Bulk generate vouchers   |
| GET    | `/vouchers/`            | List / filter vouchers   |
| GET    | `/vouchers/stats`       | Counts by status         |
| POST   | `/vouchers/redeem`      | Redeem a code            |
| POST   | `/vouchers/{id}/cancel` | Cancel active voucher    |

### Generate example

```json
{
  "package_id": 1,
  "router_id": 1,
  "quantity": 20,
  "prefix": "DYN",
  "code_length": 8,
  "expire_days": 30
}
```

## UI Theme

Pure black background (`#0a0a0a`) with yellow accents (`#ffd600`). Responsive sidebar, stat cards, printable voucher tickets.

## Database

See `BACKEND/models/tables.sql` for full schema including:

- users, admin
- package, vouchers, payments
- routers, active_sessions
- package_history, system_logs
