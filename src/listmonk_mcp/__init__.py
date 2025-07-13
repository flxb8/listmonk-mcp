"""Listmonk MCP Server package."""

__version__ = "0.1.0"

# Core components
from .client import ListmonkClient, ListmonkAPIError
from .config import Config, get_config
from .server import mcp

# Essential models
from .models import (
    Subscriber,
    Campaign,
    MailingList,
    Template,
    TransactionalEmailModel,
)

__all__ = [
    "ListmonkClient",
    "ListmonkAPIError", 
    "Config",
    "Subscriber",
    "MailingList",
    "Campaign", 
    "Template",
    "TransactionalEmailModel",
    "get_config",
    "mcp"
]