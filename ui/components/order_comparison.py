"""Order comparison component - unified visual comparison of orders."""

import streamlit as st

from staff_meal.models import Order


def render_order_comparison(expected: Order, detected: Order) -> None:
    """Render unified comparison view of expected vs detected order.

    Shows:
    - Single unified comparison table
    - Each row: Item | Expected | Detected | Status
    - Color-coded rows: green (match), red (mismatch), orange (extra)

    Args:
        expected: Expected order from QR code.
        detected: Detected order from bag image.
    """
    # Build detected items dict for quick lookup
    detected_items: dict[str, int] = {}
    for item in detected.items:
        detected_items[item.item.value] = item.quantity

    # Build expected items set for extra items check
    expected_item_names = {item.item.value for item in expected.items}

    # Container with card-like styling
    with st.container():
        st.markdown(
            '<div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin: 20px 0;">',
            unsafe_allow_html=True,
        )

        st.markdown("#### 📊 Comparaison des articles")

        # Header row
        col1, col2, col3, col4 = st.columns([3, 1.5, 1.5, 1])
        with col1:
            st.markdown("**Article**")
        with col2:
            st.markdown("**Attendu**")
        with col3:
            st.markdown("**Détecté**")
        with col4:
            st.markdown("**Statut**")

        st.divider()

        # Compare each expected item
        for expected_item in expected.items:
            item_name = expected_item.item.value
            expected_qty = expected_item.quantity
            detected_qty = detected_items.get(item_name, 0)
            is_match = expected_qty == detected_qty

            col1, col2, col3, col4 = st.columns([3, 1.5, 1.5, 1])

            with col1:
                st.markdown(f"**{item_name}**")

            with col2:
                st.markdown(f"{expected_qty}x")

            with col3:
                if is_match:
                    st.markdown(
                        f'<div style="color: #00cc00; font-weight: bold;">{detected_qty}x</div>',
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f'<div style="color: #ff4444; font-weight: bold;">{detected_qty}x</div>',
                        unsafe_allow_html=True,
                    )

            with col4:
                if is_match:
                    st.markdown(
                        '<div style="color: #00cc00; font-size: 20px;">✅</div>',
                        unsafe_allow_html=True,
                    )
                else:
                    if detected_qty == 0:
                        status_text = "❌"
                        status_color = "#ff4444"
                    elif detected_qty < expected_qty:
                        status_text = "⚠️"
                        status_color = "#ff8800"
                    else:
                        status_text = "⚠️"
                        status_color = "#ff8800"
                    st.markdown(
                        f'<div style="color: {status_color}; font-size: 20px;">{status_text}</div>',
                        unsafe_allow_html=True,
                    )

        # Check for extra items (detected but not in expected)
        extra_items = [
            item for item in detected.items if item.item.value not in expected_item_names
        ]

        # Display extra items
        for extra_item in extra_items:
            col1, col2, col3, col4 = st.columns([3, 1.5, 1.5, 1])

            with col1:
                st.markdown(
                    f'<div style="color: #ff8800;">**{extra_item.item.value}**</div>',
                    unsafe_allow_html=True,
                )

            with col2:
                st.markdown('<div style="color: #999;">—</div>', unsafe_allow_html=True)

            with col3:
                st.markdown(
                    f'<div style="color: #ff8800; font-weight: bold;">{extra_item.quantity}x</div>',
                    unsafe_allow_html=True,
                )

            with col4:
                st.markdown(
                    '<div style="color: #ff8800; font-size: 20px;">⚠️</div>',
                    unsafe_allow_html=True,
                )

        st.markdown("</div>", unsafe_allow_html=True)


__all__ = ["render_order_comparison"]
