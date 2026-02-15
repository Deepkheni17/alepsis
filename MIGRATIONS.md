# Database Migrations Guide

This project uses Alembic for database schema migrations with PostgreSQL (Supabase).

## Setup

1. **Environment Configuration**
   ```bash
   # Copy .env.example to .env and set your DATABASE_URL
   cp .env.example .env
   
   # Edit .env and set your Supabase PostgreSQL connection string
   # DATABASE_URL=postgresql://postgres:your_password@db.xxxxx.supabase.co:5432/postgres
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Common Commands

### Create a New Migration
```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Description of changes"

# Create empty migration for custom SQL
alembic revision -m "Description of changes"
```

### Apply Migrations
```bash
# Upgrade to latest version
alembic upgrade head

# Upgrade one version
alembic upgrade +1
```

### Rollback Migrations
```bash
# Downgrade one version
alembic downgrade -1

# Downgrade to specific revision
alembic downgrade <revision_id>

# Downgrade to base (remove all migrations)
alembic downgrade base
```

### View Migration History
```bash
# Show current version
alembic current

# Show migration history
alembic history

# Show pending migrations
alembic heads
```

## Initial Migration Workflow

1. **Create initial migration** (captures current schema):
   ```bash
   alembic revision --autogenerate -m "Initial schema"
   ```

2. **Review generated migration** in `alembic/versions/`:
   - Check upgrade() function
   - Check downgrade() function
   - Verify all models are included

3. **Apply migration**:
   ```bash
   alembic upgrade head
   ```

## Production Deployment

1. **Before deployment**: Always test migrations on staging database first
2. **Backup**: Create database backup before running migrations in production
3. **Apply**: Run `alembic upgrade head` on production database
4. **Verify**: Check database schema matches expected state

## Troubleshooting

- **"Can't locate revision"**: Run `alembic stamp head` to mark current database state
- **"Target database is not up to date"**: Run `alembic upgrade head`
- **Migration conflicts**: Resolve by creating merge revision with `alembic merge`

## Notes

- Alembic reads DATABASE_URL from environment variable (set in .env)
- All models must be imported in `app/models/orm_models.py` for autogenerate to work
- Always review auto-generated migrations before applying
