# Configuration model

## Runtime values

Backend product name, company name, public domain, support email, privacy email, database, mail service, LiteLLM endpoint, throttles and allowed Google hosts are environment variables.

## Build-time mobile values

`mobile/app.config.ts` reads:

- `APP_NAME`
- `APP_SLUG`
- `ANDROID_PACKAGE`
- `APP_SCHEME`
- `EXPO_PUBLIC_API_BASE_URL`
- optional asset paths

The app name and images are replaceable. The Android package identifier must be finalized before the first Play Console release.

## Configurable catalog

Domains, questions and prompt versions are database records and are managed in Django Admin. They can be activated/deactivated, reordered and versioned without changing mobile or public-web source code.

## Email provider

Django's `EMAIL_BACKEND` and standard SMTP settings are used. Local development uses console/Mailpit. Production can use any SMTP provider or a custom Django email backend without changing account API contracts.

## Deployment adapter

The included Compose/Caddy setup targets Ubuntu 22.04/24.04. GitHub workflows build immutable images and contain isolated deploy steps. Replace the deploy script or registry variables without changing application code.
