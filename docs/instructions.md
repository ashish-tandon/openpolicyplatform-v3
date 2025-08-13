-------------------------------------------------------------------------------
MODE: SCRAPERS  (RUN_SCRAPERS: <daily|bootstrap|special> <scope> [--since])
Rules:
- Keep all existing scrapers; replace nothing unless broken.
- Use adapters in services/scraper/adapters/* for upstream repos under external/.
Checklist:
1) Implement/verify adapter -> parser -> normalizer -> store.upsert()
2) Add unit + contract + integration tests
3) Register scope in runners/* and K8s CronJobs (if scheduled)
4) Emit metrics and journal run
5) Update reference docs & SERVICES_MATRIX
Examples:
- RUN_SCRAPERS: daily federal:*
- RUN_SCRAPERS: daily provincial:on:*
- RUN_SCRAPERS: bootstrap city:toronto:bills --since 2010-01-01