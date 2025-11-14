"""Output component - order details rendering."""

from typing import Any

import streamlit as st

from staff_meal.models import Order


def render_order_details(order: Order) -> None:
    """Render order details in a clear format.

    Args:
        order: Order object to display.
    """
    st.markdown("#### 📋 Détails de la commande")
    st.markdown(f"**N° Commande:** {order.order_id}")
    st.markdown(f"**Plateforme:** {order.source.value}")
    st.markdown("**Articles:**")
    for item in order.items:
        st.markdown(f"- {item.quantity}x {item.item.value}")


def render_image_output(output: Any) -> None:
    """Render Celeste AI image generation output.

    Args:
        output: Output from client.generate(). Expected to have a `content` attribute
            containing an ImageArtifact or list of ImageArtifacts, or a `render()` method.
    """
    from celeste.artifacts import ImageArtifact

    # Celeste output should handle its own rendering
    # If it has a render method, use it
    if hasattr(output, "render"):
        output.render()
        return

    # Check if output has content attribute
    if not hasattr(output, "content"):
        st.error("⚠️ Format de sortie non reconnu")
        return

    # output.content is a single ImageArtifact, not a list
    artifact = output.content
    if isinstance(artifact, ImageArtifact):
        # Try data first (bytes or PIL Image)
        if artifact.data is not None:
            st.image(artifact.data, width=400, caption="Image d'exemple de la commande")
            return
        # Fallback to URL
        if artifact.url:
            st.image(artifact.url, width=400, caption="Image d'exemple de la commande")
            return

    # If content is a list, iterate over it
    if isinstance(output.content, list):
        for item in output.content:
            if isinstance(item, ImageArtifact):
                if item.data is not None:
                    st.image(item.data, width=400, caption="Image d'exemple de la commande")
                    return
                if item.url:
                    st.image(item.url, width=400, caption="Image d'exemple de la commande")
                    return

    st.warning("⚠️ Aucune image trouvée dans la sortie")


__all__ = ["render_order_details", "render_image_output"]
