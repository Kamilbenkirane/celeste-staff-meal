"""Order validation component - validate order with bag image."""

import hashlib
import io

import streamlit as st

from staff_meal.storage import save_validation_result
from ui.components.bag_input import render_bag_image_input
from ui.components.input import render_image_input
from ui.components.order_comparison import render_order_comparison
from ui.components.output import render_order_details
from ui.components.validation_result import render_validation_result
from celeste.exceptions import MissingCredentialsError

from ui.services import compare_orders, predict_order, read_qr_order
from ui.utils import runner


def render_order_validator() -> None:
    """Render order validation form with sequential steps: QR → Image → Results."""
    if "validator_step" not in st.session_state:
        st.session_state.validator_step = 1

    if st.session_state.validator_step == 1:
        st.markdown(
            '<div style="text-align: center; font-size: 36px; font-weight: bold; margin: 20px 0;">📤 Scanner le QR Code</div>',
            unsafe_allow_html=True,
        )

        qr_image = render_image_input(
            key_prefix="validator",
            file_label="Télécharger une image",
            camera_label="Prendre une photo",
            file_help="Télécharger la photo du QR code",
            camera_help="Prendre une photo du QR code avec la caméra",
            preview_caption="QR Code",
            toggle_to_camera_label="📷 Scanner un QR code",
            toggle_to_file_label="📁 Importer un QR code",
        )

        if qr_image:
            img_bytes = io.BytesIO()
            qr_image.save(img_bytes, format="PNG")
            img_hash = hashlib.md5(img_bytes.getvalue(), usedforsecurity=False).hexdigest()  # nosec B324
            last_processed_hash = st.session_state.get("validator_qr_image_hash")

            if img_hash != last_processed_hash:
                with st.spinner("🔍 Lecture du QR code..."):
                    try:
                        order = read_qr_order(qr_image)
                        st.session_state.validator_order = order
                        st.session_state.validator_error = None
                        st.session_state.validator_qr_image_hash = img_hash
                        st.session_state.validator_step = 2
                        st.rerun()
                    except ValueError as e:
                        st.session_state.validator_error = str(e)
                        st.error(f"❌ QR code non reconnu: {e}")
                        st.session_state.validator_qr_image_hash = img_hash  # Mark as processed to avoid retry loop
        elif st.session_state.get("validator_error"):
            st.error(f"❌ {st.session_state.validator_error}")

    elif st.session_state.validator_step == 2:
        st.markdown(
            '<div style="text-align: center; font-size: 36px; font-weight: bold; margin: 20px 0;">📸 Image de la commande</div>',
            unsafe_allow_html=True,
        )

        if st.button("← RETOUR", width="stretch", help="Retourner à l'étape 1 pour scanner un nouveau QR code"):
            st.session_state.validator_step = 1
            st.session_state.validator_order = None
            st.rerun()

        st.divider()

        if "validator_order" in st.session_state and st.session_state.validator_order:
            render_order_details(st.session_state.validator_order)
            st.divider()

        bag_image = render_bag_image_input(key_prefix="validator", title="")

        if bag_image:
            img_bytes = io.BytesIO()
            bag_image.save(img_bytes, format="PNG")
            img_hash = hashlib.md5(img_bytes.getvalue(), usedforsecurity=False).hexdigest()  # nosec B324
            last_processed_hash = st.session_state.get("validator_bag_image_hash")

            if img_hash != last_processed_hash:
                st.session_state.validator_bag_image = bag_image
                with st.spinner("🔍 Extraction de la commande en cours..."):
                    expected_order = st.session_state.validator_order
                    try:
                        detected_order = predict_order(bag_image, expected_order=expected_order)
                        st.session_state.validator_detected_order = detected_order
                        st.session_state.validator_bag_image_hash = img_hash
                        st.session_state.validator_step = 3
                        st.rerun()
                    except MissingCredentialsError:
                        st.warning(
                            "⚠️ **API Key manquante** : Veuillez configurer la clé API pour Image Intelligence "
                            "dans la barre latérale (section ⚙️ Celeste AI config) ou définir la variable "
                            "d'environnement pour le fournisseur."
                        )
                        st.stop()

    elif st.session_state.validator_step == 3:
        st.markdown(
            '<div style="text-align: center; font-size: 36px; font-weight: bold; margin: 20px 0;">✅ Résultat de la validation</div>',
            unsafe_allow_html=True,
        )

        if st.button("← RETOUR", width="stretch", help="Retourner à l'étape 2 pour reprendre une photo"):
            st.session_state.validator_step = 2
            st.session_state.validator_detected_order = None
            st.rerun()

        st.divider()

        if "validator_detected_order" in st.session_state and st.session_state.validator_detected_order:
            comparison_result = compare_orders(
                st.session_state.validator_order,
                st.session_state.validator_detected_order,
            )

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
                    st.warning(f"⚠️ Impossible de sauvegarder le résultat: {e}")

            render_validation_result(
                is_complete=comparison_result.is_complete,
                comparison_result=comparison_result,
                expected_order=st.session_state.validator_order,
                detected_order=st.session_state.validator_detected_order,
            )

            st.divider()

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### 📸 Image de la commande")
                if "validator_bag_image" in st.session_state and st.session_state.validator_bag_image:
                    st.image(
                        st.session_state.validator_bag_image,
                        caption="Image de la commande",
                        width="stretch",
                    )

            with col2:
                if "validator_order" in st.session_state and st.session_state.validator_order:
                    render_order_details(st.session_state.validator_order)

            st.divider()

            with st.expander("📊 Voir la comparaison détaillée", expanded=True):
                render_order_comparison(
                    st.session_state.validator_order,
                    st.session_state.validator_detected_order,
                )

        st.divider()
        if st.button("🔄 Nouvelle validation", type="primary", width="stretch"):
            st.session_state.validator_step = 1
            st.session_state.validator_order = None
            st.session_state.validator_detected_order = None
            st.session_state.validator_bag_image = None
            st.session_state.validator_error = None
            st.session_state.validator_saved = False
            st.session_state.validator_qr_image_hash = None
            st.session_state.validator_bag_image_hash = None
            st.rerun()


__all__ = ["render_order_validator"]
