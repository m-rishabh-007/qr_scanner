# CI/CD and environment approvals

## Pull-request pipeline

The `CI` workflow runs backend linting, migration drift checks, PostgreSQL tests, a production settings check, mobile TypeScript/lint checks and a container build.

The repository intentionally keeps deployment code outside application code. The included adapter deploys Docker Compose through SSH to Ubuntu 22.04/24.04, but another cloud/container orchestrator can replace `ops/scripts/deploy-ssh-compose.sh` without changing the backend or app.

## GitHub environments

Create two GitHub environments:

- `staging`
- `production`

Configure required reviewers for both. Add environment-scoped secrets:

- `DEPLOY_SSH_KEY`
- `DEPLOY_HOST`
- `DEPLOY_USER`
- `DEPLOY_PATH`
- optional `REGISTRY_USERNAME` and `REGISTRY_PULL_TOKEN` when the container package is private; set environment variable `REGISTRY_AUTH_ENABLED=true`
- `EXPO_TOKEN` when mobile builds are enabled

Add environment variables for URLs and mobile identity. GitHub pauses jobs that reference a protected environment until an authorized reviewer approves them.

## Image promotion

Staging builds and pushes an immutable commit-SHA image. Production accepts the already tested image tag and does not rebuild it. This avoids deploying different bytes from those tested in staging.

## Registry

GHCR is the supplied default because it integrates with GitHub Actions. Change the registry/login/build steps if the final DevOps platform uses Docker Hub, ECR, GCR, ACR or a private registry. The application consumes only an image reference and is registry-independent.

## Mobile lockfile

The code generator environment could not access the public npm registry, so a package lock is not fabricated. On the first real repository checkout, run:

```bash
cd mobile
npm install
npx expo install --fix
git add package-lock.json package.json
git commit -m "chore: lock Expo dependencies"
```

After committing the real lockfile, replace `npm install` with `npm ci` in the two mobile workflows. This is deliberately documented rather than supplying an unverifiable lockfile.
