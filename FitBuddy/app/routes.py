import asyncio
import json

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from .config import settings
from .database import get_db
from .gemini_flash_generator import generate_nutrition_tip_with_flash
from .gemini_generator import generate_workout_gemini
from .schemas import FeedbackRequest, UserInput
from .services import (
    delete_user,
    get_all_users,
    get_latest_plan,
    get_or_create_user,
    plan_to_text,
    save_plan,
    update_plan_record,
)
from .updated_plan import update_workout_plan

router = APIRouter()
templates = Jinja2Templates(directory="templates")


def admin_required(request: Request) -> None:
    if not request.session.get("admin_authenticated"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Admin login required")


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={"settings": settings})


@router.post("/generate-workout", response_class=HTMLResponse)
async def generate_workout(
    request: Request,
    name: str = Form(...),
    user_id: str = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...),
    experience_level: str = Form("beginner"),
    db: Session = Depends(get_db),
):
    try:
        user = UserInput(
            name=name,
            user_id=user_id,
            age=age,
            weight=weight,
            goal=goal,
            intensity=intensity,
            experience_level=experience_level,
        )
        plan, tip = await asyncio.gather(
            asyncio.to_thread(generate_workout_gemini, user),
            asyncio.to_thread(generate_nutrition_tip_with_flash, user),
        )
        db_user = get_or_create_user(db, user)
        record = save_plan(db, db_user, plan_to_text(plan), tip.model_dump_json(indent=2))
        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "user": user,
                "plan": plan,
                "nutrition_tip": tip,
                "record_id": record.id,
                "message": None,
            },
        )
    except Exception as exc:
        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={"message": str(exc)},
            status_code=400,
        )


@router.post("/submit-feedback", response_class=HTMLResponse)
async def submit_feedback(
    request: Request,
    user_id: str = Form(...),
    feedback: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        payload = FeedbackRequest(user_id=user_id, feedback=feedback)
        found = get_latest_plan(db, payload.user_id)
        if not found:
            raise ValueError("No workout plan was found for that User ID.")
        db_user, record = found
        user = UserInput(
            name=db_user.name,
            user_id=db_user.user_id,
            age=db_user.age,
            weight=db_user.weight,
            goal=db_user.goal,
            intensity=db_user.intensity,
            experience_level=db_user.experience_level,
        )
        original = record.original_plan
        updated = await asyncio.to_thread(update_workout_plan, original, payload.feedback, user)
        update_plan_record(db, record, plan_to_text(updated), payload.feedback)
        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "user": user,
                "plan": updated,
                "nutrition_tip": json.loads(record.nutrition_tip),
                "record_id": record.id,
                "message": "Your plan was updated from the feedback.",
            },
        )
    except Exception as exc:
        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={"message": str(exc)},
            status_code=400,
        )


@router.get("/admin", response_class=HTMLResponse)
def admin_login(request: Request):
    if request.session.get("admin_authenticated"):
        return RedirectResponse("/view-all-users", status_code=303)
    return templates.TemplateResponse(request=request, name="admin_login.html")


@router.post("/admin/login")
def admin_login_submit(request: Request, password: str = Form(...)):
    import secrets

    if secrets.compare_digest(password, settings.admin_password):
        request.session["admin_authenticated"] = True
        return RedirectResponse("/view-all-users", status_code=303)
    return templates.TemplateResponse(
        request=request,
        name="admin_login.html",
        context={"error": "Invalid admin password."},
        status_code=401,
    )


@router.post("/admin/logout")
def admin_logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=303)


@router.get("/view-all-users", response_class=HTMLResponse)
def view_all_users(request: Request, db: Session = Depends(get_db)):
    admin_required(request)
    users = get_all_users(db)
    return templates.TemplateResponse(
        request=request, name="all_users.html", context={"users": users}
    )


@router.post("/admin/delete/{user_id}")
def admin_delete_user(request: Request, user_id: str, db: Session = Depends(get_db)):
    admin_required(request)
    delete_user(db, user_id)
    return RedirectResponse("/view-all-users", status_code=303)


@router.get("/health")
def health():
    return {"status": "ok", "service": "fitbuddy"}


@router.post("/api/generate-workout")
async def api_generate_workout(payload: UserInput, db: Session = Depends(get_db)):
    plan, tip = await asyncio.gather(
        asyncio.to_thread(generate_workout_gemini, payload),
        asyncio.to_thread(generate_nutrition_tip_with_flash, payload),
    )
    db_user = get_or_create_user(db, payload)
    record = save_plan(db, db_user, plan_to_text(plan), tip.model_dump_json())
    return {
        "user": payload.model_dump(),
        "plan": plan.model_dump(),
        "nutrition_tip": tip.model_dump(),
        "record_id": record.id,
    }


@router.post("/api/feedback")
async def api_feedback(payload: FeedbackRequest, db: Session = Depends(get_db)):
    found = get_latest_plan(db, payload.user_id)
    if not found:
        raise HTTPException(status_code=404, detail="No plan found for this user.")
    db_user, record = found
    user = UserInput(
        name=db_user.name,
        user_id=db_user.user_id,
        age=db_user.age,
        weight=db_user.weight,
        goal=db_user.goal,
        intensity=db_user.intensity,
        experience_level=db_user.experience_level,
    )
    updated = await asyncio.to_thread(
        update_workout_plan, record.original_plan, payload.feedback, user
    )
    update_plan_record(db, record, plan_to_text(updated), payload.feedback)
    return {"user_id": payload.user_id, "plan": updated.model_dump(), "record_id": record.id}


@router.get("/api/users")
def api_users(request: Request, db: Session = Depends(get_db)):
    admin_required(request)
    users = get_all_users(db)
    return [
        {
            "user_id": u.user_id,
            "name": u.name,
            "age": u.age,
            "weight": u.weight,
            "goal": u.goal,
            "intensity": u.intensity,
            "experience_level": u.experience_level,
            "plans": [
                {
                    "id": p.id,
                    "original_plan": json.loads(p.original_plan),
                    "updated_plan": json.loads(p.updated_plan) if p.updated_plan else None,
                    "feedback": p.feedback,
                    "nutrition_tip": json.loads(p.nutrition_tip),
                }
                for p in u.plans
            ],
        }
        for u in users
    ]
