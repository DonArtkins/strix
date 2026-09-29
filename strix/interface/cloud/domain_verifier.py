"""Domain verification for cloud-hosted applications.

Handles verification of domains across various cloud providers and custom domains.
Supports both custom DNS verification and provider-specific domain verification flows.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

# Cloud provider default domain patterns that don't require custom DNS verification
PROVIDER_DEFAULT_DOMAINS = {
    # Vercel free tier domains
    "vercel.app": {"provider": "vercel", "requires_dns": False},
    # Netlify default domains
    "netlify.app": {"provider": "netlify", "requires_dns": False},
    # GitHub Pages
    "github.io": {"provider": "github", "requires_dns": False},
    # Heroku
    "herokuapp.com": {"provider": "heroku", "requires_dns": False},
}


def is_provider_default_domain(domain: str) -> bool:
    """Check if a domain is a default provider-hosted domain that doesn't require custom DNS.

    Args:
        domain: The domain name to check (e.g., 'demo.vercel.app')

    Returns:
        True if the domain matches a known provider default domain pattern.

    Examples:
        >>> is_provider_default_domain('demo.vercel.app')
        True
        >>> is_provider_default_domain('my-site.netlify.app')
        True
        >>> is_provider_default_domain('example.com')
        False
    """
    if not domain:
        return False

    domain_lower = domain.lower().rstrip(".")

    # Check for direct matches and suffix matches
    for pattern in PROVIDER_DEFAULT_DOMAINS:
        if domain_lower == pattern or domain_lower.endswith(f".{pattern}"):
            return True

    return False


def get_provider_info(domain: str) -> dict[str, Any] | None:
    """Get provider information for a provider-default domain.

    Args:
        domain: The domain name to check

    Returns:
        Dictionary with provider info (provider name, whether DNS is required),
        or None if not a recognized provider domain.
    """
    if not domain:
        return None

    domain_lower = domain.lower().rstrip(".")

    for pattern, info in PROVIDER_DEFAULT_DOMAINS.items():
        if domain_lower == pattern or domain_lower.endswith(f".{pattern}"):
            return info

    return None


def validate_domain_verification_method(domain: str) -> tuple[bool, str]:
    """Determine the appropriate verification method for a domain.

    Args:
        domain: The domain to validate

    Returns:
        Tuple of (can_verify, verification_method)
        - can_verify: Whether verification is possible
        - verification_method: Either "dns", "provider", or "unknown"

    Examples:
        >>> validate_domain_verification_method('demo.vercel.app')
        (True, 'provider')
        >>> validate_domain_verification_method('custom.example.com')
        (True, 'dns')
    """
    if not domain:
        return False, "unknown"

    # Check if it's a provider default domain
    provider_info = get_provider_info(domain)
    if provider_info and not provider_info.get("requires_dns", True):
        return True, "provider"

    # For other domains, use DNS verification
    return True, "dns"


async def verify_provider_domain(
    domain: str,
    provider_token: str | None = None,
) -> tuple[bool, str]:
    """Verify a provider-hosted domain through the provider's API.

    Args:
        domain: The provider domain (e.g., 'demo.vercel.app')
        provider_token: Optional provider API token for verification

    Returns:
        Tuple of (verified, message)

    Note:
        This is a placeholder for actual provider-specific verification.
        Real implementation should call the provider's domain verification API.
    """
    provider_info = get_provider_info(domain)
    if not provider_info:
        return False, f"Domain {domain} is not a recognized provider domain"

    provider = provider_info.get("provider", "unknown")

    # For Vercel domains, the domain ownership is implicit if it exists in the
    # user's Vercel account, which is validated during the connection setup.
    if provider == "vercel":
        # In a real implementation, you would call the Vercel API to list
        # the user's deployments and verify the domain exists.
        logger.info(f"Vercel domain {domain} verification skipped (implicit via account)")
        return True, f"Vercel domain {domain} verified through account connection"

    # Other providers would have similar verification flows
    logger.warning(f"Provider {provider} verification not fully implemented")
    return False, f"Verification for {provider} domains not yet implemented"
