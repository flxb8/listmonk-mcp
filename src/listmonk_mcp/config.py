"""Configuration management for Listmonk MCP server using pydantic-settings."""

import os
from typing import Optional
from pathlib import Path

from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class ListmonkConfig(BaseModel):
    """Listmonk server configuration."""
    
    url: str = Field(..., description="Listmonk server URL")
    username: str = Field(..., description="Admin username")
    password: str = Field(..., description="Admin password")
    timeout: int = Field(default=30, description="Request timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    
    @field_validator('url')
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate URL format."""
        if not v.startswith(('http://', 'https://')):
            raise ValueError("URL must start with http:// or https://")
        return v.rstrip('/')
    
    @field_validator('timeout')
    @classmethod
    def validate_timeout(cls, v: int) -> int:
        """Validate timeout is positive."""
        if v <= 0:
            raise ValueError("Timeout must be positive")
        return v
    
    @field_validator('max_retries')
    @classmethod
    def validate_max_retries(cls, v: int) -> int:
        """Validate max_retries is non-negative."""
        if v < 0:
            raise ValueError("Max retries must be non-negative")
        return v


class ServerConfig(BaseModel):
    """MCP server configuration."""
    
    name: str = Field(default="Listmonk MCP Server", description="Server name")
    debug: bool = Field(default=False, description="Enable debug mode")
    log_level: str = Field(default="INFO", description="Logging level")
    
    @field_validator('log_level')
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"Log level must be one of: {valid_levels}")
        return v_upper


class Config(BaseSettings):
    """Main configuration class with automatic environment variable loading."""
    
    # Listmonk configuration
    url: str = Field(..., description="Listmonk server URL")
    username: str = Field(..., description="Admin username") 
    password: str = Field(..., description="Admin password")
    timeout: int = Field(default=30, description="Request timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    
    # Server configuration
    debug: bool = Field(default=False, description="Enable debug mode")
    log_level: str = Field(default="INFO", description="Logging level")
    server_name: str = Field(default="Listmonk MCP Server", description="Server name")
    
    model_config = SettingsConfigDict(
        env_prefix='LISTMONK_MCP_',
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore'
    )
    
    @field_validator('url')
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate URL format."""
        if not v.startswith(('http://', 'https://')):
            raise ValueError("URL must start with http:// or https://")
        return v.rstrip('/')
    
    @field_validator('timeout')
    @classmethod
    def validate_timeout(cls, v: int) -> int:
        """Validate timeout is positive."""
        if v <= 0:
            raise ValueError("Timeout must be positive")
        return v
    
    @field_validator('max_retries')
    @classmethod
    def validate_max_retries(cls, v: int) -> int:
        """Validate max_retries is non-negative."""
        if v < 0:
            raise ValueError("Max retries must be non-negative")
        return v
    
    @field_validator('log_level')
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"Log level must be one of: {valid_levels}")
        return v_upper
    
    def get_listmonk_config(self) -> ListmonkConfig:
        """Get Listmonk-specific configuration."""
        return ListmonkConfig(
            url=self.url,
            username=self.username,
            password=self.password,
            timeout=self.timeout,
            max_retries=self.max_retries
        )
    
    def get_server_config(self) -> ServerConfig:
        """Get server-specific configuration."""
        return ServerConfig(
            name=self.server_name,
            debug=self.debug,
            log_level=self.log_level
        )


# Global configuration instance
_config: Optional[Config] = None


def load_config(env_file: Optional[str] = None) -> Config:
    """Load configuration from environment variables and optional .env file."""
    global _config
    
    if env_file and Path(env_file).exists():
        _config = Config(_env_file=env_file)
    else:
        _config = Config()
    
    return _config


def get_config() -> Config:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = load_config()
    return _config


def validate_config() -> None:
    """Validate that all required configuration is present."""
    config = get_config()
    
    if not config.url:
        raise ValueError("Listmonk URL is required (set LISTMONK_MCP_URL)")
    if not config.username:
        raise ValueError("Listmonk username is required (set LISTMONK_MCP_USERNAME)")
    if not config.password:
        raise ValueError("Listmonk password is required (set LISTMONK_MCP_PASSWORD)")


def create_test_config() -> Config:
    """Create a test configuration with default values."""
    return Config(
        url="http://localhost:9000",
        username="admin", 
        password="listmonk",
        timeout=30,
        max_retries=3,
        debug=True,
        log_level="DEBUG"
    )