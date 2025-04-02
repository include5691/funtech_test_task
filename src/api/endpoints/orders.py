import uuid
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status, HTTPException
from src.db.models.order import Order
from src.schemas.order import OrderBase, OrderRead, OrderUpdate
from src.schemas.user import UserRead
from src.api.deps import get_session, get_current_user
from src.kafka.producer import send_new_order_message

order_router = APIRouter()

@order_router.post("/", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
def create_order(
    order_in: OrderBase,
    session: Session = Depends(get_session),
    current_user: UserRead = Depends(get_current_user)
):
    "Create a new order"
    order = Order(**order_in.model_dump(), user_id = current_user.id)
    session.add(order)
    session.commit()
    session.refresh(order)
    send_new_order_message(OrderRead.from_orm(order))
    return order

@order_router.get("/{order_id}/", response_model=OrderRead)
def get_order(
    order_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: UserRead = Depends(get_current_user)
):
    "Get order by id"
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

@order_router.patch("/{order_id}/", response_model=OrderRead)
def update_order_status(
    order_id: uuid.UUID,
    order_update: OrderUpdate,
    session: Session = Depends(get_session),
    current_user: UserRead = Depends(get_current_user)
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
    return order

@order_router.get("/user/{user_id}", response_model=list[OrderRead])
def get_user_orders(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: UserRead = Depends(get_current_user)
):
    "Get all orders for a user"
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's orders",
        )
    orders = session.query(Order).filter_by(user_id=user_id).all()
    return orders