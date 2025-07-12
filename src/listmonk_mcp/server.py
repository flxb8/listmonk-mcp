"""Listmonk MCP Server using FastMCP framework."""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from contextlib import asynccontextmanager

from mcp import FastMCP
from mcp.types import TextContent, Tool, Resource

from .config import Config, load_config, validate_config
from .client import ListmonkClient, ListmonkAPIError, create_client


# Global state
_client: Optional[ListmonkClient] = None
_config: Optional[Config] = None

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan():
    """Server lifespan context manager."""
    global _client, _config
    
    try:
        # Load and validate configuration
        _config = load_config()
        validate_config()
        
        logger.info(f"Connecting to Listmonk at {_config.url}")
        
        # Create and connect client
        _client = await create_client(_config)
        
        logger.info("Listmonk MCP Server started successfully")
        yield
        
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        raise
    finally:
        # Cleanup
        if _client:
            await _client.close()
            logger.info("Listmonk client disconnected")


# Create FastMCP server with lifespan
mcp = FastMCP("Listmonk MCP Server", lifespan=lifespan)


def get_client() -> ListmonkClient:
    """Get the global Listmonk client."""
    if _client is None:
        raise RuntimeError("Listmonk client not initialized")
    return _client


def get_config() -> Config:
    """Get the global configuration."""
    if _config is None:
        raise RuntimeError("Configuration not loaded")
    return _config


# Health Check Tool
@mcp.tool()
async def check_listmonk_health() -> Dict[str, Any]:
    """Check if Listmonk server is healthy and accessible."""
    try:
        client = get_client()
        health_data = await client.health_check()
        
        return {
            "status": "healthy",
            "listmonk_health": health_data,
            "server_url": get_config().url
        }
    except ListmonkAPIError as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "status_code": e.status_code
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


# Subscriber Management Tools
@mcp.tool()
async def add_subscriber(
    email: str,
    name: str,
    lists: List[int],
    status: str = "enabled",
    attributes: Optional[Dict[str, Any]] = None,
    preconfirm: bool = False
) -> Dict[str, Any]:
    """
    Add a new subscriber to Listmonk.
    
    Args:
        email: Subscriber email address
        name: Subscriber name
        lists: List of mailing list IDs to subscribe to
        status: Subscriber status (enabled, disabled, blocklisted)
        attributes: Custom subscriber attributes
        preconfirm: Whether to preconfirm subscriptions
    """
    try:
        client = get_client()
        result = await client.create_subscriber(
            email=email,
            name=name,
            status=status,
            lists=lists,
            attribs=attributes or {},
            preconfirm_subscriptions=preconfirm
        )
        
        return {
            "success": True,
            "subscriber": result.get("data"),
            "message": f"Subscriber {email} added successfully"
        }
    except ListmonkAPIError as e:
        return {
            "success": False,
            "error": str(e),
            "status_code": e.status_code
        }


@mcp.tool()
async def update_subscriber(
    subscriber_id: int,
    email: Optional[str] = None,
    name: Optional[str] = None,
    status: Optional[str] = None,
    lists: Optional[List[int]] = None,
    attributes: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Update an existing subscriber.
    
    Args:
        subscriber_id: ID of the subscriber to update
        email: New email address
        name: New name
        status: New status (enabled, disabled, blocklisted)
        lists: New list of mailing list IDs
        attributes: New custom attributes
    """
    try:
        client = get_client()
        result = await client.update_subscriber(
            subscriber_id=subscriber_id,
            email=email,
            name=name,
            status=status,
            lists=lists,
            attribs=attributes
        )
        
        return {
            "success": True,
            "subscriber": result.get("data"),
            "message": f"Subscriber {subscriber_id} updated successfully"
        }
    except ListmonkAPIError as e:
        return {
            "success": False,
            "error": str(e),
            "status_code": e.status_code
        }


@mcp.tool()
async def remove_subscriber(subscriber_id: int) -> Dict[str, Any]:
    """
    Remove a subscriber from Listmonk.
    
    Args:
        subscriber_id: ID of the subscriber to remove
    """
    try:
        client = get_client()
        await client.delete_subscriber(subscriber_id)
        
        return {
            "success": True,
            "message": f"Subscriber {subscriber_id} removed successfully"
        }
    except ListmonkAPIError as e:
        return {
            "success": False,
            "error": str(e),
            "status_code": e.status_code
        }


@mcp.tool()
async def change_subscriber_status(subscriber_id: int, status: str) -> Dict[str, Any]:
    """
    Change subscriber status.
    
    Args:
        subscriber_id: ID of the subscriber
        status: New status (enabled, disabled, blocklisted)
    """
    try:
        client = get_client()
        result = await client.set_subscriber_status(subscriber_id, status)
        
        return {
            "success": True,
            "subscriber": result.get("data"),
            "message": f"Subscriber {subscriber_id} status changed to {status}"
        }
    except ListmonkAPIError as e:
        return {
            "success": False,
            "error": str(e),
            "status_code": e.status_code
        }


# Subscriber Resources
@mcp.resource("subscriber/{subscriber_id}")
async def get_subscriber_by_id(subscriber_id: str) -> str:
    """Get subscriber details by ID."""
    try:
        client = get_client()
        result = await client.get_subscriber(int(subscriber_id))
        
        subscriber = result.get("data", {})
        
        return f"""# Subscriber Details

**ID:** {subscriber.get('id')}
**Email:** {subscriber.get('email')}
**Name:** {subscriber.get('name')}
**Status:** {subscriber.get('status')}
**Created:** {subscriber.get('created_at')}
**Updated:** {subscriber.get('updated_at')}

## Lists
{chr(10).join(f"- {lst.get('name')} (ID: {lst.get('id')})" for lst in subscriber.get('lists', []))}

## Attributes
{chr(10).join(f"- **{k}:** {v}" for k, v in subscriber.get('attribs', {}).items())}
"""
    
    except ListmonkAPIError as e:
        return f"Error retrieving subscriber {subscriber_id}: {str(e)}"


@mcp.resource("subscriber/email/{email}")
async def get_subscriber_by_email(email: str) -> str:
    """Get subscriber details by email address."""
    try:
        client = get_client()
        result = await client.get_subscriber_by_email(email)
        
        subscriber = result.get("data", {})
        
        return f"""# Subscriber Details

**ID:** {subscriber.get('id')}
**Email:** {subscriber.get('email')}
**Name:** {subscriber.get('name')}
**Status:** {subscriber.get('status')}
**Created:** {subscriber.get('created_at')}
**Updated:** {subscriber.get('updated_at')}

## Lists
{chr(10).join(f"- {lst.get('name')} (ID: {lst.get('id')})" for lst in subscriber.get('lists', []))}

## Attributes
{chr(10).join(f"- **{k}:** {v}" for k, v in subscriber.get('attribs', {}).items())}
"""
    
    except ListmonkAPIError as e:
        return f"Error retrieving subscriber {email}: {str(e)}"


@mcp.resource("subscribers")
async def list_subscribers() -> str:
    """List all subscribers with basic information."""
    try:
        client = get_client()
        result = await client.get_subscribers(per_page=50)
        
        data = result.get("data", {})
        subscribers = data.get("results", [])
        total = data.get("total", 0)
        
        subscriber_list = []
        for sub in subscribers:
            lists_str = ", ".join(lst.get('name', '') for lst in sub.get('lists', []))
            subscriber_list.append(
                f"- **{sub.get('name')}** ({sub.get('email')}) - Status: {sub.get('status')} - Lists: {lists_str}"
            )
        
        return f"""# Subscribers List

**Total Subscribers:** {total}
**Showing:** {len(subscribers)} subscribers

{chr(10).join(subscriber_list)}

*Use the get_subscriber_by_id or get_subscriber_by_email resources for detailed information.*
"""
    
    except ListmonkAPIError as e:
        return f"Error retrieving subscribers: {str(e)}"


# List Management Tools
@mcp.tool()
async def create_mailing_list(
    name: str,
    type: str = "public",
    optin: str = "single",
    tags: Optional[List[str]] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new mailing list.
    
    Args:
        name: List name
        type: List type (public, private)
        optin: Opt-in type (single, double)
        tags: List tags
        description: List description
    """
    try:
        client = get_client()
        result = await client.create_list(
            name=name,
            type=type,
            optin=optin,
            tags=tags or [],
            description=description
        )
        
        return {
            "success": True,
            "list": result.get("data"),
            "message": f"Mailing list '{name}' created successfully"
        }
    except ListmonkAPIError as e:
        return {
            "success": False,
            "error": str(e),
            "status_code": e.status_code
        }


# Main server entry point
async def main():
    """Main server entry point."""
    try:
        await mcp.run()
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())