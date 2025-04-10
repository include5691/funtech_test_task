import uuid
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status, HTTPException, Request
from fastapi_cache.decorator import cache
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from src.db.models.order import Order
from src.schemas.order import OrderBase, OrderRead, OrderUpdate
from src.schemas.user import UserRead
from src.api.deps import get_session, get_current_user
from src.kafka.producer import send_new_order_message

order_router = APIRouter()

CACHE_EXPIRING_TIME = 300


def key_builder(
    *args, namespace="", request: Request = None, order_id: str | None = None, **kwargs
):
    "Build cache key for order-related functions in namespase:id_order format"
    order_id = order_id or request.url.path.split("/")[-2]
    return f"{namespace}:{order_id}"


@order_router.post(
    "/",
    response_model=OrderRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a New Order",
    description="Creates a new order for the currently authenticated user and publishes a 'new_order' event to Kafka.",
    responses={
        status.HTTP_201_CREATED: {"description": "Order created successfully"},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Invalid order data provided"
        },
    },
)
async def create_order(
    order_in: OrderBase,
    session: Session = Depends(get_session),
    current_user: UserRead = Depends(get_current_user),
):
    "Create a new order"
    order = Order(**order_in.model_dump(), user_id=current_user.id)
    session.add(order)
    session.commit()
    session.refresh(order)
    await send_new_order_message(OrderRead.model_validate(order))
    return order


@order_router.get(
    "/{order_id}/",
    response_model=OrderRead,
    summary="Get Order by ID",
    description=f"""Retrieves details for a specific order by its UUID.
    Checks Redis cache first (TTL: {CACHE_EXPIRING_TIME} seconds).
    Only the order owner can access it.""",
    responses={
        status.HTTP_200_OK: {"description": "Order details retrieved successfully"},
    },
)
@cache(expire=CACHE_EXPIRING_TIME, key_builder=key_builder)
async def get_order(
    order_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: UserRead = Depends(get_current_user),
):
    "Get order by it's id"
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with id {order_id} not found",
        )
    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this order",
        )
    return order


@order_router.patch(
    "/{order_id}/",
    response_model=OrderRead,
    summary="Update Order Status",
    description="""Updates the status of an existing order.
    Only the order owner can perform this action.
    Invalidates/updates the Redis cache for this order.""",
    responses={
        status.HTTP_200_OK: {"description": "Order status updated successfully"},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Invalid status value provided"
        },
    },
)
async def update_order_status(
    order_id: uuid.UUID,
    order_update: OrderUpdate,
    session: Session = Depends(get_session),
    current_user: UserRead = Depends(get_current_user),
):
    "Update order status"
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with id {order_id} not found",
        )
    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this order",
        )
    order.status = order_update.status
    session.commit()
    session.refresh(order)

    redis_backend: RedisBackend = FastAPICache.get_backend()
    cache_key = key_builder(order_id=order_id)
    order_data = OrderRead.model_validate(order).model_dump_json()
    await redis_backend.set(cache_key, order_data, expire=CACHE_EXPIRING_TIME)
    return order


@order_router.get(
    "/user/{user_id}",
    response_model=list[OrderRead],
    summary="Get All Orders for a User",
    description="Retrieves a list of all orders belonging to the specified user ID. Only the user themselves can access their orders.",
    responses={
        status.HTTP_200_OK: {
            "description": "List of user orders retrieved successfully"
        },
    },
)
async def get_user_orders(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: UserRead = Depends(get_current_user),
):
    "Get all orders for a user"
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's orders",
        )
    orders = session.query(Order).filter_by(user_id=user_id).all()
    return orders
