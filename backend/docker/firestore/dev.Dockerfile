FROM node:20-slim

# Install deps
RUN apt-get update && \
    apt-get install -y curl ca-certificates gnupg && \
    rm -rf /var/lib/apt/lists/*

# Add Eclipse Temurin (Adoptium) repo
RUN curl -fsSL https://packages.adoptium.net/artifactory/api/gpg/key/public \
    | gpg --dearmor -o /usr/share/keyrings/adoptium.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/adoptium.gpg] https://packages.adoptium.net/artifactory/deb bookworm main" \
    > /etc/apt/sources.list.d/adoptium.list

# Install Java 21
RUN apt-get update && \
    apt-get install -y temurin-21-jre && \
    rm -rf /var/lib/apt/lists/*

# Install Firebase CLI
RUN npm install -g firebase-tools

WORKDIR /app

EXPOSE 8000 4000

CMD ["firebase", "emulators:start", "--project", "local-dev", "--debug", "--import", ".cache/firebase/emulators/firestore-data", "--export-on-exit"]

