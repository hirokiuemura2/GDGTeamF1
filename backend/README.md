# Backend Guide

## Quick Start

### 0. Login and get service account key

> [!NOTE]
>
> Please check that you have the `gcloud` CLI installed before you run the following commands. For Mac users, install it with `brew install gcloud-cli`. For the Windows and Linux users, check [the official docs](https://docs.cloud.google.com/sdk/docs/install-sdk). 

```bash
# Export the project ID and service account that is currently used by our project
export PROJECT_ID=gdgteamf1
export SA_NAME=fin-app

# Log in and set project ID
gcloud auth login
gcloud config set project $PROJECT_ID

# Check the service account and save its credentials
gcloud iam service-accounts keys create ./key.json \
  --iam-account "$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com"
```

> [!TIP]
>
> You can use:
> - `gcloud projects list`: check the info of all your GCP projects
> - `gcloud iam service-accounts list`: check the info of your service accounts.

### 1. Spin up the backend server with different modes 

```bash
# Build and start services with in production mode
make build prod

# Build and start services in development mode
make build-dev dev

# Build and start services in test mode and perform cleanup
make build-test test clean
```

> [!NOTE]
> 
> - If you don't want to build the image again, just remove the build flag and run the server mode you want.
> - If you what to access firestore emulator with a user interface, spin up server in dev mode and access `http://localhost:4000` through user browser.

### 2. Differences between modes

#### Production Mode

- Reflects how the server actually works in production.
- The `production` mode uses real firestore database while the other two modes use containerized firestore emulators to test db operations.

> [!IMPORTANT]
>
> - For the `production` mode to work, create `.env.local.prod` and put `GCP_PROJECT_ID=<your-gcp-project-id>` in it.

#### Test Mode

- Spin up the backend server and firestore emulator for testing and then shut them down

#### Development Mode

- For the `development` mode to work, you need to download the `.env` file from Google's secret manager using the following command. It downloads the environment variables used in production and saves them into a `.env` file.

```bash
gcloud secrets versions access latest \
--secret=gdgteamf1-env \
--format='get(payload.data)' \
| tr "_-" "\+" \
| base64 -d \
> .env
```

> [!IMPORTANT]
>
> Ports that you will need for development
> - `localhost:8080`: backend server
> - `localhost:8080/docs`: all the docs for the current API 
> - `localhost:8000`: firestore database
> - `localhost:4000`: firebase emulator UI


### 3. Environment Variables

Here is a short introduction to each environment variable used in production. Honestly, except for the external API keys, it's not recommended to replace any one of them.

- `CURRENCY_API_KEY`
  - Visit [Free Currency API](https://app.freecurrencyapi.com/login) to get one

- `JWT_AUTH_EXPIRES`
  - The expiry for access token
  - Default to `15 mins`

- `JWT_REFRESH_EXPIRES`
  - The expiry for the refresh token
  - Default to `20 days`

- `JWT_AUTH_ALGORITHM`
  - The digital signing algorithm used in JWT token creation
  - Default to `RS256`

- `JWT_AUTH_PRIVATE_KEY`
  - The key used to sign the payload and header parts of the JWT token. For more information, you can check out [JWT with RSA](https://community.inkdrop.app/d9dcf4a9124403cffb317313f835fe63/kAdYbp8A).
  - To get one, run `openssl genrsa -out private-key.pem 2048`.

- `JWT_AUTH_PUBLIC_KEY`
  - The key used to verify a `JWT` token.
  - To get one, run `openssl rsa -in private-key.pem -pubout -out public-key.pem.pub` after you have created and saved your private key to `private-key.pem`.

