from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
    extend_schema,
)
# Shared error shape from users app
from users.schemas import APIErrorSerializer  # noqa

from .serializers import OrderCreateSerializer, OrderReadSerializer, OrderUpdateSerializer

# ------------------------------------------------------------------------------
# Tags
# ------------------------------------------------------------------------------

TAGS_ORDERS = ["Orders"]

# ------------------------------------------------------------------------------
# Examples
# ------------------------------------------------------------------------------

ORDER_ITEM_WRITE_EXAMPLE = {
    "product": "3f4c9b4c-4a8e-4c6d-9b8a-8e9a3a6a2f10",
    "quantity": 2,
}

ORDER_CREATE_EXAMPLE_REQ = OpenApiExample(
    name="Order Create (request)",
    value={
        "items": [
            ORDER_ITEM_WRITE_EXAMPLE,
            {"product": "f9e2a7d4-0d2a-4f21-bc7c-8f6a3b2e1c90", "quantity": 1},
        ]
    },
    request_only=True,
)

ORDER_CREATE_EXAMPLE_RES = OpenApiExample(
    name="Order Create (response)",
    value={
        "id": "0a4f7d1b-0d3c-4e6e-9b8a-1f2e3d4c5b6a",
        "customer_id": "8b0d0d2c-2f31-4c23-9e5c-7a1e2d3c4b5a",
        "total_price": "349.97",
        "created_at": "2025-10-16T10:12:33.120Z",
        "updated_at": "2025-10-16T10:12:33.120Z",
        "items": [
            {
                "id": "a1a1a1a1-1111-2222-3333-444444444444",
                "product_id": "3f4c9b4c-4a8e-4c6d-9b8a-8e9a3a6a2f10",
                "product_name": "Pro Tripod",
                "quantity": 2,
                "unit_price": "99.99",
                "line_total": "199.98",
            },
            {
                "id": "b2b2b2b2-5555-6666-7777-888888888888",
                "product_id": "f9e2a7d4-0d2a-4f21-bc7c-8f6a3b2e1c90",
                "product_name": "Telephoto Lens",
                "quantity": 1,
                "unit_price": "149.99",
                "line_total": "149.99",
            },
        ],
    },
    response_only=True,
)

ORDER_UPDATE_EXAMPLE_REQ = OpenApiExample(
    name="Order Update/Partial Update (request)",
    value={
        "items": [
            {"product": "3f4c9b4c-4a8e-4c6d-9b8a-8e9a3a6a2f10", "quantity": 3},
            {"product": "f9e2a7d4-0d2a-4f21-bc7c-8f6a3b2e1c90", "quantity": 0},
            {"product": "1f7b3b9d-7a1c-4f03-8f0e-1ce8d64a6b77", "quantity": 1},
        ]
    },
    request_only=True,
)

ORDER_UPDATE_EXAMPLE_RES = OpenApiExample(
    name="Order Update/Partial Update (response)",
    value={
        "id": "0a4f7d1b-0d3c-4e6e-9b8a-1f2e3d4c5b6a",
        "customer_id": "8b0d0d2c-2f31-4c23-9e5c-7a1e2d3c4b5a",
        "total_price": "399.96",
        "created_at": "2025-10-16T10:12:33.120Z",
        "updated_at": "2025-10-16T10:20:41.902Z",
        "items": [
            {
                "id": "a1a1a1a1-1111-2222-3333-444444444444",
                "product_id": "3f4c9b4c-4a8e-4c6d-9b8a-8e9a3a6a2f10",
                "product_name": "Pro Tripod",
                "quantity": 3,
                "unit_price": "99.99",
                "line_total": "299.97",
            },
            {
                "id": "c3c3c3c3-aaaa-bbbb-cccc-dddddddddddd",
                "product_id": "1f7b3b9d-7a1c-4f03-8f0e-1ce8d64a6b77",
                "product_name": "Camera Strap",
                "quantity": 1,
                "unit_price": "99.99",
                "line_total": "99.99",
            },
        ],
    },
    response_only=True,
)

ORDER_LIST_EXAMPLE_RES = OpenApiExample(
    name="Orders List (response)",
    value={
        "count": 2,
        "next": None,
        "previous": None,
        "results": [
            ORDER_CREATE_EXAMPLE_RES.value,
            {
                "id": "11111111-2222-3333-4444-555555555555",
                "customer_id": "8b0d0d2c-2f31-4c23-9e5c-7a1e2d3c4b5a",
                "total_price": "149.99",
                "created_at": "2025-10-15T08:01:11.503Z",
                "updated_at": "2025-10-15T08:01:11.503Z",
                "items": [
                    {
                        "id": "9d9d9d9d-eeee-ffff-9999-aaaaaaaaaaaa",
                        "product_id": "f9e2a7d4-0d2a-4f21-bc7c-8f6a3b2e1c90",
                        "product_name": "Telephoto Lens",
                        "quantity": 1,
                        "unit_price": "149.99",
                        "line_total": "149.99",
                    }
                ],
            },
        ],
    },
    response_only=True,
)

ORDER_RETRIEVE_EXAMPLE_RES = OpenApiExample(
    name="Order Retrieve (response)",
    value=ORDER_CREATE_EXAMPLE_RES.value,
    response_only=True,
)

ORDER_DELETE_NOTE = OpenApiExample(
    name="Order Delete (note)",
    description="On success server returns HTTP 204 with no body.",
    value=None,
    response_only=True,
)

# ------------------------------------------------------------------------------
# Query parameters (filters & ordering)
# ------------------------------------------------------------------------------

ORDER_FILTER_PARAMETERS = [
    OpenApiParameter(
        name="created_from",
        type=OpenApiTypes.DATETIME,
        location=OpenApiParameter.QUERY,
        description="Filter orders created at or after this datetime (UTC ISO-8601).",
        required=False,
    ),
    OpenApiParameter(
        name="created_to",
        type=OpenApiTypes.DATETIME,
        location=OpenApiParameter.QUERY,
        description="Filter orders created at or before this datetime (UTC ISO-8601).",
        required=False,
    ),
    OpenApiParameter(
        name="edited_from",
        type=OpenApiTypes.DATETIME,
        location=OpenApiParameter.QUERY,
        description="Filter orders updated at or after this datetime (UTC ISO-8601).",
        required=False,
    ),
    OpenApiParameter(
        name="edited_to",
        type=OpenApiTypes.DATETIME,
        location=OpenApiParameter.QUERY,
        description="Filter orders updated at or before this datetime (UTC ISO-8601).",
        required=False,
    ),
    OpenApiParameter(
        name="min_total",
        type=OpenApiTypes.NUMBER,
        location=OpenApiParameter.QUERY,
        description="Filter by minimum total price.",
        required=False,
    ),
    OpenApiParameter(
        name="max_total",
        type=OpenApiTypes.NUMBER,
        location=OpenApiParameter.QUERY,
        description="Filter by maximum total price.",
        required=False,
    ),
    OpenApiParameter(
        name="ordering",
        type=OpenApiTypes.STR,
        location=OpenApiParameter.QUERY,
        description=(
            "Order by one or more fields. "
            "Allowed: created_at, updated_at, total_price. "
            "Prefix with '-' for descending. Example: '-created_at,total_price'"
        ),
        required=False,
    ),
]

# ------------------------------------------------------------------------------
# Endpoint schemas (method decorators)
# ------------------------------------------------------------------------------

list_schema = extend_schema(
    tags=TAGS_ORDERS,
    operation_id="orders_list",
    summary="List orders (scoped by RBAC)",
    description=(
        "List orders with filtering and ordering. "
        "Non-admin users only see their own orders; users with the "
        "`orders.view_all_orders` permission see all."
    ),
    parameters=ORDER_FILTER_PARAMETERS,
    responses={
        200: OpenApiResponse(
            response=OrderReadSerializer(many=True),
            description="Paginated list of orders.",
            examples=[ORDER_LIST_EXAMPLE_RES],
        ),
        401: APIErrorSerializer,
        403: APIErrorSerializer,
    },
)

retrieve_schema = extend_schema(
    tags=TAGS_ORDERS,
    operation_id="orders_retrieve",
    summary="Retrieve order",
    description=(
        "Retrieve a single order. "
        "Object-level permissions: owners can view their own; admins or "
        "holders of `orders.view_all_orders` can view any."
    ),
    responses={
        200: OpenApiResponse(
            response=OrderReadSerializer,
            examples=[ORDER_RETRIEVE_EXAMPLE_RES],
        ),
        401: APIErrorSerializer,
        403: APIErrorSerializer,
        404: APIErrorSerializer,
    },
)

create_schema = extend_schema(
    tags=TAGS_ORDERS,
    operation_id="orders_create",
    summary="Create order",
    description=(
        "Create an order for the authenticated user. "
        "Each item stores a unit price snapshot at creation time. "
        "Use product UUIDs and integer quantities (≥ 0)."
    ),
    request=OrderCreateSerializer,
    responses={
        201: OpenApiResponse(
            response=OrderReadSerializer,
            description="Order created successfully.",
            examples=[ORDER_CREATE_EXAMPLE_RES],
        ),
        400: APIErrorSerializer,
        401: APIErrorSerializer,
        403: APIErrorSerializer,
    },
    examples=[ORDER_CREATE_EXAMPLE_REQ],
)

update_schema = extend_schema(
    tags=TAGS_ORDERS,
    operation_id="orders_update",
    summary="Replace items in order",
    description=(
        "Update an order by replacing its desired items state. "
        "Upsert semantics per line: `quantity > 0` sets/creates; `0` removes. "
        "Object-level RBAC: owner or users with `orders.edit_any_order`."
    ),
    request=OrderUpdateSerializer,
    responses={
        200: OpenApiResponse(
            response=OrderReadSerializer,
            description="Order updated successfully.",
            examples=[ORDER_UPDATE_EXAMPLE_RES],
        ),
        400: APIErrorSerializer,
        401: APIErrorSerializer,
        403: APIErrorSerializer,
        404: APIErrorSerializer,
    },
    examples=[ORDER_UPDATE_EXAMPLE_REQ],
)

partial_update_schema = extend_schema(
    tags=TAGS_ORDERS,
    operation_id="orders_partial_update",
    summary="Partially update items (same contract as update)",
    description=(
        "Same request contract as `update` (send the full new desired items set). "
        "The server applies upsert semantics per item. "
        "RBAC identical to `update`."
    ),
    request=OrderUpdateSerializer,
    responses={
        200: OpenApiResponse(
            response=OrderReadSerializer,
            examples=[ORDER_UPDATE_EXAMPLE_RES],
        ),
        400: APIErrorSerializer,
        401: APIErrorSerializer,
        403: APIErrorSerializer,
        404: APIErrorSerializer,
    },
    examples=[ORDER_UPDATE_EXAMPLE_REQ],
)

destroy_schema = extend_schema(
    tags=TAGS_ORDERS,
    operation_id="orders_destroy",
    summary="Delete order",
    description=(
        "Delete an order. "
        "Object-level RBAC: owner or users with `orders.delete_any_order`."
    ),
    responses={
        204: None,
        401: APIErrorSerializer,
        403: APIErrorSerializer,
        404: APIErrorSerializer,
    },
    examples=[ORDER_DELETE_NOTE],
)
