"""Client configuration service - model selection and API key management."""

from celeste import Model, list_models
from celeste.core import Capability, Provider
from pydantic import SecretStr


def get_client_config(
    capability: Capability,
    default_provider: Provider | str = "google",
    default_model: str = "",
) -> tuple[Provider, Model, SecretStr | None]:
    """Get client configuration from session state or defaults.

    Args:
        capability: The capability to get config for.
        default_provider: Default provider name.
        default_model: Default model name/ID.

    Returns:
        Tuple of (provider, model, api_key).
    """
    import streamlit as st

    # Get capability key for session state
    cap_key = capability.value.replace("-", "_")

    # Get provider from session state or use default
    provider_name = st.session_state.get(f"{cap_key}_provider", default_provider)
    if isinstance(provider_name, str):
        provider = Provider(provider_name)
    else:
        provider = provider_name

    # Get models for this capability and provider
    models = list_models(capability=capability, provider=provider)
    if not models:
        # Fallback to any provider
        all_models = list_models(capability=capability)
        if all_models:
            provider = all_models[0].provider
            models = [m for m in all_models if m.provider == provider]
        else:
            msg = f"No models found for capability {capability.value}"
            raise ValueError(msg)

    # Get model from session state or use default
    model_id = st.session_state.get(f"{cap_key}_model", default_model)
    if model_id:
        model = next(
            (m for m in models if m.id == model_id or m.display_name == model_id), None
        )
    else:
        model = None

    if not model:
        model = models[0]  # Use first available model

    # Get API key from session state
    api_key_str = st.session_state.get(f"{cap_key}_api_key", "")
    api_key = SecretStr(api_key_str) if api_key_str else None

    return provider, model, api_key


__all__ = ["get_client_config"]
