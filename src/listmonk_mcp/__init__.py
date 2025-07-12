"""Listmonk MCP Server package."""

__version__ = "0.1.0"

# Core components
from .client import ListmonkClient, ListmonkAPIError
from .config import Config, load_config, validate_config
from .server import mcp

# Data validation layer
from .exceptions import (
    ListmonkMCPError,
    ValidationError,
    AuthenticationError,
    APIError,
    ConfigurationError,
    OperationError,
    ResourceNotFoundError,
    DuplicateResourceError,
    convert_listmonk_api_error,
    format_mcp_error,
)

from .models import (
    # Core entities
    Subscriber,
    Campaign,
    MailingList,
    Template,
    
    # Create/Update models
    CreateSubscriberModel,
    UpdateSubscriberModel,
    CreateListModel,
    UpdateListModel,
    CreateCampaignModel,
    UpdateCampaignModel,
    CreateTemplateModel,
    UpdateTemplateModel,
    TransactionalEmailModel,
    
    # Enums
    SubscriberStatusEnum,
    CampaignStatusEnum,
    CampaignTypeEnum,
    ContentTypeEnum,
    ListTypeEnum,
    OptinTypeEnum,
    TemplateTypeEnum,
    
    # MCP-specific
    MCPToolResult,
    MCPResourceContent,
)

__all__ = [
    # Core
    "ListmonkClient",
    "ListmonkAPIError", 
    "Config",
    "load_config",
    "validate_config",
    "mcp",
    
    # Exceptions
    "ListmonkMCPError",
    "ValidationError",
    "AuthenticationError",
    "APIError",
    "ConfigurationError",
    "OperationError",
    "ResourceNotFoundError",
    "DuplicateResourceError",
    "convert_listmonk_api_error",
    "format_mcp_error",
    
    # Models
    "Subscriber",
    "Campaign", 
    "MailingList",
    "Template",
    "CreateSubscriberModel",
    "UpdateSubscriberModel",
    "CreateListModel",
    "UpdateListModel",
    "CreateCampaignModel",
    "UpdateCampaignModel",
    "CreateTemplateModel",
    "UpdateTemplateModel",
    "TransactionalEmailModel",
    
    # Enums
    "SubscriberStatusEnum",
    "CampaignStatusEnum",
    "CampaignTypeEnum",
    "ContentTypeEnum",
    "ListTypeEnum",
    "OptinTypeEnum",
    "TemplateTypeEnum",
    
    # MCP
    "MCPToolResult",
    "MCPResourceContent",
]