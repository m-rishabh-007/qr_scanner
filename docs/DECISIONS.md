# Recorded decisions

1. Working product identity uses replaceable ReviewFlow placeholders.
2. Initial domains: restaurant, hotel, salon and retail.
3. English only in the first release; translation fields and request language are retained for later Hindi support.
4. GitHub is the repository and CI/CD platform.
5. LiteLLM exposes an OpenAI-compatible `/v1/chat/completions` gateway.
6. Staging and production deployments require approval.
7. Email/password registration, email verification and password recovery are required.
8. Merchant registration requires administrator approval.
9. One merchant account owns one location in MVP.
10. Backend, public QR flow and merchant mobile app live in one monorepo.
