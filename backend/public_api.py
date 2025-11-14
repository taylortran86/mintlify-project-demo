"""
Public API endpoints for customer-facing documentation.
These endpoints represent what would be documented for external API consumers.
"""
from fastapi import APIRouter, HTTPException, Header, status
from typing import Optional, List
from datetime import datetime, timedelta
import uuid
import secrets

from .api_schemas import (
    ApiKeyCreate,
    ApiKeyResponse,
    ApiKeyListResponse,
    ApiKeyUpdate,
    WebhookCreate,
    WebhookUpdate,
    WebhookResponse,
    WebhookListResponse,
    AnalyticsResponse,
    UsageStats,
    AccountInfo,
    SuccessResponse,
    ApiKeyScope,
    WebhookEvent,
)

router = APIRouter(prefix="/v1")

# In-memory storage for demo purposes (would be a database in production)
api_keys_db = {}
webhooks_db = {}


# Helper function to verify API key (demo implementation)
def verify_api_key(authorization: Optional[str] = Header(None)) -> dict:
    """
    Verify the API key from Authorization header.

    Args:
        authorization: Authorization header containing the API key

    Returns:
        dict: API key information

    Raises:
        HTTPException: 401 if API key is invalid or missing
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key. Include 'Authorization: Bearer YOUR_API_KEY' header."
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization format. Use 'Bearer YOUR_API_KEY'."
        )

    # In a real implementation, you would verify against database
    return {"account_id": "demo_account", "scopes": [ApiKeyScope.ADMIN]}


# API Key Management Endpoints
@router.post("/api-keys", response_model=ApiKeyResponse, status_code=status.HTTP_201_CREATED, tags=["API Keys"])
def create_api_key(key_data: ApiKeyCreate) -> ApiKeyResponse:
    """
    Create a new API key for authentication.

    API keys are used to authenticate requests to the API. Each key can have specific
    scopes that control what operations it can perform.

    **Important**: The full API key is only returned once upon creation. Store it securely.

    Args:
        key_data: API key configuration including name, scopes, and expiration

    Returns:
        ApiKeyResponse: The created API key with full key value (only shown once)

    Example:
        ```json
        {
          "name": "Production API Key",
          "scopes": ["read", "write"],
          "expires_at": "2025-12-31T23:59:59Z"
        }
        ```
    """
    # Generate a secure API key
    key_id = str(uuid.uuid4())
    api_key = f"sk_{secrets.token_urlsafe(32)}"
    key_prefix = api_key[:8]

    key_response = ApiKeyResponse(
        id=key_id,
        name=key_data.name,
        key=api_key,  # Only returned on creation
        key_prefix=key_prefix,
        scopes=key_data.scopes,
        created_at=datetime.utcnow(),
        expires_at=key_data.expires_at,
        last_used_at=None,
        is_active=True
    )

    # Store in demo database (without the full key for security)
    api_keys_db[key_id] = {
        **key_response.model_dump(),
        "key": None  # Don't store full key in real implementation
    }

    return key_response


@router.get("/api-keys", response_model=ApiKeyListResponse, tags=["API Keys"])
def list_api_keys() -> ApiKeyListResponse:
    """
    List all API keys for your account.

    Returns a list of all API keys associated with your account. The full key values
    are never returned - only the key prefix for identification.

    Returns:
        ApiKeyListResponse: List of API keys with metadata
    """
    keys = [
        ApiKeyResponse(**{**data, "key": None})
        for data in api_keys_db.values()
    ]

    return ApiKeyListResponse(keys=keys, total=len(keys))


@router.get("/api-keys/{key_id}", response_model=ApiKeyResponse, tags=["API Keys"])
def get_api_key(key_id: str) -> ApiKeyResponse:
    """
    Get details of a specific API key.

    Retrieve information about a specific API key including its scopes, expiration,
    and last usage time.

    Args:
        key_id: The unique identifier of the API key

    Returns:
        ApiKeyResponse: API key details

    Raises:
        HTTPException: 404 if API key not found
    """
    if key_id not in api_keys_db:
        raise HTTPException(status_code=404, detail="API key not found")

    return ApiKeyResponse(**api_keys_db[key_id])


@router.delete("/api-keys/{key_id}", response_model=SuccessResponse, tags=["API Keys"])
def revoke_api_key(key_id: str) -> SuccessResponse:
    """
    Revoke an API key.

    Permanently revokes an API key. This action cannot be undone. Any requests
    using this key will be rejected immediately.

    Args:
        key_id: The unique identifier of the API key to revoke

    Returns:
        SuccessResponse: Confirmation of revocation

    Raises:
        HTTPException: 404 if API key not found
    """
    if key_id not in api_keys_db:
        raise HTTPException(status_code=404, detail="API key not found")

    del api_keys_db[key_id]
    return SuccessResponse(success=True, message=f"API key {key_id} has been revoked")


@router.patch("/api-keys/{key_id}", response_model=ApiKeyResponse, tags=["API Keys"])
def update_api_key(key_id: str, key_update: ApiKeyUpdate) -> ApiKeyResponse:
    """
    Update an API key's properties.

    Allows you to modify certain properties of an existing API key, such as its name.
    Note that the actual key value and scopes cannot be changed after creation.

    Args:
        key_id: The unique identifier of the API key to update
        key_update: The fields to update

    Returns:
        ApiKeyResponse: The updated API key information

    Raises:
        HTTPException: 404 if API key not found
    """
    if key_id not in api_keys_db:
        raise HTTPException(status_code=404, detail="API key not found")

    api_key = api_keys_db[key_id]
    update_data = key_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        api_key[field] = value

    return ApiKeyResponse(**api_key)


# Webhook Management Endpoints
@router.post("/webhooks", response_model=WebhookResponse, status_code=status.HTTP_201_CREATED, tags=["Webhooks"])
def create_webhook(webhook_data: WebhookCreate) -> WebhookResponse:
    """
    Create a new webhook subscription.

    Webhooks allow you to receive real-time notifications when events occur in your account.
    When a subscribed event occurs, we'll send a POST request to your specified URL.

    **Webhook Payload Format:**
    ```json
    {
      "event": "task.created",
      "timestamp": "2025-11-13T10:30:00Z",
      "data": { ... event-specific data ... }
    }
    ```

    Args:
        webhook_data: Webhook configuration including URL and event subscriptions

    Returns:
        WebhookResponse: The created webhook configuration

    Example:
        ```json
        {
          "url": "https://example.com/webhooks/calendar",
          "events": ["task.created", "task.completed"],
          "description": "Notify task management system"
        }
        ```
    """
    webhook_id = str(uuid.uuid4())

    webhook = WebhookResponse(
        id=webhook_id,
        url=str(webhook_data.url),
        events=webhook_data.events,
        description=webhook_data.description,
        is_active=webhook_data.is_active,
        created_at=datetime.utcnow(),
        last_triggered_at=None
    )

    webhooks_db[webhook_id] = webhook.model_dump()
    return webhook


@router.get("/webhooks", response_model=WebhookListResponse, tags=["Webhooks"])
def list_webhooks() -> WebhookListResponse:
    """
    List all webhooks for your account.

    Returns a list of all webhook subscriptions configured for your account.

    Returns:
        WebhookListResponse: List of webhook configurations
    """
    webhooks = [WebhookResponse(**data) for data in webhooks_db.values()]
    return WebhookListResponse(webhooks=webhooks, total=len(webhooks))


@router.get("/webhooks/{webhook_id}", response_model=WebhookResponse, tags=["Webhooks"])
def get_webhook(webhook_id: str) -> WebhookResponse:
    """
    Get details of a specific webhook.

    Retrieve configuration and status information for a specific webhook subscription.

    Args:
        webhook_id: The unique identifier of the webhook

    Returns:
        WebhookResponse: Webhook configuration details

    Raises:
        HTTPException: 404 if webhook not found
    """
    if webhook_id not in webhooks_db:
        raise HTTPException(status_code=404, detail="Webhook not found")

    return WebhookResponse(**webhooks_db[webhook_id])


@router.patch("/webhooks/{webhook_id}", response_model=WebhookResponse, tags=["Webhooks"])
def update_webhook(webhook_id: str, webhook_update: WebhookUpdate) -> WebhookResponse:
    """
    Update a webhook configuration.

    Modify the URL, events, or active status of an existing webhook subscription.

    Args:
        webhook_id: The unique identifier of the webhook
        webhook_update: Fields to update

    Returns:
        WebhookResponse: Updated webhook configuration

    Raises:
        HTTPException: 404 if webhook not found
    """
    if webhook_id not in webhooks_db:
        raise HTTPException(status_code=404, detail="Webhook not found")

    webhook = webhooks_db[webhook_id]
    update_data = webhook_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        if field == "url" and value:
            webhook["url"] = str(value)
        else:
            webhook[field] = value

    return WebhookResponse(**webhook)


@router.delete("/webhooks/{webhook_id}", response_model=SuccessResponse, tags=["Webhooks"])
def delete_webhook(webhook_id: str) -> SuccessResponse:
    """
    Delete a webhook subscription.

    Permanently removes a webhook subscription. You will no longer receive
    notifications for the subscribed events.

    Args:
        webhook_id: The unique identifier of the webhook

    Returns:
        SuccessResponse: Confirmation of deletion

    Raises:
        HTTPException: 404 if webhook not found
    """
    if webhook_id not in webhooks_db:
        raise HTTPException(status_code=404, detail="Webhook not found")

    del webhooks_db[webhook_id]
    return SuccessResponse(success=True, message=f"Webhook {webhook_id} has been deleted")


# Analytics & Reporting Endpoints
@router.get("/analytics", response_model=AnalyticsResponse, tags=["Analytics"])
def get_analytics(
    period: str = "last_30_days"
) -> AnalyticsResponse:
    """
    Get usage analytics and statistics.

    Retrieve detailed analytics about your API usage, task/event activity, and
    overall account metrics.

    **Available Periods:**
    - `last_7_days` - Past week
    - `last_30_days` - Past month (default)
    - `last_90_days` - Past quarter
    - `current_month` - Current calendar month

    Args:
        period: Time period for analytics (default: "last_30_days")

    Returns:
        AnalyticsResponse: Comprehensive analytics data

    Example Response:
        ```json
        {
          "account_id": "acc_123456",
          "generated_at": "2025-11-13T10:30:00Z",
          "usage": {
            "tasks_created": 145,
            "tasks_completed": 98,
            "events_created": 67,
            "api_calls": 1523
          }
        }
        ```
    """
    # Generate demo analytics data
    usage = UsageStats(
        period=period,
        tasks_created=145,
        tasks_completed=98,
        events_created=67,
        api_calls=1523,
        active_tasks=47,
        upcoming_events=23
    )

    return AnalyticsResponse(
        account_id="demo_account",
        generated_at=datetime.utcnow(),
        usage=usage,
        top_categories=[
            {"name": "Work", "count": 67},
            {"name": "Personal", "count": 43},
            {"name": "Meetings", "count": 35}
        ]
    )


@router.get("/analytics/usage", response_model=UsageStats, tags=["Analytics"])
def get_usage_stats(period: str = "last_30_days") -> UsageStats:
    """
    Get API usage statistics.

    Retrieve specific usage metrics for tasks, events, and API calls over a given period.
    This endpoint is useful for monitoring your API quota and usage patterns.

    Args:
        period: Time period for statistics (default: "last_30_days")

    Returns:
        UsageStats: Usage statistics for the specified period
    """
    return UsageStats(
        period=period,
        tasks_created=145,
        tasks_completed=98,
        events_created=67,
        api_calls=1523,
        active_tasks=47,
        upcoming_events=23
    )


# Account Information Endpoints
@router.get("/account", response_model=AccountInfo, tags=["Account"])
def get_account_info() -> AccountInfo:
    """
    Get account information and subscription details.

    Retrieve information about your account including subscription plan,
    API quota, and usage limits.

    Returns:
        AccountInfo: Account details and subscription information
    """
    return AccountInfo(
        account_id="demo_account",
        email="demo@example.com",
        plan="Professional",
        created_at=datetime.utcnow() - timedelta(days=90),
        api_quota=100000,
        api_usage=1523
    )


# Health Check for Public API
@router.get("/health", tags=["Health"])
def public_api_health():
    """
    Health check endpoint for the public API.

    Use this endpoint to verify that the API is operational and responding to requests.

    Returns:
        dict: API health status and version information
    """
    return {
        "status": "healthy",
        "version": "v1",
        "timestamp": datetime.utcnow()
    }
