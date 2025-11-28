"""SecretVault abstraction for secret management.

Provides a unified interface for accessing secrets regardless of
the underlying storage (LocalStack, AWS Secrets Manager, env vars).
"""

import json
import os
from abc import ABC, abstractmethod
from typing import Any, Optional

import boto3
from botocore.exceptions import ClientError

from app.config import get_settings


class SecretVault(ABC):
    """Abstract base class for secret storage.

    Implementations:
    - LocalStackSecretVault: Uses LocalStack Secrets Manager (dev)
    - AWSSecretVault: Uses real AWS Secrets Manager (prod)
    - EnvSecretVault: Falls back to environment variables (testing)
    """

    @abstractmethod
    async def get_secret(self, name: str) -> str:
        """Retrieve a secret value by name.

        Args:
            name: Secret name/key

        Returns:
            Secret value as string

        Raises:
            KeyError: If secret not found
        """
        pass

    @abstractmethod
    async def get_secret_json(self, name: str) -> dict[str, Any]:
        """Retrieve a secret as parsed JSON.

        Args:
            name: Secret name/key

        Returns:
            Parsed JSON as dict

        Raises:
            KeyError: If secret not found
            ValueError: If secret is not valid JSON
        """
        pass

    @abstractmethod
    async def put_secret(self, name: str, value: str, description: Optional[str] = None) -> None:
        """Store or update a secret.

        Args:
            name: Secret name/key
            value: Secret value
            description: Optional description
        """
        pass

    @abstractmethod
    async def delete_secret(self, name: str) -> None:
        """Delete a secret.

        Args:
            name: Secret name/key
        """
        pass


class LocalStackSecretVault(SecretVault):
    """SecretVault implementation using LocalStack/AWS Secrets Manager."""

    def __init__(
        self,
        endpoint_url: Optional[str] = None,
        region: Optional[str] = None,
    ):
        """Initialize the vault.

        Args:
            endpoint_url: Override endpoint (for LocalStack)
            region: AWS region
        """
        settings = get_settings()

        self._client = boto3.client(
            "secretsmanager",
            endpoint_url=endpoint_url or settings.aws_endpoint_url,
            region_name=region or settings.aws_region,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
        )

    async def get_secret(self, name: str) -> str:
        """Retrieve a secret value by name."""
        try:
            response = self._client.get_secret_value(SecretId=name)
            return response["SecretString"]
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                raise KeyError(f"Secret not found: {name}")
            raise

    async def get_secret_json(self, name: str) -> dict[str, Any]:
        """Retrieve a secret as parsed JSON."""
        value = await self.get_secret(name)
        try:
            return json.loads(value)
        except json.JSONDecodeError as e:
            raise ValueError(f"Secret {name} is not valid JSON: {e}")

    async def put_secret(self, name: str, value: str, description: Optional[str] = None) -> None:
        """Store or update a secret."""
        try:
            # Try to update existing secret
            self._client.put_secret_value(SecretId=name, SecretString=value)
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                # Create new secret
                create_args = {"Name": name, "SecretString": value}
                if description:
                    create_args["Description"] = description
                self._client.create_secret(**create_args)
            else:
                raise

    async def delete_secret(self, name: str) -> None:
        """Delete a secret."""
        try:
            self._client.delete_secret(SecretId=name, ForceDeleteWithoutRecovery=True)
        except ClientError as e:
            if e.response["Error"]["Code"] != "ResourceNotFoundException":
                raise


class EnvSecretVault(SecretVault):
    """SecretVault implementation using environment variables.

    Useful for testing and simple deployments.
    Secret names are converted to env var names:
    - "jarvis/dev/jwt" -> "JARVIS_DEV_JWT"
    """

    def _name_to_env(self, name: str) -> str:
        """Convert secret name to environment variable name."""
        return name.replace("/", "_").replace("-", "_").upper()

    async def get_secret(self, name: str) -> str:
        """Retrieve a secret from environment variables."""
        env_name = self._name_to_env(name)
        value = os.environ.get(env_name)
        if value is None:
            raise KeyError(f"Secret not found: {name} (env: {env_name})")
        return value

    async def get_secret_json(self, name: str) -> dict[str, Any]:
        """Retrieve a secret as parsed JSON."""
        value = await self.get_secret(name)
        try:
            return json.loads(value)
        except json.JSONDecodeError as e:
            raise ValueError(f"Secret {name} is not valid JSON: {e}")

    async def put_secret(self, name: str, value: str, description: Optional[str] = None) -> None:
        """Store a secret in environment (for testing only)."""
        env_name = self._name_to_env(name)
        os.environ[env_name] = value

    async def delete_secret(self, name: str) -> None:
        """Delete a secret from environment."""
        env_name = self._name_to_env(name)
        os.environ.pop(env_name, None)


def get_secret_vault() -> SecretVault:
    """Factory function to get appropriate SecretVault implementation."""
    settings = get_settings()

    if settings.aws_endpoint_url:
        # LocalStack or custom endpoint
        return LocalStackSecretVault()
    elif settings.is_production:
        # Production AWS
        return LocalStackSecretVault(endpoint_url=None)
    else:
        # Fallback to env vars
        return EnvSecretVault()
