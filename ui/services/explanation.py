"""Service layer for generating AI explanations of validation results."""

from typing import Any

from pydantic import SecretStr

from celeste import create_client
from celeste.artifacts import AudioArtifact
from celeste.core import Capability, Provider
from staff_meal.models import Language, Order, Statistics, ValidationRecord
from ui.services.client_config import get_client_config


async def generate_validation_explanation_async(
    expected_order: Order,
    detected_order: Order,
    language: Language = Language.FRENCH,
    provider: Provider | None = None,
    model_id: str | None = None,
    api_key: SecretStr | None = None,
) -> str:
    """Generate friendly explanation of validation result using Celeste text generation.

    Args:
        expected_order: Expected order from QR code.
        detected_order: Detected order from bag image.
        language: Language for the explanation (default: French).
        provider: Provider to use (passed from sync function where session state is available).
        model_id: Model ID to use (passed from sync function where session state is available).
        api_key: API key override (passed from sync function where session state is available).

    Returns:
        Generated explanation text in the specified language.

    Raises:
        ValueError: If explanation generation fails.
    """
    client_kwargs: dict[str, Any] = {
        "capability": Capability.TEXT_GENERATION,
        "provider": provider,
        "model": model_id,
    }
    # Only add api_key if it's provided and non-empty (empty SecretStr prevents env var fallback)
    if api_key is not None:
        api_key_value = api_key.get_secret_value()
        if api_key_value and api_key_value.strip():
            client_kwargs["api_key"] = api_key

    client = create_client(**client_kwargs)

    expected_dict = expected_order.model_dump()
    detected_dict = detected_order.model_dump()

    prompt = f"""You are helping restaurant staff verify orders. Compare these two orders and explain (2-3 sentences maximum) what's missing, what's wrong, or confirm that the order is complete.

Expected order:
{expected_dict}

Detected order:
{detected_dict}

Generate the answer in {language.value}. Do not use quotes around item names - write them naturally in the text."""

    output = await client.generate(prompt=prompt)

    if hasattr(output, "content"):
        explanation = str(output.content)
    else:
        explanation = str(output)

    if not explanation or explanation.strip() == "":
        msg = "Failed to generate explanation"
        raise ValueError(msg)

    return explanation.strip()


def generate_validation_explanation(
    expected_order: Order,
    detected_order: Order,
    language: Language = Language.FRENCH,
) -> str:
    """Generate validation explanation (sync wrapper for Streamlit).

    Args:
        expected_order: Expected order from QR code.
        detected_order: Detected order from bag image.
        language: Language for the explanation (default: French).

    Returns:
        Generated explanation text in the specified language.

    Raises:
        ValueError: If explanation generation fails.
    """
    from ui.utils import runner

    # Read config in main thread where session state is available
    provider, model, api_key = get_client_config(
        Capability.TEXT_GENERATION,
        default_provider="google",
        default_model="gemini-2.5-flash-lite",
    )

    # Pass config to async function (runs in background thread without session state access)
    return runner.run(
        generate_validation_explanation_async(
            expected_order,
            detected_order,
            language,
            provider=provider,
            model_id=model.id,
            api_key=api_key,
        )
    )  # type: ignore[no-any-return]


async def generate_dashboard_insights(
    stats: Statistics,
    records: list[ValidationRecord],
    provider: Provider | None = None,
    model_id: str | None = None,
    api_key: SecretStr | None = None,
) -> str:
    """Generate AI-powered insights and recommendations for dashboard.

    Args:
        stats: Calculated statistics from validation records.
        records: List of validation records for analysis.
        provider: Provider to use (passed from sync function where session state is available).
        model_id: Model ID to use (passed from sync function where session state is available).
        api_key: API key override (passed from sync function where session state is available).

    Returns:
        Generated insights text in French with recommendations.

    Raises:
        ValueError: If insight generation fails.
    """
    if not records:
        return "📊 Aucune donnée disponible pour générer des recommandations."

    client_kwargs: dict[str, Any] = {
        "capability": Capability.TEXT_GENERATION,
        "provider": provider,
        "model": model_id,
    }
    # Only add api_key if it's provided and non-empty (empty SecretStr prevents env var fallback)
    if api_key is not None:
        api_key_value = api_key.get_secret_value()
        if api_key_value and api_key_value.strip():
            client_kwargs["api_key"] = api_key

    client = create_client(**client_kwargs)

    total_errors = stats.total_orders - stats.complete_orders
    most_forgotten_str = ""
    if stats.most_forgotten_items:
        top_items = stats.most_forgotten_items[:5]
        most_forgotten_str = ", ".join([f"{item.value} ({count}x)" for item, count in top_items])

    peak_hours: list[int] = []
    if stats.errors_by_hour:
        max_errors = max(stats.errors_by_hour.values())
        if max_errors > 0:
            peak_hours = [hour for hour, count in stats.errors_by_hour.items() if count == max_errors]

    peak_days: list[str] = []
    if stats.errors_by_day:
        max_day_errors = max(stats.errors_by_day.values())
        if max_day_errors > 0:
            peak_days = [day for day, count in stats.errors_by_day.items() if count == max_day_errors]

    missing_count = sum(len(r.comparison_result.missing_items) for r in records if not r.is_complete)
    too_few_count = sum(len(r.comparison_result.too_few_items) for r in records if not r.is_complete)
    too_many_count = sum(len(r.comparison_result.too_many_items) for r in records if not r.is_complete)
    extra_count = sum(len(r.comparison_result.extra_items) for r in records if not r.is_complete)

    error_severity = "🔴 CRITIQUE" if stats.error_rate > 20 else "🟡 ATTENTION" if stats.error_rate > 10 else "🟢 OK"

    prompt = f"""Tu es le chef de logistique d'un restaurant. Analyse ces données et génère 3-5 recommandations URGENTES et ACTIONNABLES.

📊 DONNÉES:
• {stats.total_orders} commandes | {stats.complete_orders} complètes | {stats.error_rate:.1f}% erreurs {error_severity}
• Articles oubliés: {most_forgotten_str if most_forgotten_str else "Aucun"}
• Erreurs: {missing_count} manquants | {too_few_count} insuffisants | {too_many_count} excès | {extra_count} supplémentaires
• Pic d'erreurs: {', '.join(map(str, peak_hours)) if peak_hours else "Aucun"}h | {', '.join(peak_days) if peak_days else "Aucun"}

🎯 FORMAT DE RÉPONSE (3-5 points max):
Utilise des emojis (🔴🟡🟢⚠️📌💡) et sois DIRECT et IMPACTANT.
Chaque point = 1 ligne max avec action concrète.
Exemple: "🔴 CRITIQUE: Sauce oubliée 15x → Former équipe 12h-14h"

Génère maintenant les recommandations les plus importantes."""

    output = await client.generate(prompt=prompt)

    if hasattr(output, "content"):
        insights = str(output.content)
    else:
        insights = str(output)

    if not insights or insights.strip() == "":
        msg = "Failed to generate dashboard insights"
        raise ValueError(msg)

    return insights.strip()


def generate_dashboard_insights_sync(
    stats: Statistics,
    records: list[ValidationRecord],
) -> str:
    """Generate dashboard insights (sync wrapper for Streamlit).

    Args:
        stats: Calculated statistics from validation records.
        records: List of validation records for analysis.

    Returns:
        Generated insights text in French with recommendations.

    Raises:
        ValueError: If insight generation fails.
    """
    from ui.utils import runner

    # Read config in main thread where session state is available
    provider, model, api_key = get_client_config(
        Capability.TEXT_GENERATION,
        default_provider="google",
        default_model="gemini-2.5-flash-lite",
    )

    # Pass config to async function (runs in background thread without session state access)
    return runner.run(
        generate_dashboard_insights(
            stats,
            records,
            provider=provider,
            model_id=model.id,
            api_key=api_key,
        )
    )  # type: ignore[no-any-return]


async def generate_validation_explanation_audio_async(
    explanation_text: str,
    language: Language = Language.FRENCH,
    provider: Provider | None = None,
    model_id: str | None = None,
    api_key: SecretStr | None = None,
) -> AudioArtifact | bytes:
    """Generate audio from explanation text using Celeste speech generation.

    Args:
        explanation_text: Text explanation to convert to speech.
        language: Language for the explanation (default: French).
        provider: Provider to use (passed from sync function where session state is available).
        model_id: Model ID to use (passed from sync function where session state is available).
        api_key: API key override (passed from sync function where session state is available).

    Returns:
        AudioArtifact with mime_type and metadata, or bytes if AudioArtifact not available.

    Raises:
        ValueError: If audio generation fails.
    """
    client_kwargs: dict[str, Any] = {
        "capability": Capability.SPEECH_GENERATION,
        "provider": provider,
        "model": model_id,
    }
    # Only add api_key if it's provided and non-empty (empty SecretStr prevents env var fallback)
    if api_key is not None:
        api_key_value = api_key.get_secret_value()
        if api_key_value and api_key_value.strip():
            client_kwargs["api_key"] = api_key

    client = create_client(**client_kwargs)

    output = await client.generate(
        prompt=explanation_text,
        voice="Orus",
    )

    if hasattr(output, "content"):
        audio_content = output.content

        if isinstance(audio_content, AudioArtifact):
            return audio_content

        if hasattr(audio_content, "data") or hasattr(audio_content, "mime_type"):
            audio_data: bytes | None = None

            if hasattr(audio_content, "data") and audio_content.data is not None:
                if isinstance(audio_content.data, bytes):
                    audio_data = audio_content.data
                elif hasattr(audio_content.data, "read"):
                    audio_data = audio_content.data.read()

            if audio_data is None and hasattr(audio_content, "url") and audio_content.url:
                import urllib.request
                with urllib.request.urlopen(audio_content.url) as response:  # nosec B310
                    audio_data = response.read()

            if audio_data is not None:
                mime_type: str | None = None
                if hasattr(audio_content, "mime_type"):
                    mime_type = str(audio_content.mime_type)

                metadata: dict[str, Any] = {}
                if hasattr(audio_content, "metadata"):
                    metadata = dict(audio_content.metadata) if audio_content.metadata else {}

                return AudioArtifact(
                    data=audio_data,
                    mime_type=mime_type,  # type: ignore[arg-type]
                    metadata=metadata or {},
                )

        if isinstance(audio_content, bytes):
            return audio_content

        if isinstance(audio_content, str):
            msg = "Audio content is string, expected AudioArtifact or bytes"
            raise ValueError(msg)

        try:
            return bytes(audio_content)
        except (TypeError, ValueError) as e:
            msg = f"Failed to extract audio content: {type(audio_content)}"
            raise ValueError(msg) from e

    msg = "Output does not have content attribute"
    raise ValueError(msg)


def generate_validation_explanation_audio(
    explanation_text: str,
    language: Language = Language.FRENCH,
) -> AudioArtifact | bytes:
    """Generate audio from explanation text (sync wrapper for Streamlit).

    Args:
        explanation_text: Text explanation to convert to speech.
        language: Language for the explanation (default: French).

    Returns:
        AudioArtifact with mime_type and metadata, or bytes if AudioArtifact not available.

    Raises:
        ValueError: If audio generation fails.
    """
    from ui.utils import runner

    # Read config in main thread where session state is available
    provider, model, api_key = get_client_config(
        Capability.SPEECH_GENERATION,
        default_provider="google",
        default_model="gemini-2.5-flash-preview-tts",
    )

    # Pass config to async function (runs in background thread without session state access)
    return runner.run(
        generate_validation_explanation_audio_async(
            explanation_text,
            language,
            provider=provider,
            model_id=model.id,
            api_key=api_key,
        )
    )  # type: ignore[no-any-return]


__all__ = [
    "generate_validation_explanation",
    "generate_validation_explanation_async",
    "generate_validation_explanation_audio",
    "generate_validation_explanation_audio_async",
    "generate_dashboard_insights",
    "generate_dashboard_insights_sync",
]
