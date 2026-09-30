from .ai_common import get_client
from .config import settings
from .schemas import NutritionTip, UserInput


def _mock_tip(user: UserInput) -> NutritionTip:
    if user.goal == "muscle gain":
        return NutritionTip(
            tip="Include a protein-rich food in each main meal, such as eggs, fish, chicken, beans, lentils, or Greek yogurt.",
            recovery_note="Hydrate regularly and allow adequate sleep between demanding sessions.",
        )
    if user.goal == "weight loss":
        return NutritionTip(
            tip="Build meals around vegetables, a protein source, high-fiber carbohydrates, and sensible portions rather than relying on extreme restriction.",
            recovery_note="Keep hydration and sleep consistent to support training and recovery.",
        )
    if user.goal == "flexibility":
        return NutritionTip(
            tip="Prioritize balanced meals with protein, fruits or vegetables, whole grains, and adequate fluids.",
            recovery_note="Use gentle mobility work and avoid forcing a stretch into pain.",
        )
    return NutritionTip(
        tip="Aim for balanced meals containing protein, vegetables or fruit, whole grains, and healthy fats.",
        recovery_note="Hydrate consistently and give your body adequate sleep and recovery time.",
    )


def generate_nutrition_tip_with_flash(user: UserInput) -> NutritionTip:
    if settings.mock_ai:
        return _mock_tip(user)

    client = get_client()
    prompt = f"""
Give one concise nutrition/recovery tip for a fitness user.

Goal: {user.goal}
Intensity: {user.intensity}
Experience: {user.experience_level}

Keep it practical, non-medical, and suitable for a general wellness application.
Return only the requested structured JSON.
"""
    response = client.models.generate_content(
        model=settings.tip_model,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": NutritionTip,
            "temperature": 0.4,
        },
    )
    if getattr(response, "parsed", None):
        return response.parsed
    return NutritionTip.model_validate_json(response.text)
