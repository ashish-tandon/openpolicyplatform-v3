# Services Matrix

### Scraper Service
| Tier         | Entity            | Frequency   | Scope Example                | Owner | Notes |
|--------------|-------------------|-------------|------------------------------|-------|-------|
| federal      | bills             | daily       | federal:*                    | TBA   | idempotent upsert |
| federal      | representatives   | daily       | federal:*                    | TBA   | external IDs stable |
| federal      | committees        | daily       | federal:*                    | TBA   | membership edges |
| provincial   | bills/people/…    | daily       | provincial:on:*              | TBA   | per-province |
| city         | bills/people/…    | bootstrap   | city:toronto:bills (2010+)   | TBA   | historical backfill |