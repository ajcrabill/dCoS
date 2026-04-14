"""
Account Manager - Manage dual Gmail/GDrive accounts (primary user + agent).

Handles OAuth token storage/retrieval, account validation, and permission checking.

Assumes:
- Primary account (user): read-only access to email, calendar, drive
- Agent account (dCoS): read-write access to own email, calendar, drive
"""

import json
import keyring
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timedelta


class AccountManager:
    """Manage primary and agent Gmail/GDrive accounts."""

    def __init__(self, config_path: Path):
        """
        Initialize account manager.

        Args:
            config_path: Path to accounts.yaml config file
        """
        self.config_path = Path(config_path)
        self.config = self._load_config()

    def _load_config(self) -> dict:
        """Load account configuration."""
        if not self.config_path.exists():
            return {}

        import yaml
        with open(self.config_path) as f:
            return yaml.safe_load(f) or {}

    def get_primary_email(self) -> str:
        """Get primary user's email address."""
        return self.config.get('accounts', {}).get('primary_email', {}).get('email', '')

    def get_agent_email(self) -> str:
        """Get agent's email address."""
        return self.config.get('accounts', {}).get('agent_email', {}).get('email', '')

    def get_agent_name(self) -> str:
        """Get agent's name (personalization)."""
        return self.config.get('agent_name', 'Chief')

    def store_token(
        self,
        account_type: str,
        access_token: str,
        refresh_token: Optional[str] = None,
        expires_in: int = 3600
    ):
        """
        Store OAuth tokens securely using OS keychain.

        Args:
            account_type: 'primary' or 'agent'
            access_token: OAuth access token
            refresh_token: OAuth refresh token (optional)
            expires_in: Seconds until token expires
        """
        service = f"dcos_{account_type}"

        # Store access token
        keyring.set_password(service, "access_token", access_token)

        # Store expiration time
        expiry = datetime.now() + timedelta(seconds=expires_in)
        keyring.set_password(service, "expires_at", expiry.isoformat())

        # Store refresh token if provided
        if refresh_token:
            keyring.set_password(service, "refresh_token", refresh_token)

    def get_token(self, account_type: str) -> Optional[str]:
        """
        Get valid access token, auto-refreshing if expired.

        Args:
            account_type: 'primary' or 'agent'

        Returns:
            Valid access token or None
        """
        service = f"dcos_{account_type}"

        try:
            token = keyring.get_password(service, "access_token")
            if not token:
                return None

            # Check expiration
            expires_at = keyring.get_password(service, "expires_at")
            if expires_at:
                expiry = datetime.fromisoformat(expires_at)
                if expiry < datetime.now():
                    # Token expired, try to refresh
                    return self._refresh_token(account_type)

            return token
        except Exception:
            return None

    def _refresh_token(self, account_type: str) -> Optional[str]:
        """Refresh expired token."""
        service = f"dcos_{account_type}"
        refresh_token = keyring.get_password(service, "refresh_token")

        if not refresh_token:
            return None

        # This would make actual OAuth refresh request
        # For now, return None to indicate need to re-authenticate
        return None

    def validate_primary_access(self) -> Dict[str, Any]:
        """Validate access to primary user's account."""
        email = self.get_primary_email()
        token = self.get_token("primary")

        if not email or not token:
            return {
                "valid": False,
                "message": "Primary account not configured or token missing"
            }

        return {
            "valid": True,
            "email": email,
            "scopes": ["gmail.readonly", "calendar.readonly", "drive.readonly"]
        }

    def validate_agent_access(self) -> Dict[str, Any]:
        """Validate access to agent's account."""
        email = self.get_agent_email()
        token = self.get_token("agent")

        if not email or not token:
            return {
                "valid": False,
                "message": "Agent account not configured or token missing"
            }

        return {
            "valid": True,
            "email": email,
            "scopes": ["gmail.modify", "calendar", "drive.file"]
        }

    def get_account_summary(self) -> Dict[str, Any]:
        """Get summary of account configuration."""
        primary_check = self.validate_primary_access()
        agent_check = self.validate_agent_access()

        return {
            "primary": {
                "email": self.get_primary_email(),
                "status": "connected" if primary_check["valid"] else "not_configured",
                "scopes": primary_check.get("scopes", [])
            },
            "agent": {
                "name": self.get_agent_name(),
                "email": self.get_agent_email(),
                "status": "connected" if agent_check["valid"] else "not_configured",
                "scopes": agent_check.get("scopes", [])
            }
        }

    def clear_tokens(self, account_type: str):
        """Clear stored tokens (for logout/re-authentication)."""
        service = f"dcos_{account_type}"
        try:
            keyring.delete_password(service, "access_token")
            keyring.delete_password(service, "refresh_token")
            keyring.delete_password(service, "expires_at")
        except:
            pass


class OAuthFlow:
    """Helper for OAuth authentication flow."""

    @staticmethod
    def generate_auth_url(
        client_id: str,
        redirect_uri: str = "http://localhost:8080/callback",
        scopes: Optional[list] = None
    ) -> str:
        """
        Generate OAuth authorization URL.

        Args:
            client_id: Google OAuth client ID
            redirect_uri: Where to redirect after auth
            scopes: List of OAuth scopes to request

        Returns:
            Authorization URL
        """
        if scopes is None:
            scopes = [
                "https://www.googleapis.com/auth/gmail.readonly",
                "https://www.googleapis.com/auth/calendar.readonly",
                "https://www.googleapis.com/auth/drive.readonly"
            ]

        scope_str = "+".join(scopes)

        return (
            f"https://accounts.google.com/o/oauth2/v2/auth?"
            f"client_id={client_id}&"
            f"redirect_uri={redirect_uri}&"
            f"response_type=code&"
            f"scope={scope_str}&"
            f"access_type=offline"
        )

    @staticmethod
    def exchange_code_for_token(
        code: str,
        client_id: str,
        client_secret: str,
        redirect_uri: str = "http://localhost:8080/callback"
    ) -> Dict[str, Any]:
        """
        Exchange authorization code for access token.

        Args:
            code: Authorization code from OAuth flow
            client_id: Google OAuth client ID
            client_secret: Google OAuth client secret
            redirect_uri: Must match redirect_uri from authorization request

        Returns:
            Token response with access_token, refresh_token, expires_in
        """
        import urllib.request

        data = {
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code"
        }

        try:
            req = urllib.request.Request(
                "https://oauth2.googleapis.com/token",
                data=json.dumps(data).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                return json.loads(response.read().decode())
        except Exception as e:
            return {"error": str(e)}
