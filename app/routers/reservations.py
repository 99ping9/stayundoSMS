from fastapi import APIRouter, HTTPException, Depends
from app.database import get_supabase
from app.models import ReservationCreate, Reservation
from supabase import Client

router = APIRouter(prefix="/reservations", tags=["v3_reservations"])

@router.get("/", response_model=list[dict])
async def get_reservations(supabase: Client = Depends(get_supabase)):
    response = supabase.table("v3_reservations").select("*").order("checkin_date", desc=False).execute()
    return response.data

from fastapi.encoders import jsonable_encoder

@router.post("/", response_model=dict)
async def create_reservation(reservation: ReservationCreate, supabase: Client = Depends(get_supabase)):
    data = jsonable_encoder(reservation)
    
    # Validation: Check for Overlapping Reservations
    # Same accommodation
    # Overlap: (existing.checkin < new.checkout) AND (existing.checkout > new.checkin)
    
    existing = supabase.table("v3_reservations").select("*") \
        .eq("accommodation_name", reservation.accommodation_name) \
        .lt("checkin_date", reservation.checkout_date) \
        .gt("checkout_date", reservation.checkin_date) \
        .execute()

    if existing.data:
        raise HTTPException(status_code=400, detail="이미 예약된 날짜입니다.")

    response = supabase.table("v3_reservations").insert(data).execute()
    if not response.data:
        raise HTTPException(status_code=400, detail="Failed to create reservation")
    return response.data[0]

from app.models import ReservationCreate, ReservationUpdate, Reservation

@router.delete("/{reservation_id}")
async def delete_reservation(reservation_id: int, supabase: Client = Depends(get_supabase)):
    response = supabase.table("v3_reservations").delete().eq("id", reservation_id).execute()
    return {"message": "Reservation deleted"}

@router.put("/{reservation_id}", response_model=dict)
async def update_reservation(reservation_id: int, reservation: ReservationUpdate, supabase: Client = Depends(get_supabase)):
    data = jsonable_encoder(reservation)
    
    # Validation: Check for Overlapping Reservations (excluding current one)
    existing = supabase.table("v3_reservations").select("*") \
        .eq("accommodation_name", reservation.accommodation_name) \
        .neq("id", reservation_id) \
        .lt("checkin_date", reservation.checkout_date) \
        .gt("checkout_date", reservation.checkin_date) \
        .execute()

    if existing.data:
         raise HTTPException(status_code=400, detail="이미 예약된 날짜입니다.")

    response = supabase.table("v3_reservations").update(data).eq("id", reservation_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return response.data[0]
