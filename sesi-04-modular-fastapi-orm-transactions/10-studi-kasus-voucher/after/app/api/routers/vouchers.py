"""API: endpoint voucher."""
from fastapi import APIRouter, Depends

from app.api.dependencies import get_voucher_service
from app.api.schemas import ErrorOut, VoucherIn, VoucherOut
from app.application.voucher_service import VoucherService

router = APIRouter(prefix="/vouchers", tags=["vouchers"])


@router.post("", status_code=201, response_model=VoucherOut, summary="Buat voucher",
             responses={409: {"model": ErrorOut, "description": "Kode voucher sudah dipakai"}})
def create_voucher(payload: VoucherIn, service: VoucherService = Depends(get_voucher_service)):
    return VoucherOut.from_domain(service.create_voucher(payload.code, payload.amount, payload.quota))


@router.get("/{code}", response_model=VoucherOut, summary="Detail voucher dan sisa kuota",
            responses={404: {"model": ErrorOut, "description": "Voucher tidak ditemukan"}})
def get_voucher(code: str, service: VoucherService = Depends(get_voucher_service)):
    return VoucherOut.from_domain(service.get_voucher(code))
