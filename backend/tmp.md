GDGTeamF1 — Backend (FastAPI, GCP, Docker)

- Implemented end-to-end JWT auth with access/refresh tokens, Argon2 password hashing, and token verification; added login, refresh, and session-check endpoints.
- Built currency conversion API using httpx and FreeCurrencyAPI with robust timeout/HTTP error handling and Pydantic v2 validation.
- Designed Firestore data model and repository/service layers; created expense API and offloaded blocking IO to threadpool where needed.
- Production secrets via Google Secret Manager; import-safe config/bootstrap; fixed Cloud Run commands and environment parity.
- Containerized local dev and CI with Docker Compose; integrated Firestore emulator and stabilized pytest suite.
- Auth + Google OAuth integration points prepared for frontend; expanded README to streamline onboarding.

Impact: Reduced onboarding time and test flakiness; enabled frontend integration with reliable auth and data APIs.

Tech: Python (FastAPI, Pydantic, httpx, PyJWT/Authlib, pwdlib/Argon2), Google Cloud (Firestore, Secret Manager), Docker/Compose, pytest, macOS/Linux.
