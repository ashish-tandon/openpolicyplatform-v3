# Next Steps

## Scraper Adapters
- Implement adapters for `opencivicdata/scrapers-ca` (province/municipal):
  - People, organizations, events, bills
  - Add rate limiting and per-domain backoff
  - Map fields to our schema and upsert
- Implement `openparliament` historic importer:
  - One-off jobs per dataset with resumable checkpoints
  - Normalize to current schema via MCP stage

## MCP/Data Quality
- Formalize MCP validation rules
- Add normalization and canonicalization steps before writes
- Emit MCP metrics and surface in Grafana

## Observability
- Add Grafana panels for DB write throughput and error rates
- Add alerting rules in Prometheus for worker stalls and high failure rates

## Performance & Load
- Tune Redis queue size and worker concurrency
- Add headless-browser usage where required with limits

## Security
- Harden JWT handling and token revocation list
- Secure Prometheus/Grafana behind auth

## Deployment
- Provide Terraform or Ansible for infra provisioning (see `external/open-policy-infra`)
- Add CI workflows for tests and image builds