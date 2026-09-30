from typing import Literal

from pydantic import BaseModel, Field, field_validator


Goal = Literal["weight loss", "muscle gain", "general wellness", "flexibility"]
Intensity = Literal["low", "medium", "high"]
Experience = Literal["beginner", "intermediate", "advanced"]


class UserInput(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    user_id: str = Field(min_length=2, max_length=80, pattern=r"^[A-Za-z0-9_-]+$")
    age: int = Field(ge=13, le=100)
    weight: float = Field(gt=25, le=400)
    goal: Goal
    intensity: Intensity
    experience_level: Experience = "beginner"

    @field_validator("name", "user_id")
    @classmethod
    def strip_strings(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be empty.")
        return value


class FeedbackRequest(BaseModel):
    user_id: str = Field(min_length=2, max_length=80)
    feedback: str = Field(min_length=3, max_length=2000)


class Exercise(BaseModel):
    name: str
    sets: int = Field(ge=1, le=10)
    reps_or_duration: str
    rest: str


class DayPlan(BaseModel):
    day: str
    focus: str
    warmup: str
    exercises: list[Exercise] = Field(min_length=1, max_length=8)
    cooldown: str


class WorkoutPlan(BaseModel):
    title: str
    summary: str
    days: list[DayPlan] = Field(min_length=7, max_length=7)
    safety_note: str


class NutritionTip(BaseModel):
    tip: str
    recovery_note: str
