"""AI configuration sidebar component - model selection and API key override."""

import streamlit as st
from celeste import Model, list_models
from celeste.core import Capability, Provider
from ui.utils import get_provider_favicon_url


def render_ai_config_sidebar() -> None:
    """Render AI configuration sidebar with model selection and API key override."""
    with st.sidebar:
        st.markdown("### ⚙️ Celeste AI config")

        # Image Intelligence (for order prediction)
        with st.expander("🖼️ Image Intelligence", expanded=False):
            _render_capability_config(
                Capability.IMAGE_INTELLIGENCE, "google", "gemini-2.5-flash-lite"
            )

        # Text Generation (for explanations and insights)
        with st.expander("📝 Text Generation", expanded=False):
            _render_capability_config(
                Capability.TEXT_GENERATION, "google", "gemini-2.5-flash-lite"
            )

        # Speech Generation (for audio explanations)
        with st.expander("🔊 Speech Generation", expanded=False):
            _render_capability_config(
                Capability.SPEECH_GENERATION, "google", "gemini-2.5-flash-preview-tts"
            )

        # Image Generation (for demo mode)
        with st.expander("🎨 Image Generation", expanded=False):
            _render_capability_config(
                Capability.IMAGE_GENERATION, "google", "gemini-2.5-flash-image"
            )


def _render_capability_config(
    capability: Capability,
    default_provider: str,
    default_model: str,
) -> None:
    """Render configuration UI for a single capability.

    Args:
        capability: The capability to configure.
        default_provider: Default provider name.
        default_model: Default model name/ID.
    """
    cap_key = capability.value.replace("-", "_")

    # Get available providers
    models = list_models(capability=capability)
    providers = sorted({m.provider for m in models}, key=lambda x: x.value)

    if not providers:
        st.caption("No providers available")
        return

    # Show provider icons above selectbox
    icons_html = " ".join(
        f'<img src="{get_provider_favicon_url(p)}" width="20" height="20" title="{p.value.title()}" style="margin: 0 4px;" />'
        for p in providers
    )
    st.markdown(
        f'<div style="text-align: center; margin-bottom: 8px;">{icons_html}</div>',
        unsafe_allow_html=True,
    )

    # Provider selection
    provider_name = st.session_state.get(f"{cap_key}_provider", default_provider)
    provider = next((p for p in providers if p.value == provider_name), providers[0])

    provider_idx = providers.index(provider) if provider in providers else 0
    selected_provider = st.selectbox(
        "Provider",
        providers,
        index=provider_idx,
        key=f"{cap_key}_provider_select",
        format_func=lambda x: x.value.title(),
    )
    st.session_state[f"{cap_key}_provider"] = selected_provider.value

    # Show selected provider icon below selectbox
    if selected_provider:
        icon_url = get_provider_favicon_url(selected_provider)
        st.markdown(
            f'<div style="text-align: center; margin-top: -10px; margin-bottom: 8px;">'
            f'<img src="{icon_url}" width="20" height="20" title="{selected_provider.value.title()}" />'
            f"</div>",
            unsafe_allow_html=True,
        )

    # Model selection
    provider_models = sorted(
        [m for m in models if m.provider == selected_provider],
        key=lambda m: m.display_name,
    )

    if provider_models:
        model_id = st.session_state.get(f"{cap_key}_model", default_model)
        model_idx = next(
            (
                i
                for i, m in enumerate(provider_models)
                if m.id == model_id or m.display_name == model_id
            ),
            0,
        )

        selected_model = st.selectbox(
            "Model",
            provider_models,
            index=model_idx,
            key=f"{cap_key}_model_select",
            format_func=lambda m: m.display_name,
        )
        st.session_state[f"{cap_key}_model"] = selected_model.id

    # API key override
    st.caption("API Key (leave empty to use env variable)")
    # Use the key parameter to store directly in the session state key we use
    # This ensures consistency between what's displayed and what's stored
    # Streamlit automatically manages the session state when key is provided
    st.text_input(
        "API Key",
        type="password",
        value=st.session_state.get(f"{cap_key}_api_key", ""),
        key=f"{cap_key}_api_key",  # Store directly in the key we read from
        placeholder="Leave empty to use env variable",
    )


__all__ = ["render_ai_config_sidebar"]
