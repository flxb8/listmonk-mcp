"""Listmonk API client abstraction using httpx."""

import asyncio
from typing import Dict, Any, List, Optional, Union
from urllib.parse import urljoin

import httpx
from httpx import AsyncClient, Response

from .config import Config, ListmonkConfig


class ListmonkAPIError(Exception):
    """Base exception for Listmonk API errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class ListmonkClient:
    """Async HTTP client for Listmonk API operations."""
    
    def __init__(self, config: ListmonkConfig):
        self.config = config
        self.base_url = config.url.rstrip('/')
        self._client: Optional[AsyncClient] = None
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def connect(self) -> None:
        """Initialize the HTTP client with authentication."""
        # Use API token authentication format: "username:token"
        auth_token = f"{self.config.username}:{self.config.password}"
        
        self._client = AsyncClient(
            timeout=httpx.Timeout(self.config.timeout),
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
            headers={
                "User-Agent": "Listmonk-MCP-Server/0.1.0",
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"token {auth_token}"
            }
        )
        
        # Test connection with health check
        await self.health_check()
    
    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
    
    def _get_client(self) -> AsyncClient:
        """Get the HTTP client, raising error if not connected."""
        if self._client is None:
            raise RuntimeError("Client not connected. Call connect() first or use as async context manager.")
        return self._client
    
    def _build_url(self, endpoint: str) -> str:
        """Build full URL from endpoint."""
        return urljoin(f"{self.base_url}/", endpoint.lstrip('/'))
    
    async def _request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        retry_count: int = 0
    ) -> Dict[str, Any]:
        """Make HTTP request with retry logic and error handling."""
        client = self._get_client()
        url = self._build_url(endpoint)
        
        try:
            response = await client.request(
                method=method,
                url=url,
                params=params,
                json=json_data
            )
            
            return await self._handle_response(response)
            
        except httpx.RequestError as e:
            if retry_count < self.config.max_retries:
                await asyncio.sleep(2 ** retry_count)  # Exponential backoff
                return await self._request(method, endpoint, params, json_data, retry_count + 1)
            
            raise ListmonkAPIError(f"Request failed: {str(e)}")
    
    async def _handle_response(self, response: Response) -> Dict[str, Any]:
        """Handle HTTP response and extract data."""
        try:
            response_data = response.json()
        except Exception:
            response_data = {"text": response.text}
        
        if response.is_success:
            return response_data
        
        # Handle API errors
        error_message = response_data.get("message", f"HTTP {response.status_code}")
        raise ListmonkAPIError(
            message=error_message,
            status_code=response.status_code,
            response=response_data
        )
    
    # Health and Authentication
    async def health_check(self) -> Dict[str, Any]:
        """Check if Listmonk server is healthy and accessible."""
        return await self._request("GET", "/api/health")
    
    # Subscriber Operations
    async def get_subscribers(
        self, 
        page: int = 1, 
        per_page: int = 20,
        order_by: str = "created_at",
        order: str = "desc",
        query: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get subscribers with pagination and filtering."""
        params = {
            "page": page,
            "per_page": per_page,
            "order_by": order_by,
            "order": order,
        }
        if query:
            params["query"] = query
            
        return await self._request("GET", "/api/subscribers", params=params)
    
    async def get_subscriber(self, subscriber_id: int) -> Dict[str, Any]:
        """Get subscriber by ID."""
        return await self._request("GET", f"/api/subscribers/{subscriber_id}")
    
    async def get_subscriber_by_email(self, email: str) -> Dict[str, Any]:
        """Get subscriber by email address."""
        params = {"query": f"subscribers.email = '{email}'"}
        response = await self._request("GET", "/api/subscribers", params=params)
        
        if response.get("data", {}).get("results"):
            return {"data": response["data"]["results"][0]}
        else:
            raise ListmonkAPIError(f"Subscriber with email {email} not found", status_code=404)
    
    async def create_subscriber(
        self,
        email: str,
        name: str,
        status: str = "enabled",
        lists: Optional[List[int]] = None,
        attribs: Optional[Dict[str, Any]] = None,
        preconfirm_subscriptions: bool = False
    ) -> Dict[str, Any]:
        """Create a new subscriber."""
        data = {
            "email": email,
            "name": name,
            "status": status,
            "lists": lists or [],
            "attribs": attribs or {},
            "preconfirm_subscriptions": preconfirm_subscriptions
        }
        return await self._request("POST", "/api/subscribers", json_data=data)
    
    async def update_subscriber(
        self,
        subscriber_id: int,
        email: Optional[str] = None,
        name: Optional[str] = None,
        status: Optional[str] = None,
        lists: Optional[List[int]] = None,
        attribs: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Update an existing subscriber."""
        data = {}
        if email is not None:
            data["email"] = email
        if name is not None:
            data["name"] = name
        if status is not None:
            data["status"] = status
        if lists is not None:
            data["lists"] = lists
        if attribs is not None:
            data["attribs"] = attribs
            
        return await self._request("PUT", f"/api/subscribers/{subscriber_id}", json_data=data)
    
    async def delete_subscriber(self, subscriber_id: int) -> Dict[str, Any]:
        """Delete a subscriber."""
        return await self._request("DELETE", f"/api/subscribers/{subscriber_id}")
    
    async def set_subscriber_status(self, subscriber_id: int, status: str) -> Dict[str, Any]:
        """Set subscriber status (enabled, disabled, blocklisted)."""
        data = {"status": status}
        return await self._request("PUT", f"/api/subscribers/{subscriber_id}", json_data=data)
    
    # List Operations
    async def get_lists(self) -> Dict[str, Any]:
        """Get all mailing lists."""
        return await self._request("GET", "/api/lists")
    
    async def get_list(self, list_id: int) -> Dict[str, Any]:
        """Get mailing list by ID."""
        return await self._request("GET", f"/api/lists/{list_id}")
    
    async def create_list(
        self,
        name: str,
        type: str = "public",
        optin: str = "single",
        tags: Optional[List[str]] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new mailing list."""
        data = {
            "name": name,
            "type": type,
            "optin": optin,
            "tags": tags or [],
        }
        if description:
            data["description"] = description
            
        return await self._request("POST", "/api/lists", json_data=data)
    
    async def update_list(
        self,
        list_id: int,
        name: Optional[str] = None,
        type: Optional[str] = None,
        optin: Optional[str] = None,
        tags: Optional[List[str]] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update an existing mailing list."""
        data = {}
        if name is not None:
            data["name"] = name
        if type is not None:
            data["type"] = type
        if optin is not None:
            data["optin"] = optin
        if tags is not None:
            data["tags"] = tags
        if description is not None:
            data["description"] = description
            
        return await self._request("PUT", f"/api/lists/{list_id}", json_data=data)
    
    async def delete_list(self, list_id: int) -> Dict[str, Any]:
        """Delete a mailing list."""
        return await self._request("DELETE", f"/api/lists/{list_id}")
    
    async def get_list_subscribers(self, list_id: int, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Get subscribers for a specific list."""
        params = {"page": page, "per_page": per_page}
        return await self._request("GET", f"/api/lists/{list_id}/subscribers", params=params)
    
    # Campaign Operations
    async def get_campaigns(
        self, 
        page: int = 1, 
        per_page: int = 20,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get campaigns with pagination and filtering."""
        params = {"page": page, "per_page": per_page}
        if status:
            params["status"] = status
            
        return await self._request("GET", "/api/campaigns", params=params)
    
    async def get_campaign(self, campaign_id: int) -> Dict[str, Any]:
        """Get campaign by ID."""
        return await self._request("GET", f"/api/campaigns/{campaign_id}")
    
    async def create_campaign(
        self,
        name: str,
        subject: str,
        lists: List[int],
        type: str = "regular",
        content_type: str = "richtext",
        body: Optional[str] = None,
        template_id: Optional[int] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Create a new campaign."""
        data = {
            "name": name,
            "subject": subject,
            "lists": lists,
            "type": type,
            "content_type": content_type,
            "tags": tags or []
        }
        
        if body:
            data["body"] = body
        if template_id:
            data["template_id"] = template_id
            
        return await self._request("POST", "/api/campaigns", json_data=data)
    
    async def update_campaign(
        self,
        campaign_id: int,
        name: Optional[str] = None,
        subject: Optional[str] = None,
        lists: Optional[List[int]] = None,
        body: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Update an existing campaign."""
        data = {}
        if name is not None:
            data["name"] = name
        if subject is not None:
            data["subject"] = subject
        if lists is not None:
            data["lists"] = lists
        if body is not None:
            data["body"] = body
        if tags is not None:
            data["tags"] = tags
            
        return await self._request("PUT", f"/api/campaigns/{campaign_id}", json_data=data)
    
    async def send_campaign(self, campaign_id: int) -> Dict[str, Any]:
        """Send a campaign immediately."""
        return await self._request("PUT", f"/api/campaigns/{campaign_id}/status", json_data={"status": "running"})
    
    async def schedule_campaign(self, campaign_id: int, send_at: str) -> Dict[str, Any]:
        """Schedule a campaign for future delivery."""
        data = {"status": "scheduled", "send_at": send_at}
        return await self._request("PUT", f"/api/campaigns/{campaign_id}/status", json_data=data)
    
    async def get_campaign_preview(self, campaign_id: int) -> Dict[str, Any]:
        """Get campaign HTML preview."""
        return await self._request("GET", f"/api/campaigns/{campaign_id}/preview")
    
    # Template Operations
    async def get_templates(self) -> Dict[str, Any]:
        """Get all email templates."""
        return await self._request("GET", "/api/templates")
    
    async def get_template(self, template_id: int) -> Dict[str, Any]:
        """Get template by ID."""
        return await self._request("GET", f"/api/templates/{template_id}")
    
    async def create_template(
        self,
        name: str,
        body: str,
        type: str = "campaign",
        is_default: bool = False
    ) -> Dict[str, Any]:
        """Create a new email template."""
        data = {
            "name": name,
            "body": body,
            "type": type,
            "is_default": is_default
        }
        return await self._request("POST", "/api/templates", json_data=data)
    
    async def update_template(
        self,
        template_id: int,
        name: Optional[str] = None,
        body: Optional[str] = None,
        is_default: Optional[bool] = None
    ) -> Dict[str, Any]:
        """Update an existing template."""
        data = {}
        if name is not None:
            data["name"] = name
        if body is not None:
            data["body"] = body
        if is_default is not None:
            data["is_default"] = is_default
            
        return await self._request("PUT", f"/api/templates/{template_id}", json_data=data)
    
    async def delete_template(self, template_id: int) -> Dict[str, Any]:
        """Delete a template."""
        return await self._request("DELETE", f"/api/templates/{template_id}")
    
    # Transactional Email
    async def send_transactional_email(
        self,
        subscriber_email: str,
        template_id: int,
        data: Optional[Dict[str, Any]] = None,
        content_type: str = "html"
    ) -> Dict[str, Any]:
        """Send a transactional email."""
        payload = {
            "subscriber_email": subscriber_email,
            "template_id": template_id,
            "data": data or {},
            "content_type": content_type
        }
        return await self._request("POST", "/api/tx", json_data=payload)


async def create_client(config: Config) -> ListmonkClient:
    """Create and connect a Listmonk client."""
    listmonk_config = config.get_listmonk_config()
    client = ListmonkClient(listmonk_config)
    await client.connect()
    return client