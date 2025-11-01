# Database Setup Guide

This guide will help you set up Supabase for storing transactions and rule evaluations.

## Prerequisites

- Supabase account (sign up at https://supabase.com)
- Python dependencies installed (`uv sync` or `pip install -r requirements.txt`)

## Setup Steps

### 1. Create a Supabase Project

1. Go to https://supabase.com and sign in
2. Click "New Project"
3. Fill in your project details:
   - Name: `singhack` (or your preferred name)
   - Database Password: Choose a strong password
   - Region: Select closest to your location
4. Wait for the project to be created (~2 minutes)

### 2. Get Your Supabase Credentials

1. In your Supabase project dashboard, go to **Settings** → **API**
2. Copy the following values:
   - **Project URL** (e.g., `https://xxxxx.supabase.co`)
   - **anon/public key** (for development) or **service_role key** (for backend-only access)

### 3. Configure Environment Variables

1. Update your `.env` file in the `backend` directory:

```env
GROQ_API_KEY=your_groq_api_key_here
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your_supabase_key_here
```

### 4. Create Database Tables

1. In your Supabase project dashboard, go to **SQL Editor**
2. Click "New query"
3. Copy the entire contents of `schema.sql` from this directory
4. Paste it into the SQL editor
5. Click "Run" to execute the SQL and create all tables

Alternatively, you can run it via the Supabase CLI:

```bash
# Install Supabase CLI if you haven't
npm install -g supabase

# Login to Supabase
supabase login

# Link your project
supabase link --project-ref your-project-ref

# Run migrations
supabase db push
```

### 5. Verify Setup

The database should now have the following tables:
- `transactions` - Stores all transaction data
- `rules` - Stores compliance rules
- `rule_evaluations` - Stores individual rule evaluation results
- `batch_evaluations` - Stores batch evaluation summaries

You can verify this in the **Table Editor** in your Supabase dashboard.

## Database Schema Overview

### Tables

#### `transactions`
Stores all transaction details with fields like:
- `transaction_id` (unique identifier)
- `amount`, `currency`
- `originator_name`, `beneficiary_name`
- Customer information (KYC, PEP status, etc.)
- FX details
- SWIFT information
- And more...

#### `rules`
Stores compliance rules:
- `rule_id` (UUID)
- `statement` (rule description)
- `jurisdiction` (array of jurisdictions)
- `source_url`
- `suggested_action`

#### `rule_evaluations`
Stores results of evaluating transactions against rules:
- `transaction_id`
- `rule_id`
- `conditions_met` (boolean)
- `confidence_score` (0.0-1.0)
- `reasoning`
- `suggested_action`
- `evaluated_at`

#### `batch_evaluations`
Stores summary of batch evaluations:
- `transaction_id`
- `total_rules_evaluated`
- `violated_rules_count`
- `passed_rules_count`
- `overall_risk_level` (low/medium/high)
- `requires_action` (boolean)

## API Endpoints

Once set up, your application will have the following endpoints:

### Evaluation Endpoints (Already Existing)
- `POST /api/evaluation/evaluate` - Evaluate a transaction (now also stores in DB)
- `POST /api/evaluation/evaluate-single` - Evaluate against single rule

### Dashboard Endpoints (New)
- `GET /api/dashboard/stats` - Get dashboard statistics
- `GET /api/dashboard/transactions` - Get all transactions with evaluations
- `GET /api/dashboard/transactions/high-risk` - Get high-risk transactions
- `GET /api/dashboard/transactions/requires-action` - Get transactions requiring action
- `GET /api/dashboard/transactions/{transaction_id}` - Get specific transaction details
- `GET /api/dashboard/transactions/{transaction_id}/evaluations` - Get all evaluations for a transaction

## Testing the Setup

### 1. Start your FastAPI server

```bash
cd backend
uvicorn main:app --reload
```

### 2. Test the evaluation endpoint

Send a POST request to `/api/evaluation/evaluate` with a transaction and rules. The results will now be automatically stored in Supabase.

### 3. View stored data

- Visit your Supabase dashboard → Table Editor to see the stored data
- Use the dashboard API endpoints to retrieve data programmatically

### 4. Example: Get dashboard stats

```bash
curl http://localhost:8000/api/dashboard/stats
```

Response:
```json
{
  "total_transactions": 10,
  "transactions_requiring_action": 3,
  "total_rule_violations": 15
}
```

## Troubleshooting

### Connection Issues
- Verify your `SUPABASE_URL` and `SUPABASE_KEY` are correct
- Check that your Supabase project is active
- Ensure your IP is not blocked (Supabase allows all IPs by default)

### Table Creation Issues
- Make sure you ran the entire `schema.sql` file
- Check for SQL errors in the Supabase SQL Editor
- Verify the UUID extension is enabled: `CREATE EXTENSION IF NOT EXISTS "uuid-ossp";`

### Data Not Storing
- Check your FastAPI logs for database errors
- Verify the evaluation endpoint is being called successfully
- Check Supabase logs in your dashboard

## Next Steps

1. **Build a Frontend Dashboard**: Use the dashboard API endpoints to create a React/Vue/Angular dashboard
2. **Add Analytics**: Query the database for trends, statistics, and insights
3. **Set Up Alerts**: Create database triggers or use Supabase Edge Functions for real-time alerts
4. **Add Indexes**: If you notice slow queries, add additional indexes in the SQL editor
5. **Set Up Backups**: Configure automated backups in Supabase settings

## Security Considerations

- **Never commit** your `SUPABASE_KEY` to version control
- Use the `service_role` key only on the backend, never expose it to the frontend
- For frontend access, use Row Level Security (RLS) policies in Supabase
- Consider adding authentication to your API endpoints
- Regularly rotate your Supabase keys

## Support

- Supabase Documentation: https://supabase.com/docs
- FastAPI Documentation: https://fastapi.tiangolo.com
- For project-specific issues, contact the development team
