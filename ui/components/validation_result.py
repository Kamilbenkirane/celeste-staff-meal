"""Validation result display component - shows order validation results."""

import re

import streamlit as st

from celeste.artifacts import AudioArtifact
from celeste.exceptions import MissingCredentialsError
from celeste.mime_types import AudioMimeType

from staff_meal.models import ComparisonResult, Language, Order
from ui.services.explanation import (
    generate_validation_explanation,
    generate_validation_explanation_audio,
)
from ui.utils.audio import pcm_to_wav


def render_validation_result(
    is_complete: bool,
    comparison_result: ComparisonResult,
    expected_order: Order,
    detected_order: Order,
    show_explanation: bool = True,
) -> None:
    """Render validation result with clear visual feedback.

    Shows AI explanation first, then status badge, then collapsible error details.

    Args:
        is_complete: True if all items match and no extra items, False otherwise.
        comparison_result: ComparisonResult from compare_orders() with missing_items, too_few_items, too_many_items, extra_items.
        expected_order: Expected order from QR code.
        detected_order: Detected order from bag image.
        show_explanation: Whether to show AI-generated explanation (default True).
    """
    st.divider()

    if show_explanation:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("**💬 Explication:**")
        with col2:
            all_languages = [
                Language.FRENCH,
                Language.ENGLISH,
                Language.SPANISH,
                Language.ARABIC,
                Language.WOLOF,
                Language.BAMBARA,
                Language.MANDARIN_CHINESE,
                Language.VIETNAMESE,
                Language.PORTUGUESE,
                Language.ROMANIAN,
                Language.BERBER_TAMAZIGHT,
                Language.LINGALA,
                Language.SWAHILI,
                Language.CANTONESE,
                Language.TURKISH,
                Language.ITALIAN,
                Language.POLISH,
                Language.HINDI,
                Language.FULA_FULANI,
                Language.HAUSA,
                Language.KHMER,
                Language.URDU,
                Language.BENGALI,
                Language.TAGALOG,
                Language.TAMIL,
            ]

            language_display_names = {
                Language.FRENCH: "🇫🇷 Français",
                Language.ENGLISH: "🇬🇧 English",
                Language.SPANISH: "🇪🇸 Español",
                Language.ARABIC: "🇸🇦 العربية",
                Language.WOLOF: "🇸🇳 Wolof",
                Language.BAMBARA: "🇲🇱 Bambara",
                Language.MANDARIN_CHINESE: "🇨🇳 中文 (Mandarin)",
                Language.VIETNAMESE: "🇻🇳 Tiếng Việt",
                Language.PORTUGUESE: "🇵🇹 Português",
                Language.ROMANIAN: "🇷🇴 Română",
                Language.BERBER_TAMAZIGHT: "ⵣ Tamazight",
                Language.LINGALA: "🇨🇩 Lingála",
                Language.SWAHILI: "🇹🇿 Kiswahili",
                Language.CANTONESE: "🇭🇰 粵語 (Cantonese)",
                Language.TURKISH: "🇹🇷 Türkçe",
                Language.ITALIAN: "🇮🇹 Italiano",
                Language.POLISH: "🇵🇱 Polski",
                Language.HINDI: "🇮🇳 हिन्दी",
                Language.FULA_FULANI: "🇬🇳 Fulfulde",
                Language.HAUSA: "🇳🇬 Hausa",
                Language.KHMER: "🇰🇭 ភាសាខ្មែរ",
                Language.URDU: "🇵🇰 اردو",
                Language.BENGALI: "🇧🇩 বাংলা",
                Language.TAGALOG: "🇵🇭 Tagalog",
                Language.TAMIL: "🇮🇳 தமிழ்",
            }

            language = st.selectbox(
                "Langue",
                options=all_languages,
                format_func=lambda x: language_display_names.get(x, x.value),
                index=0,
                key="explanation_language",
            )
        try:
            try:
                explanation = generate_validation_explanation(expected_order, detected_order, language)
            except MissingCredentialsError:
                st.warning(
                    "⚠️ **API Key manquante** : Veuillez configurer la clé API pour Text Generation "
                    "dans la barre latérale (section ⚙️ Celeste AI config) ou définir la variable "
                    "d'environnement pour le fournisseur."
                )
                explanation = "Configuration de l'API requise pour générer l'explication."
            formatted_explanation = re.sub(
                r'"([^"]+)"',
                r'<strong style="color: #1976d2; font-weight: 600;">\1</strong>',
                explanation,
            )
            st.markdown(
                '<div style="background-color: #f8f9fa; padding: 24px; border-radius: 8px; margin: 15px 0; border: 1px solid #e0e0e0;">',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div style="margin: 0; font-size: 20px; line-height: 1.8; color: #212529;">{formatted_explanation}</div>',
                unsafe_allow_html=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)

            audio_key = f"audio_{expected_order.order_id}_{detected_order.order_id}_{language.value}"

            if audio_key not in st.session_state:
                st.session_state[audio_key] = None

            col1, col2 = st.columns([1, 3])
            with col1:
                generate_audio_clicked = st.button(
                    "🔊 Générer l'audio",
                    key=f"generate_audio_{audio_key}",
                    help="Générer la version audio de l'explication",
                )

            if generate_audio_clicked or st.session_state[audio_key] is not None:
                if st.session_state[audio_key] is None:
                    try:
                        with st.spinner("🔊 Génération de l'audio..."):
                            try:
                                audio_content = generate_validation_explanation_audio(explanation, language)
                                st.session_state[audio_key] = audio_content
                            except MissingCredentialsError:
                                st.warning(
                                    "⚠️ **API Key manquante** : Veuillez configurer la clé API pour Speech Generation "
                                    "dans la barre latérale (section ⚙️ Celeste AI config) ou définir la variable "
                                    "d'environnement pour le fournisseur."
                                )
                                st.session_state[audio_key] = None
                    except Exception:  # nosec B110
                        st.session_state[audio_key] = None
                        st.error("⚠️ Échec de la génération audio")

                if st.session_state[audio_key]:
                    audio_content = st.session_state[audio_key]
                    audio_bytes: bytes | None = None

                    if isinstance(audio_content, AudioArtifact):
                        if audio_content.data is not None:
                            if isinstance(audio_content.data, bytes):
                                audio_bytes = audio_content.data
                            elif hasattr(audio_content.data, "read"):
                                audio_bytes = audio_content.data.read()
                            else:
                                audio_bytes = None
                        elif hasattr(audio_content, "url") and audio_content.url:
                            import urllib.request
                            with urllib.request.urlopen(audio_content.url) as response:  # nosec B310
                                audio_bytes = response.read()

                        if audio_bytes and hasattr(audio_content, "mime_type"):
                            if audio_content.mime_type == AudioMimeType.PCM:
                                metadata = getattr(audio_content, "metadata", {}) or {}
                                audio_bytes = pcm_to_wav(
                                    audio_bytes,
                                    sample_rate=metadata.get("sample_rate", 24000),
                                    channels=metadata.get("channels", 1),
                                    sample_width=metadata.get("sample_width", 2),
                                )
                    elif isinstance(audio_content, bytes):
                        audio_bytes = audio_content

                    if audio_bytes:
                        st.audio(audio_bytes, autoplay=False)
        except Exception:  # nosec B110
            pass

    if is_complete:
        st.markdown(
            '<div style="text-align: center; background-color: #e8f5e9; padding: 30px; border-radius: 10px; margin: 20px 0;">',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div style="text-align: center; font-size: 64px; color: #2e7d32; margin: 10px 0;">✅</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div style="text-align: center; font-size: 36px; font-weight: bold; color: #2e7d32; margin: 10px 0;">VALIDÉ</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div style="text-align: center; font-size: 20px; color: #2e7d32; margin: 10px 0;">Tout est correct. Vous pouvez fermer le sac.</div>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        error_count = (
            len(comparison_result.missing_items)
            + len(comparison_result.too_few_items)
            + len(comparison_result.too_many_items)
            + len(comparison_result.extra_items)
        )
        st.markdown(
            '<div style="text-align: center; background-color: #ffebee; padding: 20px; border-radius: 10px; margin: 20px 0;">',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div style="text-align: center; font-size: 64px; color: #c62828; margin: 10px 0;">❌</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div style="text-align: center; font-size: 36px; font-weight: bold; color: #c62828; margin: 10px 0;">ERREUR</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div style="text-align: center; font-size: 18px; color: #c62828; margin: 10px 0;">{error_count} erreur(s) détectée(s)</div>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    if not is_complete:
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("🔍 Détails des erreurs", expanded=True):
            if comparison_result.missing_items:
                missing_list = ", ".join(
                    [
                        f"{item.item.value} ({item.expected_quantity}x)"
                        for item in comparison_result.missing_items
                    ]
                )
                st.markdown(f"**❌ Articles manquants:** {missing_list}")

            if comparison_result.too_few_items:
                too_few_list = ", ".join(
                    [
                        f"{item.item.value} (attendu: {item.expected_quantity}x, détecté: {item.detected_quantity}x)"
                        for item in comparison_result.too_few_items
                    ]
                )
                st.markdown(f"**⚠️ Quantités insuffisantes:** {too_few_list}")

            if comparison_result.too_many_items:
                too_many_list = ", ".join(
                    [
                        f"{item.item.value} (attendu: {item.expected_quantity}x, détecté: {item.detected_quantity}x)"
                        for item in comparison_result.too_many_items
                    ]
                )
                st.markdown(f"**⚠️ Quantités excessives:** {too_many_list}")

            if comparison_result.extra_items:
                extra_list = ", ".join(
                    [f"{item.item.value} ({item.quantity}x)" for item in comparison_result.extra_items]
                )
                st.markdown(f"**➕ Articles supplémentaires:** {extra_list}")


__all__ = ["render_validation_result"]
