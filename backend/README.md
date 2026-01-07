# Backend Guide

## Quick Start

### 0. Login and get service account key

> [!NOTE]
>
> Please check that you have the `gcloud` CLI installed before you run the following commands. For Mac users, install it with `brew install gcloud-cli`. For Windows users, I'm sorry but you are on your own. 

```bash
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

#### Production Mode

- Reflects how the server actually work on production.
- The `production` mode uses real firestore database while the other two modes use containerized firestore emulators to test db operations.
- For the `production` mode to work, create `.env.local.prod` and put `GCP_PROJECT_ID=<your-gcp-project-id>` in it.

#### Development Mode

- For the `development` mode to work, you need a .env file with the following environment variables:

```bash
JWT_AUTH_EXPIRES=60
JWT_AUTH_ALGORITHM=RS256
JWT_AUTH_PRIVATE_KEY=""
JWT_AUTH_PUBLIC_KEY=""
CURRENCY_API_KEY=<your-currency-api-key>
GCP_PROJECT_ID=<your-gcp-project-id>
```

- `CURRENCY_API_KEY`: Visit [Free Currency API](https://app.freecurrencyapi.com/login) to get one
- `JWT_AUTH_PRIVATE_KEY`: Run `openssl genrsa -out private-key.pem 2048` and copy the value in the `private-key.pem` file.
- `JWT_AUTH_PUBLIC_KEY`: Run `openssl rsa -in private-key.pem -pubout -out public-key.pem.pub` and copy the value in the `public-key.pem.pub` file.

> [!IMPORTANT]
>
> Ports that you will need for the development
> - `localhost:8080`: backend server
> - `localhost:8080/docs`: all the docs for the current API 
> - `localhost:8000`: firestore database
> - `localhost:4000`: firebase emulator UI
