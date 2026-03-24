"""LangChain integration placeholder."""


def attach_sentinel(chain, organism):
    """Attach Sentinel organism metadata to a chain object."""
    setattr(chain, "sentinel_organism", organism)
    return chain
