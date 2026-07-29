# GitHub App Setup Checklist for PR Prep

Use this checklist to register and configure a GitHub App for PR Prep in development, staging, or production.

## 1. Registration
- [ ] Go to **GitHub Settings > Developer Settings > GitHub Apps > New GitHub App**.
- [ ] Set **GitHub App name** (e.g. `PR-Prep-Staging`).
- [ ] Set **Homepage URL** (e.g. `https://your-domain.com`).
- [ ] Set **Webhook URL** (e.g. `https://api.your-domain.com/webhook/github`).
- [ ] Set **Webhook Secret** and record it in `.env` as `GITHUB_WEBHOOK_SECRET`.

## 2. Permissions required
### Repository Permissions:
- [ ] **Pull requests**: `Read & Write` (to fetch diffs and post PR reviews / inline comments).
- [ ] **Contents**: `Read-only` (to inspect files for RAG context).
- [ ] **Metadata**: `Read-only` (required by default).

### Subscribe to Events:
- [ ] Check **Pull request** event.

## 3. Credentials & Keys
- [ ] Note down **App ID** and save to `.env` as `GITHUB_APP_ID`.
- [ ] Generate a private key (`.pem` file), save it securely, and configure `GITHUB_PRIVATE_KEY_PATH` in `.env`.
- [ ] Download and verify private key permissions (`chmod 600`).

## 4. Local Webhook Testing (Smee.io / ngrok)
- [ ] For local development, use `smee` proxy or `ngrok`:
  ```bash
  npx smee -u https://smee.io/YOUR_CHANNEL -t http://localhost:8000/webhook/github
  ```
- [ ] Update Webhook URL in GitHub App settings with your proxy channel URL.

## 5. Verification
- [ ] Install the GitHub App on a test repository.
- [ ] Open a PR in the test repository and verify `pull_request.opened` event lands on the FastAPI `/webhook/github` endpoint with valid HMAC signature.
