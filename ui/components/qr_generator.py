"""QR code generator component - create order and generate QR code."""

import random
from typing import Any

import streamlit as st

from celeste import create_client
from celeste.artifacts import ImageArtifact
from celeste.core import Capability
from celeste.exceptions import MissingCredentialsError
from PIL import Image
from staff_meal.models import Item, Order, OrderItem, OrderSource
from staff_meal.order_storage import get_all_orders, save_order
from staff_meal.qr import generate_qr
from ui.components.output import render_image_output, render_order_details
from ui.services.client_config import get_client_config
from ui.utils import runner
from ui.utils.image import pil_image_to_bytes


def _generate_order_id() -> str:
    """Generate a unique order ID."""
    suffix = random.randint(10000, 99999)  # nosec B311
    return f"ORD-{suffix}"


def _format_order_prompt(order: Order) -> str:
    """Format order items into a prompt for image generation."""
    items_text = "\n".join(f"- {item.quantity}x {item.item.value}" for item in order.items)
    available_items = "\n".join(f"- {item.value}" for item in Item)

    prompt_parts = [
        "Generate a realistic image of a restaurant takeout meal showing ONLY the items from this order:",
        "",
        items_text,
        "",
        "CRITICAL REQUIREMENTS - DO NOT GENERATE EXTRA ITEMS:",
        "- Show ONLY the items listed above, nothing else",
        "- Do NOT add condiments, sauces, chopsticks, or any accessories unless explicitly listed in the order",
        "- Do NOT generate any items from the available menu list below unless they are in the order above",
        "",
        "Available menu items (for reference - do NOT generate these unless in order):",
        available_items,
        "",
        "CRITICAL PACKAGING REQUIREMENTS:",
        "- Show items in their actual packaging format as indicated by the item names",
        "- If an item name includes 'Boite de X' (box of X), show it as a box/container, not individual pieces",
        "- For example: 'Boite de 6 California Saumons' should be shown as 1 box containing 6 pieces, not 6 separate items",
        "- Each box/container should be clearly visible and distinct",
        "",
        "Style and composition:",
        "- Meal arranged on a kitchen countertop or clean surface",
        "- Items presented in appropriate containers (plastic boxes, bowls, etc.) matching the packaging format",
        "- Natural and clear lighting",
        "- Sharp and professional image",
        "- Top-down or slightly angled view to see all items clearly",
        "",
        "The image must show EXACTLY the indicated quantities of boxes/containers for each item, and NOTHING ELSE.",
    ]

    return "\n".join(prompt_parts)


def render_qr_generator() -> None:
    """Render QR code generator form and display."""
    st.markdown("#### 📝 Créer une commande")

    st.markdown("##### 📥 Charger une commande sauvegardée")
    try:
        saved_orders = runner.run(get_all_orders(limit=50))
        if saved_orders:
            order_options = {f"{order.order_id} ({order.source.value})": order for order in saved_orders}
            selected_order_key = st.selectbox(
                "Sélectionner une commande",
                options=[""] + list(order_options.keys()),
                key="load_saved_order",
            )

            if selected_order_key and selected_order_key != "":
                selected_order = order_options[selected_order_key]
                if st.button("📱 Charger et régénérer QR", key="load_order_btn"):
                    qr_image = generate_qr(selected_order)

                    st.session_state.generated_qr = qr_image
                    st.session_state.generated_order = selected_order

                    st.session_state.qr_generator_order_id = selected_order.order_id
                    st.session_state.qr_generator_source = selected_order.source
                    st.session_state.qr_generator_items = [
                        (item.item, item.quantity) for item in selected_order.items
                    ]
                    st.rerun()
        else:
            st.info("Aucune commande sauvegardée.")
    except Exception:  # nosec B110
        pass  # Silent failure - don't break UI if loading fails

    st.divider()

    if "qr_generator_order_id" not in st.session_state:
        st.session_state.qr_generator_order_id = _generate_order_id()

    default_source = (
        st.session_state.get("qr_generator_source", OrderSource.UBER_EATS)
        if "qr_generator_source" in st.session_state
        else OrderSource.UBER_EATS
    )
    source = st.selectbox(
        "Plateforme",
        [OrderSource.UBER_EATS, OrderSource.DELIVEROO],
        format_func=lambda x: "UberEats" if x == OrderSource.UBER_EATS else "Deliveroo",
        index=0 if default_source == OrderSource.UBER_EATS else 1,
        key="qr_generator_source",
    )

    st.markdown("**Articles:**")

    if "qr_generator_items" not in st.session_state:
        st.session_state.qr_generator_items = []

    items = st.session_state.qr_generator_items

    if items:
        for idx, (item_enum, quantity) in enumerate(items):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.text(f"{quantity}x {item_enum.value}")
            with col2:
                if st.button("✏️", key=f"edit_item_{idx}", help="Modifier"):
                    items.pop(idx)
                    st.session_state[f"edit_item_{idx}_item"] = item_enum
                    st.session_state[f"edit_item_{idx}_qty"] = quantity
                    st.rerun()
            with col3:
                if st.button("🗑️", key=f"remove_item_{idx}", help="Supprimer"):
                    items.pop(idx)
                    st.rerun()

    st.divider()
    col1, col2, col3 = st.columns([3, 1, 1])

    with col1:
        new_item = st.selectbox(
            "Article",
            list(Item),
            format_func=lambda x: x.value,
            key="qr_generator_new_item",
        )

    with col2:
        new_quantity = st.number_input(
            "Quantité",
            min_value=1,
            value=1,
            key="qr_generator_new_quantity",
        )

    with col3:
        st.markdown("<br>", unsafe_allow_html=True)  # Spacing
        if st.button("➕ Ajouter", key="qr_generator_add_item", width="stretch"):
            items.append((new_item, new_quantity))
            st.rerun()

    st.divider()
    generate_clicked = st.button(
        "📱 GÉNÉRER QR CODE",
        type="primary",
        width="stretch",
        help="Générer le QR code pour cette commande",
        disabled=not items,
    )

    if generate_clicked:
        if not items:
            st.error("⚠️ Veuillez ajouter au moins un article")
        else:
            order_id = st.session_state.qr_generator_order_id

            order_items = [OrderItem(item=item_enum, quantity=qty) for item_enum, qty in items]
            order = Order(order_id=order_id, source=source, items=order_items)

            qr_image = generate_qr(order)

            try:
                runner.run(save_order(order))
            except Exception:  # nosec B110
                pass  # Silent failure - order still works locally

            st.session_state.generated_qr = qr_image
            st.session_state.generated_order = order

            st.session_state.qr_generator_order_id = _generate_order_id()

    if "generated_qr" in st.session_state:
        st.divider()
        st.markdown("#### 📱 QR Code généré")

        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            img_bytes = pil_image_to_bytes(st.session_state.generated_qr)
            st.image(img_bytes, width=300)

        if "generated_order" in st.session_state:
            render_order_details(st.session_state.generated_order)

        st.divider()
        generate_image_clicked = st.button(
            "🎨 Générer une image d'exemple",
            width="stretch",
            type="secondary",
            help="Générer une image d'exemple de la commande avec l'IA",
        )

        if generate_image_clicked:
            if "generated_order" not in st.session_state:
                st.error("⚠️ Veuillez d'abord générer un QR code")
            else:
                with st.spinner("🎨 Génération de l'image en cours..."):
                    order = st.session_state.generated_order
                    provider, model, api_key = get_client_config(
                        Capability.IMAGE_GENERATION,
                        default_provider="google",
                        default_model="gemini-2.5-flash-image",
                    )
                    client_kwargs: dict[str, Any] = {
                        "capability": Capability.IMAGE_GENERATION,
                        "provider": provider,
                        "model": model.id,
                    }
                    if api_key is not None and api_key.get_secret_value():
                        client_kwargs["api_key"] = api_key

                    try:
                        client = create_client(**client_kwargs)
                        prompt = _format_order_prompt(order)
                        output = runner.run(client.generate(prompt=prompt))
                        st.session_state.generated_image_output = output
                    except MissingCredentialsError:
                        st.warning(
                            "⚠️ **API Key manquante** : Veuillez configurer la clé API pour Image Generation "
                            "dans la barre latérale (section ⚙️ Celeste AI config) ou définir la variable "
                            f"d'environnement pour le fournisseur {provider.value}."
                        )
                        st.stop()

        if "generated_image_output" in st.session_state:
            st.divider()
            st.markdown("#### 🎨 Image d'exemple générée")
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                render_image_output(st.session_state.generated_image_output)

        st.divider()
        qr_img_bytes = pil_image_to_bytes(st.session_state.generated_qr)

        generated_image_bytes: bytes | None = None
        if "generated_image_output" in st.session_state:
            generated_output: Any = st.session_state.generated_image_output
            artifact: ImageArtifact | None = None

            if hasattr(generated_output, "content"):
                content = generated_output.content
                if isinstance(content, ImageArtifact):
                    artifact = content
                elif isinstance(content, list) and content:
                    artifact = content[0] if isinstance(content[0], ImageArtifact) else None

            if artifact:
                if artifact.data is not None:
                    if isinstance(artifact.data, Image.Image):
                        img_buffer = pil_image_to_bytes(artifact.data)
                        generated_image_bytes = img_buffer.getvalue()
                    elif isinstance(artifact.data, bytes):
                        generated_image_bytes = artifact.data

        if generated_image_bytes:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.download_button(
                    label="💾 Télécharger QR Code",
                    data=qr_img_bytes,
                    file_name=f"qr_{st.session_state.generated_order.order_id}.png",
                    mime="image/png",
                    width="stretch",
                )
            with col2:
                st.download_button(
                    label="🎨 Télécharger Image",
                    data=generated_image_bytes,
                    file_name=f"image_{st.session_state.generated_order.order_id}.png",
                    mime="image/png",
                    width="stretch",
                )
            with col3:
                if st.button("➕ Créer une nouvelle commande", width="stretch", type="secondary"):
                    st.session_state.qr_generator_items = []
                    st.session_state.qr_generator_order_id = _generate_order_id()
                    if "generated_qr" in st.session_state:
                        del st.session_state.generated_qr
                    if "generated_order" in st.session_state:
                        del st.session_state.generated_order
                    if "generated_image_output" in st.session_state:
                        del st.session_state.generated_image_output
                    st.rerun()
        else:
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="💾 Télécharger QR Code",
                    data=qr_img_bytes,
                    file_name=f"qr_{st.session_state.generated_order.order_id}.png",
                    mime="image/png",
                    width="stretch",
                )
            with col2:
                if st.button("➕ Créer une nouvelle commande", width="stretch", type="secondary"):
                    st.session_state.qr_generator_items = []
                    st.session_state.qr_generator_order_id = _generate_order_id()
                    if "generated_qr" in st.session_state:
                        del st.session_state.generated_qr
                    if "generated_order" in st.session_state:
                        del st.session_state.generated_order
                    if "generated_image_output" in st.session_state:
                        del st.session_state.generated_image_output
                    st.rerun()


__all__ = ["render_qr_generator"]
