from google.cloud import secretmanager


def load_env_from_secret_manager(
    *,
    secret_name: str,
    project_id: str,
    target_path: str = ".env",
) -> None:
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    env_content = response.payload.data.decode("utf-8")
    with open(target_path, "w") as f:
        f.write(env_content)
