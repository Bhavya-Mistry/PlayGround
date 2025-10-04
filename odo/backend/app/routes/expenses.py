from typing import List
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form

from ..config import get_database, Database
from ..models.expense import ExpenseModel, ApprovalStep, ApprovalStatus
from ..schemas.expense import ExpenseCreate, ExpenseOut, ApprovalDecision
from ..models.user import UserModel
from .users import get_current_user # Re-using our security dependency

router = APIRouter(
    prefix="/expenses",
    tags=["Expenses"]
)

@router.post("/", response_model=ExpenseOut, status_code=status.HTTP_201_CREATED)
def submit_expense(
    # We use Form(...) to accept form data alongside a file upload
    expense_data: ExpenseCreate = Depends(), 
    receipt: UploadFile = File(None),
    db: Database = Depends(get_database),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Endpoint for an authenticated user to submit a new expense claim.
    """
    # Find the default approval flow for the user's company
    # For now, we assume one flow per company. A more complex app could have many.
    approval_flow = db.approval_flows.find_one({"company_id": current_user.company_id})
    if not approval_flow:
        raise HTTPException(status_code=404, detail="No approval flow configured for this company.")

    # --- Build the approval chain for this specific expense ---
    approval_steps = []
    # 1. Add employee's direct manager if the rule is set
    if approval_flow.get("is_manager_first_approver") and current_user.manager_id:
        approval_steps.append(ApprovalStep(approver_id=current_user.manager_id))

    # 2. Add the fixed approvers from the flow
    for approver_id in approval_flow.get("approvers", []):
        approval_steps.append(ApprovalStep(approver_id=approver_id))

    if not approval_steps:
        raise HTTPException(status_code=400, detail="Approval flow is empty. Cannot submit expense.")

    # TODO: Handle receipt file upload (save it and get a URL)
    receipt_url = f"uploads/{receipt.filename}" if receipt else None
    
    new_expense = ExpenseModel(
        **expense_data.model_dump(),
        employee_id=current_user.id,
        company_id=current_user.company_id,
        approval_steps=approval_steps,
        receipt_image_url=receipt_url
    )
    
    created_expense = db.expenses.insert_one(new_expense.model_dump(by_alias=True))
    expense_doc = db.expenses.find_one({"_id": created_expense.inserted_id})
    return expense_doc

@router.get("/my-expenses", response_model=List[ExpenseOut])
def get_my_expenses(
    db: Database = Depends(get_database),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Returns a list of all expenses submitted by the current user.
    """
    expenses = db.expenses.find({"employee_id": current_user.id}).sort("created_at", -1)
    return list(expenses)

@router.get("/approvals", response_model=List[ExpenseOut])
def get_expenses_for_approval(
    db: Database = Depends(get_database),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Returns a list of expenses waiting for the current user's approval.
    """
    # Find expenses where it's the current user's turn to approve.
    # This query finds expenses where the first "Pending" step belongs to the current user.
    pipeline = [
        {"$match": {"status": ApprovalStatus.PENDING, "approval_steps.approver_id": current_user.id}},
        {"$addFields": {
            "current_step": {
                "$arrayElemAt": [
                    {"$filter": {"input": "$approval_steps", "as": "step", "cond": {"$eq": ["$$step.status", "Pending"]}}},
                    0
                ]}
        }},
        {"$match": {"current_step.approver_id": current_user.id}}
    ]
    expenses = db.expenses.aggregate(pipeline)
    return list(expenses)

@router.post("/{expense_id}/decision", response_model=ExpenseOut)
def make_approval_decision(
    expense_id: str,
    decision: ApprovalDecision,
    db: Database = Depends(get_database),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Endpoint for an approver to approve or reject an expense.
    """
    expense = db.expenses.find_one({"_id": ObjectId(expense_id)})
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found.")

    # Find the current pending approval step
    current_step_index = -1
    for i, step in enumerate(expense["approval_steps"]):
        if step["status"] == ApprovalStatus.PENDING:
            current_step_index = i
            break
    
    if current_step_index == -1 or expense["approval_steps"][current_step_index]["approver_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not your turn to approve this expense.")
        
    # --- Update the expense document ---
    # Update the specific step
    db.expenses.update_one(
        {"_id": ObjectId(expense_id), "approval_steps.approver_id": current_user.id},
        {
            "$set": {
                f"approval_steps.{current_step_index}.status": decision.status,
                f"approval_steps.{current_step_index}.comment": decision.comment,
                f"approval_steps.{current_step_index}.decision_date": datetime.utcnow()
            }
        }
    )
    
    # Update the overall expense status
    if decision.status == ApprovalStatus.REJECTED:
        db.expenses.update_one({"_id": ObjectId(expense_id)}, {"$set": {"status": ApprovalStatus.REJECTED}})
    elif current_step_index == len(expense["approval_steps"]) - 1: # Was this the last approver?
        db.expenses.update_one({"_id": ObjectId(expense_id)}, {"$set": {"status": ApprovalStatus.APPROVED}})

    updated_expense = db.expenses.find_one({"_id": ObjectId(expense_id)})
    return updated_expense