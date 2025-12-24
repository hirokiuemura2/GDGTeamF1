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
> - $gcloud projects list$: check the info of all your GCP projects
> - $gcloud iam service-accounts list$: check the info of your service accounts.

### 1. Spin up the backend server with different modes 

```bash
# Build and start services with in production mode
make build prod

# Build and start services in development mode
make build-dev dev

# Build and start services in test mode and perform cleanup
make build-test test clean
```

> [!HINT]
> If you don't want to build the image again, just remove the build flag and run server mode you want.

> [!NOTE]
> The production mode uses real firestore database while the other two modes use containerized firestore emulators to test db operations.

