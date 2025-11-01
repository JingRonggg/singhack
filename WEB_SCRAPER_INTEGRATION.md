# Web Scraper Database Integration

## Overview

The web scraper now **automatically stores all extracted rules** into the Supabase database whenever it runs. This means every time you scrape regulatory content from websites, the rules are permanently stored and can be:
- Retrieved via the dashboard API
- Used in future transaction evaluations
- Filtered by jurisdiction
- Audited and tracked over time

## What Was Implemented

### 1. Automatic Rule Storage in Web Scraper

**File:** `backend/controller/web_scraper.py`

When the `/api/scraper/scrape` endpoint is called, it now:
1. Scrapes the provided URLs
2. Extracts compliance rules using AI
3. **Automatically stores each rule in Supabase**
4. Returns the scraped rules to the caller
5. Logs success/failure for each rule stored

**Features:**
- Graceful error handling - if one rule fails to store, others continue
- Detailed logging for tracking
- Non-blocking - scraper still returns results even if DB storage fails
- Upsert behavior - same rule scraped twice won't create duplicates

### 2. New Dashboard Endpoints for Rules

**File:** `backend/controller/dashboard.py`

Added three new endpoints:

#### GET /api/dashboard/rules
Get all stored rules with pagination and optional jurisdiction filter.

**Query Parameters:**
- `limit` (default: 100, max: 500) - Number of rules to return
- `offset` (default: 0) - Pagination offset
- `jurisdiction` (optional) - Filter by jurisdiction (e.g., "HK", "SG")

**Example:**
```bash
# Get all rules
curl http://127.0.0.1:8000/api/dashboard/rules

# Get rules for Hong Kong
curl http://127.0.0.1:8000/api/dashboard/rules?jurisdiction=HK

# Pagination
curl http://127.0.0.1:8000/api/dashboard/rules?limit=50&offset=100
```

**Response:**
```json
{
  "rules": [
    {
      "rule_id": "550e8400-e29b-41d4-a716-446655440001",
      "statement": "High-value transactions require enhanced due diligence",
      "jurisdiction": ["HK", "SG"],
      "source_url": "https://...",
      "suggested_action": "enhanced due diligence",
      "created_at": "2025-11-01T11:22:34Z"
    }
  ],
  "total": 3,
  "limit": 100,
  "offset": 0,
  "jurisdiction_filter": "HK"
}
```

#### GET /api/dashboard/rules/{rule_id}
Get detailed information about a specific rule.

**Example:**
```bash
curl http://127.0.0.1:8000/api/dashboard/rules/550e8400-e29b-41d4-a716-446655440001
```

### 3. Enhanced Database Service

**File:** `backend/services/database_service.py`

Added two new methods:

- `get_rule(rule_id)` - Retrieve a single rule by UUID
- `get_all_rules(limit, offset, jurisdiction)` - Get rules with filtering

### 4. Updated Dashboard Stats

The stats endpoint now includes total rules count:

**GET /api/dashboard/stats**

```json
{
  "total_transactions": 1,
  "transactions_requiring_action": 0,
  "total_rule_violations": 1,
  "total_rules": 3
}
```

## How It Works

### Web Scraper Flow

```
1. User calls: POST /api/scraper/scrape
   ↓
2. Web scraper extracts rules from URLs
   ↓
3. Rules are validated using Pydantic schemas
   ↓
4. FOR EACH RULE:
   - Store in Supabase (upsert by rule_id)
   - Log success/failure
   ↓
5. Return all scraped rules to user
```

### Example Web Scraper Usage

```bash
# Scrape default URLs (configured in web_scraper tool)
curl -X POST http://127.0.0.1:8000/api/scraper/scrape \
  -H "Content-Type: application/json" \
  -d '{}'

# Scrape specific URLs
curl -X POST http://127.0.0.1:8000/api/scraper/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "urls": [
      "https://www.hkma.gov.hk/eng/regulatory-resources/",
      "https://www.mas.gov.sg/regulation"
    ]
  }'
```

**Response:**
```json
{
  "www.hkma.gov.hk": {
    "ruleset_id": "abc123...",
    "created_at": 1698765432,
    "rules": {
      "1": {
        "rule_id": "550e8400-...",
        "statement": "Large cash transactions require reporting",
        "jurisdiction": ["HK"],
        "source_url": "https://www.hkma.gov.hk/...",
        "suggested_action": "enhanced due diligence"
      },
      "2": { ... }
    },
    "source_urls": ["https://..."]
  }
}
```

## Database Schema

The `rules` table stores:
- `rule_id` (UUID, unique) - Unique identifier for the rule
- `statement` (TEXT) - The rule description
- `jurisdiction` (TEXT[]) - Array of jurisdictions (e.g., ["HK", "SG"])
- `source_url` (TEXT) - Where the rule was extracted from
- `suggested_action` (TEXT) - Action to take (enhanced due diligence, transaction blocking, escalation)
- `created_at` (TIMESTAMP) - When the rule was first stored
- `updated_at` (TIMESTAMP) - Last update time

## Benefits

### 1. **Persistent Rule Library**
- All scraped rules are permanently stored
- Build a comprehensive compliance rule database over time
- Rules can be referenced by UUID in evaluations

### 2. **Audit Trail**
- Track when rules were scraped
- Know the source of each rule
- Monitor rule changes over time

### 3. **Reusable Rules**
- Use stored rules for future evaluations
- No need to re-scrape every time
- Faster evaluation setup

### 4. **Centralized Management**
- View all rules in one place
- Filter by jurisdiction
- Easy integration with frontend dashboards

## Testing the Integration

### 1. Check Current Rules
```bash
curl http://127.0.0.1:8000/api/dashboard/stats
# Should show total_rules: 3
```

### 2. View All Rules
```bash
curl http://127.0.0.1:8000/api/dashboard/rules | jq
```

### 3. Filter by Jurisdiction
```bash
curl "http://127.0.0.1:8000/api/dashboard/rules?jurisdiction=HK" | jq
```

### 4. Get Specific Rule
```bash
curl http://127.0.0.1:8000/api/dashboard/rules/550e8400-e29b-41d4-a716-446655440001 | jq
```

### 5. Scrape New Rules (will auto-store)
```bash
curl -X POST http://127.0.0.1:8000/api/scraper/scrape \
  -H "Content-Type: application/json" \
  -d '{"urls": ["https://your-regulatory-url.com"]}'

# Then check stats again
curl http://127.0.0.1:8000/api/dashboard/stats
# total_rules should increase
```

## Frontend Integration

For building a dashboard, you can now:

### Display Rules Library
```javascript
// Fetch all rules
const response = await fetch('http://localhost:8000/api/dashboard/rules');
const data = await response.json();

// Display rules table
data.rules.forEach(rule => {
  console.log(`${rule.statement} - ${rule.jurisdiction.join(', ')}`);
});
```

### Filter by Jurisdiction
```javascript
// Get only Singapore rules
const response = await fetch('http://localhost:8000/api/dashboard/rules?jurisdiction=SG');
```

### Scrape and Store New Rules
```javascript
// Scrape new regulatory websites
const response = await fetch('http://localhost:8000/api/scraper/scrape', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    urls: ['https://new-regulatory-site.com']
  })
});

// Rules are automatically stored in database
const rules = await response.json();
```

## API Endpoints Summary

### Web Scraper (with auto-storage)
- `POST /api/scraper/scrape` - Scrape URLs and store rules

### Dashboard - Rules
- `GET /api/dashboard/rules` - Get all rules (with filters)
- `GET /api/dashboard/rules/{rule_id}` - Get specific rule
- `GET /api/dashboard/stats` - Overall stats (includes total_rules)

### Dashboard - Transactions (existing)
- `GET /api/dashboard/transactions` - All transactions
- `GET /api/dashboard/transactions/{id}` - Transaction details
- `GET /api/dashboard/transactions/{id}/evaluations` - Evaluations
- `GET /api/dashboard/transactions/high-risk` - High-risk filter
- `GET /api/dashboard/transactions/requires-action` - Action required

### Evaluation (existing, with auto-storage)
- `POST /api/evaluation/evaluate` - Evaluate and store

## Logging

The system logs all rule storage operations:

```
INFO - Stored rule 550e8400-... from www.hkma.gov.hk
INFO - Stored rule 550e8400-... from www.mas.gov.sg
INFO - Successfully stored 15 rules in database
```

Check your server logs to monitor rule storage activity.

## Error Handling

- **Individual rule failure**: Logged but doesn't stop processing other rules
- **Database connection failure**: Logged but scraper still returns results
- **Duplicate rules**: Upserted (updated if already exists)

## Next Steps

1. **Scrape More Sources**
   - Add regulatory websites to scrape
   - Build comprehensive rule library
   - Cover multiple jurisdictions

2. **Build Rules Management UI**
   - Display all stored rules
   - Edit/update rules
   - Manage jurisdictions
   - Track rule changes

3. **Use Stored Rules for Evaluation**
   - Reference rules by ID
   - Auto-load rules for specific jurisdictions
   - Build rule sets for different scenarios

4. **Analytics**
   - Track most violated rules
   - Analyze rule effectiveness
   - Monitor rule usage across transactions

## Files Modified

- `backend/controller/web_scraper.py` - Added auto-storage
- `backend/controller/dashboard.py` - Added rules endpoints
- `backend/services/database_service.py` - Added rule retrieval methods

All changes are backward compatible - existing functionality is unchanged!
