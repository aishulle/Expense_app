# Expense Sharing API

A production-grade backend API for an expense sharing application (similar to Splitwise) built with FastAPI, PostgreSQL, and Redis.

## Features

- **User Management**: Create and manage users
- **Group Management**: Create groups and add members
- **Expense Splitting**: Three split types supported:
  - **EQUAL**: Split expense equally among participants
  - **EXACT**: Specify exact amounts for each participant
  - **PERCENT**: Split expense by percentage
- **Balance Tracking**:
  - **Raw Balances**: Ledger-style debt tracking
  - **Simplified Balances**: Optimized minimal transfers using greedy algorithm
- **Settlements**: Record payments to reduce outstanding balances
- **Caching**: Redis caching for balance calculations
- **Database Migrations**: Alembic for schema versioning

## Tech Stack

- **Python 3.11**
- **FastAPI** - Modern web framework
- **PostgreSQL** - Relational database
- **SQLAlchemy 2.0** (async) - ORM
- **Alembic** - Database migrations
- **Redis** - Caching
- **Pydantic v2** - Data validation
- **pytest** - Testing framework
- **Docker & docker-compose** - Containerization

## Project Structure

```
.
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── core/                   # Core configuration and utilities
│   │   ├── config.py          # Application settings
│   │   ├── database.py        # Database connection and session
│   │   └── redis_client.py    # Redis client
│   ├── models/                 # SQLAlchemy models
│   │   ├── user.py
│   │   ├── group.py
│   │   ├── expense.py
│   │   └── settlement.py
│   ├── schemas/                # Pydantic schemas
│   │   ├── user.py
│   │   ├── group.py
│   │   ├── expense.py
│   │   ├── settlement.py
│   │   └── balance.py
│   ├── repositories/           # Data access layer
│   │   ├── user_repository.py
│   │   ├── group_repository.py
│   │   ├── expense_repository.py
│   │   └── settlement_repository.py
│   ├── services/               # Business logic
│   │   ├── expense_service.py
│   │   ├── balance_service.py
│   │   └── settlement_service.py
│   ├── api/                    # API routers
│   │   └── routers/
│   │       ├── users.py
│   │       ├── groups.py
│   │       ├── expenses.py
│   │       ├── balances.py
│   │       ├── settlements.py
│   │       └── health.py
│   └── utils/                  # Utility functions
│       ├── money.py           # Money rounding and distribution
│       └── balance_simplification.py  # Balance simplification algorithm
├── tests/                      # Test files
├── alembic/                    # Database migrations
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## Setup Instructions

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)

### Using Docker (Recommended)

1. **Clone the repository** (if applicable)

2. **Create a `.env` file** from `.env.example`:
   ```bash
   cp .env.example .env
   ```

3. **Start the services**:
   ```bash
   docker-compose up -d
   ```

   This will start:
   - PostgreSQL database on port 5432
   - Redis on port 6379
   - FastAPI application on port 8000

4. **Run database migrations**:
   ```bash
   docker-compose exec api alembic upgrade head
   ```

5. **Access the API**:
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Local Development Setup

1. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your database and Redis URLs
   ```

4. **Start PostgreSQL and Redis** (using Docker or locally):
   ```bash
   docker-compose up -d postgres redis
   ```

5. **Run migrations**:
   ```bash
   alembic upgrade head
   ```

6. **Run the application**:
   ```bash
   uvicorn app.main:app --reload
   ```

## Environment Variables

Create a `.env` file with the following variables:

```env
POSTGRES_USER=expense_user
POSTGRES_PASSWORD=expense_pass
POSTGRES_DB=expense_db
DATABASE_URL=postgresql+asyncpg://expense_user:expense_pass@localhost:5432/expense_db
REDIS_URL=redis://localhost:6379/0
ENVIRONMENT=development
```

## API Endpoints

### Health Check
- `GET /health` - Health check endpoint

### Users
- `POST /api/v1/users` - Create a new user
- `GET /api/v1/users/{user_id}` - Get user by ID

### Groups
- `POST /api/v1/groups` - Create a new group
- `GET /api/v1/groups/{group_id}` - Get group by ID (with members)
- `POST /api/v1/groups/{group_id}/members` - Add member to group

### Expenses
- `POST /api/v1/groups/{group_id}/expenses` - Create a new expense

### Balances
- `GET /api/v1/groups/{group_id}/balances/raw` - Get raw balances (ledger-style)
- `GET /api/v1/groups/{group_id}/balances/simplified` - Get simplified balances

### Settlements
- `POST /api/v1/groups/{group_id}/settlements` - Create a settlement

## Example API Requests

### 1. Create a User
```bash
curl -X POST "http://localhost:8000/api/v1/users" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com"
  }'
```

### 2. Create a Group
```bash
curl -X POST "http://localhost:8000/api/v1/groups" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Weekend Trip"
  }'
```

### 3. Add Members to Group
```bash
curl -X POST "http://localhost:8000/api/v1/groups/{group_id}/members" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-uuid-here"
  }'
```

### 4. Create an Expense (Equal Split)
```bash
curl -X POST "http://localhost:8000/api/v1/groups/{group_id}/expenses" \
  -H "Content-Type: application/json" \
  -d '{
    "paid_by_user_id": "user-uuid-here",
    "amount": "100.00",
    "description": "Dinner",
    "split_type": "EQUAL",
    "splits": []
  }'
```

### 5. Create an Expense (Exact Split)
```bash
curl -X POST "http://localhost:8000/api/v1/groups/{group_id}/expenses" \
  -H "Content-Type: application/json" \
  -d '{
    "paid_by_user_id": "user-uuid-here",
    "amount": "100.00",
    "description": "Groceries",
    "split_type": "EXACT",
    "splits": [
      {"user_id": "user1-uuid", "amount": "60.00"},
      {"user_id": "user2-uuid", "amount": "40.00"}
    ]
  }'
```

### 6. Create an Expense (Percent Split)
```bash
curl -X POST "http://localhost:8000/api/v1/groups/{group_id}/expenses" \
  -H "Content-Type: application/json" \
  -d '{
    "paid_by_user_id": "user-uuid-here",
    "amount": "100.00",
    "description": "Hotel",
    "split_type": "PERCENT",
    "splits": [
      {"user_id": "user1-uuid", "percent": "50.00"},
      {"user_id": "user2-uuid", "percent": "30.00"},
      {"user_id": "user3-uuid", "percent": "20.00"}
    ]
  }'
```

### 7. Get Simplified Balances
```bash
curl -X GET "http://localhost:8000/api/v1/groups/{group_id}/balances/simplified"
```

### 8. Create a Settlement
```bash
curl -X POST "http://localhost:8000/api/v1/groups/{group_id}/settlements" \
  -H "Content-Type: application/json" \
  -d '{
    "payer_id": "user1-uuid",
    "payee_id": "user2-uuid",
    "amount": "50.00"
  }'
```

## Split Types and Rounding

### EQUAL Split
- Amount is divided equally among participants
- Remaining cents after rounding are distributed fairly (first few participants get an extra cent)
- Example: $100.00 split 3 ways = $33.33, $33.33, $33.34

### EXACT Split
- Amounts must be provided for each participant
- Sum of split amounts must exactly equal the total expense amount
- Validation error if sum doesn't match

### PERCENT Split
- Percentages must be provided for each participant
- Sum of percentages must equal 100
- Amounts are calculated from percentages and rounded to 2 decimal places
- Remaining cents are distributed fairly
- Example: 33.33%, 33.33%, 33.34% of $100 = $33.33, $33.33, $33.34

## Balance Simplification Algorithm

The simplified balances use a **greedy matching algorithm**:

1. Calculate net balance for each user (positive = owed money, negative = owes money)
2. Sort debtors (negative balance) and creditors (positive balance) by amount
3. Match largest debtors to largest creditors
4. Create transfers for minimal number of transactions
5. Only return positive transfers (no zero amounts)

Example:
- Raw balances: A owes B $50, B owes C $30, A owes C $20
- Simplified: A pays C $70 directly

## Testing

### Prerequisites

Before running tests, install all dependencies:

```bash
pip install -r requirements.txt
```

### Running Tests

**Run all tests:**
```bash
pytest -v
```

**Run with coverage report:**
```bash
pytest --cov=app --cov-report=html --cov-report=term
```

**Run specific test file:**
```bash
pytest tests/test_expense_splits.py -v
pytest tests/test_balances.py -v
pytest tests/test_users_groups.py -v
```

**Run a specific test:**
```bash
pytest tests/test_expense_splits.py::test_equal_split_with_rounding -v
```

**Note:** Tests use an in-memory SQLite database and mocked Redis, so no setup is required.

For detailed testing instructions, see [TESTING.md](TESTING.md) or [QUICK_START_TESTS.md](QUICK_START_TESTS.md).

### Test Coverage

Test coverage includes:
- Equal split with rounding
- Exact split validation
- Percent split validation and rounding
- Raw balance calculations
- Simplified balance calculations
- Settlement balance reduction

## Database Migrations

### Create a new migration
```bash
alembic revision --autogenerate -m "Description of changes"
```

### Apply migrations
```bash
alembic upgrade head
```

### Rollback migration
```bash
alembic downgrade -1
```

## Redis Caching

Balance endpoints are cached in Redis:
- Cache keys: `balances:{group_id}:raw` and `balances:{group_id}:simplified`
- Cache duration: 1 hour (3600 seconds)
- Cache invalidation: Automatically invalidated when expenses or settlements are created

## Development Notes

- All monetary values use `Decimal` type for precision (no floats)
- Database stores amounts as `NUMERIC(12,2)`
- All amounts are rounded to 2 decimal places
- The API uses UUIDs for all entity IDs
- Transactions are used for all write operations

## License

This project is provided as-is for educational and development purposes.

