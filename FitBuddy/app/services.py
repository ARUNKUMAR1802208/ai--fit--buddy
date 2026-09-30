import json
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from .models import User, WorkoutPlanRecord
from .schemas import UserInput


def plan_to_text(plan) -> str:
    return json.dumps(plan.model_dump(), indent=2, ensure_ascii=False)


def get_or_create_user(db: Session, data: UserInput) -> User:
    user = db.scalar(select(User).where(User.user_id == data.user_id))
    if user:
        user.name = data.name
        user.age = data.age
        user.weight = data.weight
        user.goal = data.goal
        user.intensity = data.intensity
        user.experience_level = data.experience_level
    else:
        user = User(**data.model_dump())
        db.add(user)
        db.flush()
    return user


def save_plan(db: Session, user: User, original_plan: str, nutrition_tip: str) -> WorkoutPlanRecord:
    record = WorkoutPlanRecord(
        user_pk=user.id,
        original_plan=original_plan,
        nutrition_tip=nutrition_tip,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def update_plan_record(
    db: Session, record: WorkoutPlanRecord, updated_plan: str, feedback: str
) -> WorkoutPlanRecord:
    record.updated_plan = updated_plan
    record.feedback = feedback
    record.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(record)
    return record


def get_latest_plan(db: Session, user_id: str) -> tuple[User, WorkoutPlanRecord] | None:
    user = db.scalar(
        select(User)
        .options(selectinload(User.plans))
        .where(User.user_id == user_id)
    )
    if not user or not user.plans:
        return None
    record = sorted(user.plans, key=lambda p: p.created_at)[-1]
    return user, record


def get_all_users(db: Session) -> list[User]:
    return list(
        db.scalars(
            select(User).options(selectinload(User.plans)).order_by(User.created_at.desc())
        ).unique()
    )


def delete_user(db: Session, user_id: str) -> bool:
    user = db.scalar(select(User).where(User.user_id == user_id))
    if not user:
        return False
    db.delete(user)
    db.commit()
    return True
