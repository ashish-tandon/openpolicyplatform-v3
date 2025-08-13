# Service Readiness Checklist

- Audit Variables
  - Env vars documented in `docs/operations/environment-variables.md`
  - Central config keys in `config/central-config.yaml`
- Compliance
  - Ports match assigned; host/IP restrictions applied
  - Liveness/Readiness endpoints implemented
- Documentation
  - README present with purpose and usage
  - Inputs/Outputs and functions declared (API contracts or CLI usage)
- Tests
  - Unit tests green
  - Integration tests scheduled (if applicable)
  - Pre-deploy test plan documented
- Container Standards
  - Non-root user (recommended), pinned dependencies
  - Healthchecks
  - Minimal base image