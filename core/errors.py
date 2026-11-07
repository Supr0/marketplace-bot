class MarketplaceError(Exception):
    """Base error for the bot to catch"""

class SourceUnavailable(MarketplaceError):
    """Network, timeout errors etc. Repeat request."""

class SourceRejectedQuery(MarketplaceError):
    """Request rejected by the source, Don't repeat request."""