# Deployment Control Policy

## Rolling Policy
- Prepare new image (build and push) but do not switch traffic yet
- Bring down previous service instance cleanly
  - For API/Web Deployments: scale to 0 and wait for termination
  - For CronJobs: ensure no running Jobs; suspend CronJob if needed
- Deploy new image and scale up (API/Web)
- Re-enable CronJobs/schedules

## Helm Strategy
- Use `helm upgrade --install` with `--wait --timeout 5m` and `--atomic` to rollback on failure

## K8s Notes
- Ensure `terminationGracePeriodSeconds` is set
- Use readiness probes to prevent traffic before ready
- Use pre-stop hooks if necessary