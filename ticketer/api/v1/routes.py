"""API v1 routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ticketer.db.session import get_db
from ticketer.api.v1 import deps
from ticketer.schemas import (
    UserCreate,
    UserLogin,
    UserResponse,
    Token,
    VenueCreate,
    VenueResponse,
    EventCreate,
    EventResponse,
    EventUpdate,
    OrderCreate,
    OrderResponse,
    OrderConfirm,
    SeatCreate,
    SeatResponse,
)
from ticketer.services.auth_service import AuthService
from ticketer.services.event_service import EventService
from ticketer.services.order_service import OrderService
from ticketer.repositories.seat_repository import SQLAlchemySeatRepository
from ticketer.repositories.venue_repository import SQLAlchemyVenueRepository
from ticketer.repositories.event_repository import SQLAlchemyEventRepository
from ticketer.repositories.order_repository import SQLAlchemyOrderRepository

router = APIRouter()


# ============================================================================
# User / Auth Routes
# ============================================================================


@router.post("/users/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(
    user_data: UserCreate,
    auth_service: AuthService = Depends(deps.get_auth_service),
):
    """Register a new user."""
    try:
        user = auth_service.register_user(user_data.email, user_data.password)
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/users/login", response_model=Token)
def login_user(
    user_data: UserLogin,
    auth_service: AuthService = Depends(deps.get_auth_service),
):
    """Login a user."""
    user = auth_service.authenticate_user(user_data.email, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    access_token = auth_service.create_access_token(user.id)
    return Token(access_token=access_token, token_type="bearer")


# ============================================================================
# Venue Routes
# ============================================================================


@router.post("/venues/", response_model=VenueResponse, status_code=status.HTTP_201_CREATED)
def create_venue(
    venue_data: VenueCreate,
    venue_repo: SQLAlchemyVenueRepository = Depends(deps.get_venue_repository),
):
    """Create a new venue."""
    venue = venue_repo.create(name=venue_data.name, address=venue_data.address)
    return venue


@router.get("/venues/", response_model=list[VenueResponse])
def list_venues(
    venue_repo: SQLAlchemyVenueRepository = Depends(deps.get_venue_repository),
):
    """List all venues."""
    return venue_repo.list_all()


@router.get("/venues/{venue_id}", response_model=VenueResponse)
def get_venue(
    venue_id: int,
    venue_repo: SQLAlchemyVenueRepository = Depends(deps.get_venue_repository),
):
    """Get a venue by ID."""
    venue = venue_repo.get_by_id(venue_id)
    if not venue:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Venue not found")
    return venue


# ============================================================================
# Event Routes
# ============================================================================


@router.post("/events/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(
    event_data: EventCreate,
    event_service: EventService = Depends(deps.get_event_service),
):
    """Create a new event."""
    try:
        event = event_service.create_event(
            venue_id=event_data.venue_id,
            name=event_data.name,
            start_at=event_data.start_at,
            capacity=event_data.capacity,
        )
        return event
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/events/", response_model=list[EventResponse])
def list_events(
    sales_open_only: bool = False,
    event_repo: SQLAlchemyEventRepository = Depends(deps.get_event_repository),
):
    """List all events."""
    return event_repo.list_all(sales_open_only=sales_open_only)


@router.get("/events/{event_id}", response_model=EventResponse)
def get_event(
    event_id: int,
    event_repo: SQLAlchemyEventRepository = Depends(deps.get_event_repository),
):
    """Get an event by ID."""
    event = event_repo.get_by_id(event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return event


@router.patch("/events/{event_id}", response_model=EventResponse)
def update_event(
    event_id: int,
    event_data: EventUpdate,
    event_repo: SQLAlchemyEventRepository = Depends(deps.get_event_repository),
):
    """Update an event (admin only in real app)."""
    event = event_repo.get_by_id(event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    if event_data.sales_open is not None:
        event_repo.update_sales_status(event_id, event_data.sales_open)

    return event_repo.get_by_id(event_id)


# ============================================================================
# Seat Routes
# ============================================================================


@router.post("/seats/", response_model=SeatResponse, status_code=status.HTTP_201_CREATED)
def create_seat(
    seat_data: SeatCreate,
    seat_repo: SQLAlchemySeatRepository = Depends(deps.get_seat_repository),
):
    """Create a new seat."""
    seat = seat_repo.create(
        event_id=seat_data.event_id,
        seat_label=seat_data.seat_label,
        row=seat_data.row,
        col=seat_data.col,
    )
    return seat


@router.get("/events/{event_id}/seats", response_model=list[SeatResponse])
def get_available_seats(
    event_id: int,
    seat_repo: SQLAlchemySeatRepository = Depends(deps.get_seat_repository),
):
    """Get available seats for an event."""
    return seat_repo.get_available_seats(event_id)


# ============================================================================
# Order Routes
# ============================================================================


@router.post("/orders/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    order_data: OrderCreate,
    order_service: OrderService = Depends(deps.get_order_service),
):
    """Create a new order with temporary hold."""
    try:
        # Convert Pydantic models to dicts
        items = [item.model_dump() for item in order_data.items]
        order = order_service.create_order_with_hold(user_id=order_data.user_id, items=items)
        return order
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    order_repo: SQLAlchemyOrderRepository = Depends(deps.get_order_repository),
):
    """Get an order by ID."""
    order = order_repo.get_by_id(order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order


@router.post("/orders/{order_id}/confirm", response_model=OrderResponse)
def confirm_order(
    order_id: int,
    confirm_data: OrderConfirm,
    order_service: OrderService = Depends(deps.get_order_service),
    db: Session = Depends(get_db),
):
    """Confirm an order by processing payment."""
    try:
        order = order_service.confirm_order(
            order_id=order_id, payment_token=confirm_data.payment_token, db_session=db
        )
        return order
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/orders/{order_id}/cancel", response_model=OrderResponse)
def cancel_order(
    order_id: int,
    order_service: OrderService = Depends(deps.get_order_service),
):
    """Cancel an order."""
    try:
        order = order_service.cancel_order(order_id)
        return order
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
