"""Order validation component - validate order with bag image."""

import streamlit as st

from staff_meal.storage import save_validation_result
from ui.components.bag_input import render_bag_image_input
from ui.components.order_comparison import render_order_comparison
from ui.components.output import render_order_details
from ui.components.qr_input import render_qr_input_section
from ui.components.validation_result import render_validation_result
from ui.services import compare_orders, predict_order
from ui.utils import runner


def render_order_validator() -> None:
    """Render order validation form with sequential steps: QR → Image → Results."""
    # Initialize step tracking
    if "validator_step" not in st.session_state:
        st.session_state.validator_step = 1

    # Step 1: QR Code
    if st.session_state.validator_step == 1:
        st.markdown(
            '<div style="text-align: center; font-size: 36px; font-weight: bold; margin: 20px 0;">📤 Scanner le QR Code</div>',
            unsafe_allow_html=True,
        )

        qr_image, order, error_message = render_qr_input_section(
            key_prefix="validator",
            title="",
        )

        # Store order in session state and progress to step 2 if successful
        if order:
            st.session_state.validator_order = order
            st.session_state.validator_error = None
            st.session_state.validator_step = 2
            st.rerun()
        elif error_message:
            st.session_state.validator_order = None
            st.session_state.validator_error = error_message
            st.error("❌ QR code non reconnu")
            return

    # Step 2: Bag Image
    elif st.session_state.validator_step == 2:
        st.markdown(
            '<div style="text-align: center; font-size: 36px; font-weight: bold; margin: 20px 0;">📸 Image de la commande</div>',
            unsafe_allow_html=True,
        )

        # Back button to Step 1
        if st.button("← RETOUR", width="stretch", help="Retourner à l'étape 1 pour scanner un nouveau QR code"):
            st.session_state.validator_step = 1
            st.session_state.validator_order = None
            st.rerun()

        st.divider()

        # Display order details
        if "validator_order" in st.session_state and st.session_state.validator_order:
            render_order_details(st.session_state.validator_order)
            st.divider()

        bag_image = render_bag_image_input(key_prefix="validator", title="")

        # Extract items button
        st.divider()
        extract_clicked = st.button(
            "🔍 EXTRAIRE LES ARTICLES",
            type="primary",
            width="stretch",
            help="Extraire les articles détectés dans l'image du sac",
            disabled=bag_image is None,
            key="validator_extract",
        )

        if extract_clicked:
            if bag_image is None:
                st.error("⚠️ Veuillez télécharger une image de la commande")
            else:
                # Store bag image in session state for Step 3 display
                st.session_state.validator_bag_image = bag_image
                with st.spinner("🔍 Extraction de la commande en cours..."):
                    expected_order = st.session_state.validator_order
                    detected_order = predict_order(bag_image, expected_order=expected_order)
                    st.session_state.validator_detected_order = detected_order
                    st.session_state.validator_step = 3
                    st.rerun()

    # Step 3: Results
    elif st.session_state.validator_step == 3:
        st.markdown(
            '<div style="text-align: center; font-size: 36px; font-weight: bold; margin: 20px 0;">✅ Résultat de la validation</div>',
            unsafe_allow_html=True,
        )

        # Back button to Step 2
        if st.button("← RETOUR", width="stretch", help="Retourner à l'étape 2 pour reprendre une photo"):
            st.session_state.validator_step = 2
            st.session_state.validator_detected_order = None
            st.rerun()

        st.divider()

        if "validator_detected_order" in st.session_state and st.session_state.validator_detected_order:
            # Side-by-side layout: Photo (left) | Order Details (right)
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### 📸 Image de la commande")
                if "validator_bag_image" in st.session_state and st.session_state.validator_bag_image:
                    st.image(
                        st.session_state.validator_bag_image,
                        caption="Image de la commande",
                        width="stretch",
                    )
                else:
                    st.info("Aucune image disponible")

            with col2:
                if "validator_order" in st.session_state and st.session_state.validator_order:
                    render_order_details(st.session_state.validator_order)

            st.divider()

            # Compare orders
            comparison_result = compare_orders(
                st.session_state.validator_order,
                st.session_state.validator_detected_order,
            )

            # Save validation result to database (only once per validation)
            if "validator_saved" not in st.session_state or not st.session_state.validator_saved:
                try:
                    runner.run(
                        save_validation_result(
                            expected_order=st.session_state.validator_order,
                            detected_order=st.session_state.validator_detected_order,
                            comparison_result=comparison_result,
                            operator=None,  # Could be added from user input in future
                        )
                    )
                    st.session_state.validator_saved = True
                except Exception as e:
                    # Don't break the UI if saving fails
                    st.warning(f"⚠️ Impossible de sauvegarder le résultat: {e}")

            # Display unified comparison view
            render_order_comparison(
                st.session_state.validator_order,
                st.session_state.validator_detected_order,
            )

            # Display validation result
            render_validation_result(
                is_complete=comparison_result.is_complete,
                comparison_result=comparison_result,
                order=st.session_state.validator_order,
            )

        # Button to start new validation
        st.divider()
        if st.button("🔄 Nouvelle validation", type="primary", width="stretch"):
            # Reset state
            st.session_state.validator_step = 1
            st.session_state.validator_order = None
            st.session_state.validator_detected_order = None
            st.session_state.validator_bag_image = None
            st.session_state.validator_error = None
            st.session_state.validator_saved = False
            st.rerun()


__all__ = ["render_order_validator"]
