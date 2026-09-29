"""Tests for domain verification, especially for provider default domains."""

import pytest

from strix.interface.cloud.domain_verifier import (
    get_provider_info,
    is_provider_default_domain,
    validate_domain_verification_method,
    verify_provider_domain,
)


class TestIsProviderDefaultDomain:
    """Test detection of provider-default domains."""

    def test_vercel_app_domain_is_recognized(self) -> None:
        """Vercel free tier domain should be recognized."""
        assert is_provider_default_domain("demo.vercel.app")

    def test_vercel_app_with_subdomain_is_recognized(self) -> None:
        """Vercel domain with multiple subdomains should be recognized."""
        assert is_provider_default_domain("my-app-123.vercel.app")

    def test_vercel_app_case_insensitive(self) -> None:
        """Domain matching should be case-insensitive."""
        assert is_provider_default_domain("DEMO.VERCEL.APP")
        assert is_provider_default_domain("Demo.Vercel.App")

    def test_vercel_app_with_trailing_dot(self) -> None:
        """Should handle trailing dots."""
        assert is_provider_default_domain("demo.vercel.app.")

    def test_netlify_app_domain_is_recognized(self) -> None:
        """Netlify free tier domain should be recognized."""
        assert is_provider_default_domain("my-site.netlify.app")

    def test_github_pages_domain_is_recognized(self) -> None:
        """GitHub Pages domain should be recognized."""
        assert is_provider_default_domain("user.github.io")

    def test_custom_domain_not_recognized(self) -> None:
        """Custom domains should not be recognized as provider domains."""
        assert not is_provider_default_domain("example.com")
        assert not is_provider_default_domain("custom.example.com")

    def test_vercel_com_not_recognized(self) -> None:
        """vercel.com (Vercel's own site) should not be recognized as a free domain."""
        # vercel.com itself is not a free domain pattern
        assert not is_provider_default_domain("vercel.com")

    def test_empty_domain(self) -> None:
        """Empty domain should not be recognized."""
        assert not is_provider_default_domain("")
        assert not is_provider_default_domain(None)


class TestGetProviderInfo:
    """Test retrieval of provider information."""

    def test_vercel_provider_info(self) -> None:
        """Should return Vercel provider info."""
        info = get_provider_info("demo.vercel.app")
        assert info is not None
        assert info["provider"] == "vercel"
        assert info["requires_dns"] is False

    def test_netlify_provider_info(self) -> None:
        """Should return Netlify provider info."""
        info = get_provider_info("my-site.netlify.app")
        assert info is not None
        assert info["provider"] == "netlify"
        assert info["requires_dns"] is False

    def test_custom_domain_returns_none(self) -> None:
        """Should return None for custom domains."""
        assert get_provider_info("example.com") is None


class TestValidateDomainVerificationMethod:
    """Test domain verification method selection."""

    def test_vercel_domain_uses_provider_verification(self) -> None:
        """Vercel domains should use provider verification."""
        can_verify, method = validate_domain_verification_method("demo.vercel.app")
        assert can_verify is True
        assert method == "provider"

    def test_custom_domain_uses_dns_verification(self) -> None:
        """Custom domains should use DNS verification."""
        can_verify, method = validate_domain_verification_method("example.com")
        assert can_verify is True
        assert method == "dns"

    def test_empty_domain_returns_unknown(self) -> None:
        """Empty domain should return unknown method."""
        can_verify, method = validate_domain_verification_method("")
        assert can_verify is False
        assert method == "unknown"


@pytest.mark.asyncio
async def test_verify_vercel_domain() -> None:
    """Vercel domain verification should succeed."""
    verified, message = await verify_provider_domain("demo.vercel.app")
    assert verified is True
    assert "vercel" in message.lower()
    assert "demo.vercel.app" in message


@pytest.mark.asyncio
async def test_verify_unknown_provider_domain() -> None:
    """Unknown provider domain should fail."""
    verified, message = await verify_provider_domain("example.com")
    assert verified is False
    assert "not a recognized provider domain" in message
