from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.services import expense_service
from app.api.routes.auth import get_current_user
from app.schemas.expanse import ExpenseCreate, ExpenseUpdate

router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.get("/")
async def list_expenses(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=50, ge=1, le=200),
    category: Optional[str] = Query(default=None),
    start_date: Optional[datetime] = Query(default=None),
    end_date: Optional[datetime] = Query(default=None),
    source: Optional[str] = Query(default=None),
    current_user: dict = Depends(get_current_user),
):
    return await expense_service.get_expenses(
        user_id=current_user["id"],
        page=page,
        limit=limit,
        category=category,
        start_date=start_date,
        end_date=end_date,
        source=source,
    )


@router.get("/summary")
async def get_summary(current_user: dict = Depends(get_current_user)):
    return await expense_service.get_summary(user_id=current_user["id"])


@router.get("/{expense_id}")
async def get_expense(
    expense_id: str,
    current_user: dict = Depends(get_current_user),
):
    expense = await expense_service.get_expense_by_id(expense_id, current_user["id"])
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


@router.post("/", status_code=201)
async def create_expense(
    data: ExpenseCreate,
    current_user: dict = Depends(get_current_user),
):
    return await expense_service.create_expense(
        user_id=current_user["id"],
        data=data.dict(),
    )


@router.put("/{expense_id}")
async def update_expense(
    expense_id: str,
    data: ExpenseUpdate,
    current_user: dict = Depends(get_current_user),
):
    updated = await expense_service.update_expense(
        expense_id=expense_id,
        user_id=current_user["id"],
        data=data.dict(),
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Expense not found")
    return updated


@router.delete("/{expense_id}")
async def delete_expense(
    expense_id: str,
    current_user: dict = Depends(get_current_user),
):
    deleted = await expense_service.delete_expense(expense_id, current_user["id"])
    if not deleted:
        raise HTTPException(status_code=404, detail="Expense not found")
    return {"message": "Deleted successfully"}