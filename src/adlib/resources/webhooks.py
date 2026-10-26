from __future__ import annotations

from typing import Optional, Union, cast

from .. import _endpoints as E
from ..types import DeliveriesResponse, DeliveryResponse, DeliveryStatus, QueuedResponse, WebhookSecretResponse
from ._base import AsyncResource, SyncResource

__all__ = ["Webhooks", "AsyncWebhooks"]


class Webhooks(SyncResource):
    """Webhook deliveries, test events and the signing secret. To verify signatures see :func:`adlib.verify_webhook_signature`."""

    def deliveries(self, *, status: Optional[DeliveryStatus] = None, cursor: Optional[str] = None, limit: Optional[int] = None) -> DeliveriesResponse:
        """Your webhook deliveries, newest first, with status, attempts and the receiver's HTTP
        status. Kept 30 days. Paginated."""
        return cast(DeliveriesResponse, self._request(E.list_deliveries(status, cursor, limit)))

    def delivery(self, id: Union[int, str]) -> DeliveryResponse:
        """One delivery incl. its payload."""
        return cast(DeliveryResponse, self._request(E.get_delivery(id)))

    def redeliver(self, id: Union[int, str]) -> QueuedResponse:
        """Queues a delivery again."""
        return cast(QueuedResponse, self._request(E.redeliver(id)))

    def test(self, url: str) -> QueuedResponse:
        """Sends a signed test event (``webhook.ping``) to a URL, to verify your endpoint and
        signature check. Slack and Discord webhook URLs get a readable message instead, unsigned."""
        return cast(QueuedResponse, self._request(E.test_webhook(url)))

    def secret(self) -> WebhookSecretResponse:
        """Your webhook signing secret (``whsec_...``)."""
        return cast(WebhookSecretResponse, self._request(E.webhook_secret()))

    def rotate_secret(self) -> WebhookSecretResponse:
        """Rotates the signing secret. Deliveries from now on use the new one; the old one stops working immediately."""
        return cast(WebhookSecretResponse, self._request(E.rotate_webhook_secret()))


class AsyncWebhooks(AsyncResource):
    """Async version of :class:`Webhooks`."""

    async def deliveries(self, *, status: Optional[DeliveryStatus] = None, cursor: Optional[str] = None, limit: Optional[int] = None) -> DeliveriesResponse:
        """Your webhook deliveries, newest first, with status, attempts and the receiver's HTTP
        status. Kept 30 days. Paginated."""
        return cast(DeliveriesResponse, await self._request(E.list_deliveries(status, cursor, limit)))

    async def delivery(self, id: Union[int, str]) -> DeliveryResponse:
        """One delivery incl. its payload."""
        return cast(DeliveryResponse, await self._request(E.get_delivery(id)))

    async def redeliver(self, id: Union[int, str]) -> QueuedResponse:
        """Queues a delivery again."""
        return cast(QueuedResponse, await self._request(E.redeliver(id)))

    async def test(self, url: str) -> QueuedResponse:
        """Sends a signed test event (``webhook.ping``) to a URL, to verify your endpoint and
        signature check. Slack and Discord webhook URLs get a readable message instead, unsigned."""
        return cast(QueuedResponse, await self._request(E.test_webhook(url)))

    async def secret(self) -> WebhookSecretResponse:
        """Your webhook signing secret (``whsec_...``)."""
        return cast(WebhookSecretResponse, await self._request(E.webhook_secret()))

    async def rotate_secret(self) -> WebhookSecretResponse:
        """Rotates the signing secret. Deliveries from now on use the new one; the old one stops working immediately."""
        return cast(WebhookSecretResponse, await self._request(E.rotate_webhook_secret()))
