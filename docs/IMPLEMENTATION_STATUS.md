# Implementation status

This repository is a clean first implementation baseline, not a modification of the presentation prototype.

## Implemented

- Environment/build-time product identity and replaceable placeholder assets.
- Django 5.2.16 split settings, custom email user, verification, reset, merchant approval and deletion request.
- One-account/one-location MVP constraint.
- Configurable domains, questions, translations and versioned per-language prompts in Django Admin.
- Seed data for restaurant, hotel, salon/barbershop and retail.
- Stable opaque QR tokens, PNG generation, Google-link allowlist validation and advanced token rotation.
- Anonymous customer web flow with structured ratings, optional comment, exactly three drafts, editing, clipboard recovery and same-tab Google redirect.
- LiteLLM OpenAI-compatible generation client with timeout, concurrency limit, strict validation, one retry and two-generation session cap.
- Funnel events, overview calculations, 7/30/90 periods, trend/aspect charts, rule-based highlights and merchant feedback records.
- Expo React Native TypeScript merchant app with Overview, Feedback and QR tabs plus Settings.
- Docker/Compose/Caddy baseline, PostgreSQL backup/restore scripts, health endpoints and a self-hosted-model LiteLLM adapter.
- GitHub Actions CI, protected staging/production deployment jobs, immutable image promotion, CodeQL and dependency review.
- EAS build profiles targeting a production Android App Bundle and a 16 KB AAB alignment check script.

## Requires owner-supplied values later

- Final product/company/store identity and permanent Android package name.
- Real domains/DNS, staging/production hosts and registry/deployment credentials.
- Actual self-hosted model endpoint/name and prompt evaluation results.
- SMTP provider credentials.
- Privacy/retention/legal approval.
- Play Console and EAS project credentials.
- Real Google review links and merchant pilot data.

## Validation completed in the generation environment

- Python source compiled successfully with `compileall`.
- Public JavaScript passed Node syntax checking.
- YAML and JSON files parsed successfully.
- Secret-pattern scan found no embedded credential.

## Validation not executable in the generation environment

The sandbox package registries did not provide the required current Python/npm packages, and Docker was unavailable. Therefore Django tests, Expo type checking, dependency installation, container startup and EAS builds must run in GitHub CI or a normal development workstation. The repository does not fabricate a package lock or claim those runtime checks passed.
