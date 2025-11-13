"""Dashboard component - displays statistics and charts for validation records."""

import csv
import io
from datetime import datetime, timedelta

import pandas as pd  # type: ignore[import-untyped]
import streamlit as st

from staff_meal.models import ValidationRecord
from staff_meal.storage import get_all_validation_records
from ui.services.statistics import calculate_statistics
from ui.utils import runner


def render_dashboard() -> None:
    """Render statistics dashboard with metrics and charts."""
    st.markdown(
        '<div style="text-align: center; font-size: 48px; font-weight: bold; margin: 20px 0;">📊 Tableau de bord</div>',
        unsafe_allow_html=True,
    )
    st.divider()

    # Date range filter
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        start_date = st.date_input(
            "Date de début",
            value=datetime.now().date() - timedelta(days=30),
            key="dashboard_start_date",
        )
    with col2:
        end_date = st.date_input(
            "Date de fin",
            value=datetime.now().date(),
            key="dashboard_end_date",
        )
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Actualiser", key="dashboard_refresh"):
            st.rerun()

    st.divider()

    # Load validation records
    with st.spinner("Chargement des données..."):
        start_datetime = datetime.combine(start_date, datetime.min.time()) if start_date else None
        end_datetime = datetime.combine(end_date, datetime.max.time()) if end_date else None
        records = runner.run(get_all_validation_records(start_date=start_datetime, end_date=end_datetime))

    if not records:
        st.info("Aucune donnée disponible pour la période sélectionnée.")
        return

    # Calculate statistics
    stats = calculate_statistics(records)

    # Key metrics display
    st.markdown("#### 📈 Métriques principales")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total commandes", stats.total_orders)

    with col2:
        st.metric("Commandes complètes", stats.complete_orders)

    with col3:
        completion_rate = (stats.complete_orders / stats.total_orders * 100) if stats.total_orders > 0 else 0.0
        st.metric("Taux de complétude", f"{completion_rate:.1f}%")

    with col4:
        st.metric("Taux d'erreur", f"{stats.error_rate:.1f}%")

    st.divider()

    # Charts section
    st.markdown("#### 📊 Graphiques")

    # Completion rate over time
    if len(records) > 0:
        # Group by date
        records_by_date: dict[str, list[ValidationRecord]] = {}
        for record in records:
            date_key = record.timestamp.date().isoformat()
            if date_key not in records_by_date:
                records_by_date[date_key] = []
            records_by_date[date_key].append(record)

        # Calculate daily completion rates
        dates = []
        completion_rates = []
        for date_key in sorted(records_by_date.keys()):
            daily_records = records_by_date[date_key]
            daily_stats = calculate_statistics(daily_records)
            dates.append(date_key)
            completion_rate = (
                (daily_stats.complete_orders / daily_stats.total_orders * 100) if daily_stats.total_orders > 0 else 0.0
            )
            completion_rates.append(completion_rate)

        if dates:
            df_completion = pd.DataFrame({"Date": dates, "Taux de complétude (%)": completion_rates})
            st.markdown("**Taux de complétude dans le temps**")
            st.line_chart(df_completion.set_index("Date"))

    # Errors by hour
    if stats.errors_by_hour:
        hours = list(range(24))
        error_counts = [stats.errors_by_hour.get(hour, 0) for hour in hours]
        df_hours = pd.DataFrame({"Heure": hours, "Nombre d'erreurs": error_counts})
        st.markdown("**Erreurs par heure de la journée**")
        st.bar_chart(df_hours.set_index("Heure"))

    # Errors by day
    if stats.errors_by_day:
        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        days = [day for day in day_order if day in stats.errors_by_day]
        error_counts = [stats.errors_by_day.get(day, 0) for day in days]
        df_days = pd.DataFrame({"Jour": days, "Nombre d'erreurs": error_counts})
        st.markdown("**Erreurs par jour de la semaine**")
        st.bar_chart(df_days.set_index("Jour"))

    # Most forgotten items
    if stats.most_forgotten_items:
        st.divider()
        st.markdown("#### 🔴 Articles les plus souvent oubliés")
        items_data = [
            {"Article": item.value, "Nombre d'oublis": count} for item, count in stats.most_forgotten_items[:10]
        ]
        df_items = pd.DataFrame(items_data)
        st.dataframe(df_items, use_container_width=True, hide_index=True)

        # Chart for most forgotten items
        if items_data:
            df_items_chart = pd.DataFrame(items_data)
            st.bar_chart(df_items_chart.set_index("Article"))

    # Export functionality
    st.divider()
    st.markdown("#### 💾 Export des données")

    # Create CSV export
    csv_data = _create_csv_export(records)
    st.download_button(
        label="📥 Télécharger CSV",
        data=csv_data,
        file_name=f"validations_{start_date}_{end_date}.csv",
        mime="text/csv",
        key="dashboard_export_csv",
    )


def _create_csv_export(records: list[ValidationRecord]) -> str:
    """Create CSV export of validation records.

    Args:
        records: List of validation records to export.

    Returns:
        CSV string.
    """
    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow(
        [
            "ID",
            "Order ID",
            "Timestamp",
            "Operator",
            "Is Complete",
            "Expected Items",
            "Detected Items",
            "Missing Items",
            "Too Few Items",
            "Too Many Items",
            "Extra Items",
        ]
    )

    # Data rows
    for record in records:
        expected_items_str = ", ".join([f"{item.quantity}x {item.item.value}" for item in record.expected_order.items])
        detected_items_str = ", ".join([f"{item.quantity}x {item.item.value}" for item in record.detected_order.items])
        missing_items_str = ", ".join(
            [f"{m.expected_quantity}x {m.item.value}" for m in record.comparison_result.missing_items]
        )
        too_few_str = ", ".join(
            [f"{m.expected_quantity}x {m.item.value}" for m in record.comparison_result.too_few_items]
        )
        too_many_str = ", ".join(
            [f"{m.expected_quantity}x {m.item.value}" for m in record.comparison_result.too_many_items]
        )
        extra_items_str = ", ".join(
            [f"{item.quantity}x {item.item.value}" for item in record.comparison_result.extra_items]
        )

        writer.writerow(
            [
                record.id or "",
                record.order_id,
                record.timestamp.isoformat(),
                record.operator or "",
                "Oui" if record.is_complete else "Non",
                expected_items_str,
                detected_items_str,
                missing_items_str,
                too_few_str,
                too_many_str,
                extra_items_str,
            ]
        )

    return output.getvalue()


__all__ = ["render_dashboard"]
