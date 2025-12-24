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

     
5. **Access the API**:
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc


- Transactions are used for all write operations

## License

This project is provided as-is for educational and development purposes.

