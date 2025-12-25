FROM eclipse-temurin:21-jre-jammy

# Install required system deps
RUN apt-get update && \
    apt-get install -y \
      curl \
      ca-certificates \
      python3 \
      python3-distutils \
      tar \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt

# Install gcloud via tarball (component manager ENABLED)
RUN curl -fsSL \
    https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-472.0.0-linux-x86_64.tar.gz \
    -o gcloud.tar.gz && \
    tar -xzf gcloud.tar.gz && \
    ./google-cloud-sdk/install.sh --quiet

# Using netcat to check whether firestore emulator has been spun up
RUN apt-get update && apt-get install -y netcat-openbsd

ENV PATH="/opt/google-cloud-sdk/bin:$PATH"

# Install Firestore emulator
RUN gcloud components install cloud-firestore-emulator --quiet

EXPOSE 8000

CMD [ "gcloud", "emulators", "firestore", "start", "--host-port=0.0.0.0:8000" ]

