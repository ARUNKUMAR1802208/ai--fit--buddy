from .ai_common import get_client
from .config import settings
from .gemini_generator import _mock_plan
from .schemas import UserInput, WorkoutPlan


def update_workout_plan(original_plan: str, feedback: str, user: UserInput) -> WorkoutPlan:
    if settings.mock_ai:
        plan = _mock_plan(user)
        plan.summary = f"Updated using feedback: {feedback[:160]}"
        return plan

    client = get_client()
    prompt = f"""
Revise the existing 7-day fitness plan according to the user's feedback.

User profile:
- Age: {user.age}
- Weight: {user.weight} kg
- Goal: {user.goal}
- Intensity: {user.intensity}
- Experience: {user.experience_level}

Original plan:
{original_plan}

User feedback:
{feedback}

Requirements:
- Preserve useful parts of the original plan.
- Apply the feedback where it is safe and reasonable.
- Keep exactly 7 days.
- Keep warm-up, exercises, sets/reps or duration, rest, and cooldown for every day.
- Do not diagnose or prescribe medication.
- Return only data matching the structured schema.
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
