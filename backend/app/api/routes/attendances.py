from fastapi import APIRouter, Depends, HTTPException

from app.application.services.attendance_service import AttendanceService, get_attendance_service
from app.schemas.attendance import AttendanceDetailResponse, AttendanceListResponse

router = APIRouter()


@router.get("/attendances", response_model=AttendanceListResponse)
def list_attendances(
    service: AttendanceService = Depends(get_attendance_service),
) -> AttendanceListResponse:
    return service.list()


@router.get("/attendances/{attendance_id}", response_model=AttendanceDetailResponse)
def get_attendance(
    attendance_id: str,
    service: AttendanceService = Depends(get_attendance_service),
) -> AttendanceDetailResponse:
    attendance = service.get(attendance_id)
    if attendance is None:
        raise HTTPException(status_code=404, detail="Atendimento não encontrado.")
    return attendance
