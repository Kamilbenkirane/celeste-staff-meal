"""Validation result display component - shows order validation results."""

import streamlit as st

from staff_meal.models import ComparisonResult, Order


def render_validation_result(
    is_complete: bool,
    comparison_result: ComparisonResult,
    order: Order,
) -> None:
    """Render validation result with clear visual feedback.

    Shows ✅ "VALIDÉ" or ❌ "ERREUR" with grouped, actionable error messages.

    Args:
        is_complete: True if all items match and no extra items, False otherwise.
        comparison_result: ComparisonResult from compare_orders() with missing_items, too_few_items, too_many_items, extra_items.
        order: Order object being validated.
    """
    st.divider()

    if is_complete:
        # Success state - large green checkmark
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
        # Failure state - large red X with error summary
        st.markdown(
            '<div style="text-align: center; background-color: #ffebee; padding: 20px; border-radius: 10px; margin: 20px 0;">',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div style="text-align: center; font-size: 64px; color: #c62828; margin: 10px 0;">❌</div>',
            unsafe_allow_html=True,
        )

        # Count total errors
        error_count = (
            len(comparison_result.missing_items)
            + len(comparison_result.too_few_items)
            + len(comparison_result.too_many_items)
            + len(comparison_result.extra_items)
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

        # Detailed error breakdown
        st.markdown("#### 🔍 Détails des erreurs")

        # Missing items (not detected at all)
        if comparison_result.missing_items:
            st.markdown(
                '<div style="background-color: #ffebee; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #c62828;">',
                unsafe_allow_html=True,
            )
            st.markdown("**❌ Articles manquants:**")
            for item_mismatch in comparison_result.missing_items:
                item_name = item_mismatch.item.value
                expected_qty = item_mismatch.expected_quantity
                st.markdown(
                    f'<div style="margin: 8px 0; font-size: 18px;">• {item_name} (attendu: {expected_qty}x, détecté: 0x)</div>',
                    unsafe_allow_html=True,
                )
            st.markdown("</div>", unsafe_allow_html=True)

        # Too few items
        if comparison_result.too_few_items:
            st.markdown(
                '<div style="background-color: #fff3e0; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #ff8800;">',
                unsafe_allow_html=True,
            )
            st.markdown("**⚠️ Quantités insuffisantes:**")
            for item_mismatch in comparison_result.too_few_items:
                item_name = item_mismatch.item.value
                expected_qty = item_mismatch.expected_quantity
                detected_qty = item_mismatch.detected_quantity
                st.markdown(
                    f'<div style="margin: 8px 0; font-size: 18px;">• {item_name} (attendu: {expected_qty}x, détecté: {detected_qty}x)</div>',
                    unsafe_allow_html=True,
                )
            st.markdown("</div>", unsafe_allow_html=True)

        # Too many items
        if comparison_result.too_many_items:
            st.markdown(
                '<div style="background-color: #fff3e0; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #ff8800;">',
                unsafe_allow_html=True,
            )
            st.markdown("**⚠️ Quantités excessives:**")
            for item_mismatch in comparison_result.too_many_items:
                item_name = item_mismatch.item.value
                expected_qty = item_mismatch.expected_quantity
                detected_qty = item_mismatch.detected_quantity
                st.markdown(
                    f'<div style="margin: 8px 0; font-size: 18px;">• {item_name} (attendu: {expected_qty}x, détecté: {detected_qty}x)</div>',
                    unsafe_allow_html=True,
                )
            st.markdown("</div>", unsafe_allow_html=True)

        # Extra items (not in expected order)
        if comparison_result.extra_items:
            st.markdown(
                '<div style="background-color: #fff3e0; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #ff8800;">',
                unsafe_allow_html=True,
            )
            st.markdown("**⚠️ Articles supplémentaires:**")
            for item in comparison_result.extra_items:
                st.markdown(
                    f'<div style="margin: 8px 0; font-size: 18px;">• {item.item.value} ({item.quantity}x)</div>',
                    unsafe_allow_html=True,
                )
            st.markdown("</div>", unsafe_allow_html=True)


__all__ = ["render_validation_result"]
