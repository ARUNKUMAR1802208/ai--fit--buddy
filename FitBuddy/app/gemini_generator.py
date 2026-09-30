from .ai_common import get_client
from .config import settings
from .schemas import UserInput, WorkoutPlan


def _mock_plan(user: UserInput) -> WorkoutPlan:
    focuses = [
        "Full body",
        "Upper body",
        "Cardio",
        "Lower body",
        "Core & mobility",
        "Active recovery",
        "Full body & stretching",
    ]
    days = []
    for i, focus in enumerate(focuses, start=1):
        days.append(
            {
                "day": f"Day {i}",
                "focus": focus,
                "warmup": "5–10 minutes of brisk walking and dynamic mobility.",
                "exercises": [
                    {"name": "Bodyweight squat", "sets": 3, "reps_or_duration": "10–12 reps", "rest": "60 sec"},
                    {"name": "Incline push-up", "sets": 3, "reps_or_duration": "8–12 reps", "rest": "60 sec"},
                    {"name": "Plank", "sets": 3, "reps_or_duration": "20–40 sec", "rest": "45 sec"},
                ],
                "cooldown": "5 minutes of easy movement and gentle stretching.",
            }
        )
    return WorkoutPlan(
        title=f"7-Day {user.goal.title()} Plan",
        summary=f"A {user.intensity}-intensity plan for {user.experience_level} level training.",
        days=days,
        safety_note="Start gradually, use controlled technique, and stop if you feel sharp pain, dizziness, or unusual symptoms.",
    )


def generate_workout_gemini(user: UserInput) -> WorkoutPlan:
    if settings.mock_ai:
        return _mock_plan(user)

    client = get_client()
    prompt = f"""
Create a safe, practical 7-day fitness plan for this user.

Name: {user.name}
Age: {user.age}
Weight: {user.weight} kg
Goal: {user.goal}
Preferred intensity: {user.intensity}
Experience level: {user.experience_level}

Requirements:
- Exactly 7 days.
- Each day must have a clear focus.
- Include a 5–10 minute warm-up.
- Include 1–8 exercises with sets, reps or duration, and rest.
- Include a cooldown/recovery instruction.
- Respect the requested intensity and experience level.
- Include rest or active-recovery work where appropriate.
- Do not diagnose conditions or prescribe medication.
- Do not claim the plan is medically personalized.
- Return only data matching the supplied structured schema.
"""
    response = client.models.generate_content(
        model=settings.workout_model,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": WorkoutPlan,
            "temperature": 0.5,
        },
    )
    if getattr(response, "parsed", None):
        return response.parsed
    return WorkoutPlan.model_validate_json(response.text)
