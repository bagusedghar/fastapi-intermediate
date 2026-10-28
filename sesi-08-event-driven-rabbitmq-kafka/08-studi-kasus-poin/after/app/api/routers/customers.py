"""API: endpoint customer.

Saldo poin dibaca dari database. Poinnya ditambahkan oleh consumer, bukan oleh API.
"""
from fastapi import APIRouter, Depends

from app.api.dependencies import get_points_service
from app.api.schemas import PointsOut
from app.application.points_service import PointsService

router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("/{customer}/points", response_model=PointsOut, summary="Saldo poin loyalty customer")
def get_points(customer: str, service: PointsService = Depends(get_points_service)):
    return PointsOut(customer=customer, points=service.balance(customer))
