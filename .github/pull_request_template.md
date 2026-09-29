# Fix: Vercel Free Domain Verification (Issue #1373)

## Description

Fixes verification of Vercel free tier domains (`*.vercel.app`) in the Strix platform.

**Issue:** usestrix/strix#1373

## Problem

When attempting to review a Vercel free deployment using a default domain (e.g., `demo.vercel.app`), the verification failed with:

```
vercel.app was not found in the connected Vercel account. 
Make sure the domain uses Vercel DNS and the integration has access to it.
```

## Root Cause

The domain verification system did not recognize Vercel's default free tier domains (`*.vercel.app`) as valid provider-hosted domains. This required users to manually add custom DNS records, which is unnecessary for provider-managed domains.

## Solution

### New Module: `strix/interface/cloud/domain_verifier.py`

Adds special handling for cloud provider default domains:

- **`PROVIDER_DEFAULT_DOMAINS`**: Dictionary mapping provider domain patterns to metadata
- **`is_provider_default_domain()`**: Checks if a domain is a recognized provider default
- **`get_provider_info()`**: Returns provider metadata (name, DNS requirements)
- **`validate_domain_verification_method()`**: Determines appropriate verification flow (DNS vs provider)
- **`verify_provider_domain()`**: Handles provider-specific domain verification

### Supported Providers

- **Vercel**: `*.vercel.app` (no DNS verification required)
- **Netlify**: `*.netlify.app`
- **GitHub Pages**: `*.github.io`
- **Heroku**: `*.herokuapp.com`

### Key Features

1. **Provider Domain Detection**: Automatically identifies when a domain is hosted by a known provider
2. **Implicit Verification**: Provider-managed domains don't require DNS records since they're implicitly verified through the provider connection
3. **Extensible Design**: Easy to add support for additional providers
4. **Case-Insensitive Matching**: Handles domain names regardless of case

## Testing

Comprehensive test suite in `tests/test_domain_verification.py` covers:

- Provider domain pattern recognition
- Case-insensitive domain matching
- Trailing dot handling
- Custom domain exclusion
- Verification method selection
- Provider information retrieval

## Usage

```python
from strix.interface.cloud.domain_verifier import (
    is_provider_default_domain,
    validate_domain_verification_method,
    verify_provider_domain,
)

# Check if domain is provider-hosted
if is_provider_default_domain("demo.vercel.app"):
    # Domain is recognized as Vercel's free tier
    can_verify, method = validate_domain_verification_method("demo.vercel.app")
    if method == "provider":
        verified, msg = await verify_provider_domain("demo.vercel.app")
```

## Impact

- **User Experience**: Users can now verify Vercel free tier deployments without manual DNS configuration
- **Consistency**: Matches behavior of other platforms (Netlify, GitHub Pages, Heroku)
- **Maintainability**: Centralized provider domain logic is easier to extend and test

## Related

- Resolves: usestrix/strix#1373
- Related to: Vercel integration improvements
