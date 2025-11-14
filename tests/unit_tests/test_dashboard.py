"""Tests for dashboard component."""

from datetime import datetime
from unittest.mock import MagicMock, patch

from staff_meal.models import (
    ComparisonResult,
    Item,
    ItemMatch,
    ItemMismatch,
    Order,
    OrderItem,
    OrderSource,
    Statistics,
    ValidationRecord,
)
from ui.components.dashboard import (
    _create_csv_export,
    _render_error_analysis_charts,
    _render_formatted_insights,
    _render_item_analysis_charts,
    _render_trend_charts,
)
from ui.services.statistics import calculate_statistics


class TestRenderFormattedInsights:
    """Tests for _render_formatted_insights function."""

    @patch("ui.components.dashboard.st.error")
    @patch("ui.components.dashboard.st.warning")
    @patch("ui.components.dashboard.st.success")
    @patch("ui.components.dashboard.st.info")
    @patch("ui.components.dashboard.st.markdown")
    def test_parse_critical_recommendation(
        self,
        mock_markdown: MagicMock,
        mock_info: MagicMock,
        mock_success: MagicMock,
        mock_warning: MagicMock,
        mock_error: MagicMock,
    ) -> None:
        """Parse and render critical recommendation."""
        insights = "🔴 CRITIQUE: Sauce oubliée 15x → Former équipe 12h-14h"
        _render_formatted_insights(insights)

        mock_error.assert_called_once_with(insights)
        mock_warning.assert_not_called()
        mock_success.assert_not_called()

    @patch("ui.components.dashboard.st.error")
    @patch("ui.components.dashboard.st.warning")
    @patch("ui.components.dashboard.st.success")
    @patch("ui.components.dashboard.st.info")
    @patch("ui.components.dashboard.st.markdown")
    def test_parse_warning_recommendation(
        self,
        mock_markdown: MagicMock,
        mock_info: MagicMock,
        mock_success: MagicMock,
        mock_warning: MagicMock,
        mock_error: MagicMock,
    ) -> None:
        """Parse and render warning recommendation."""
        insights = "🟡 ATTENTION: Pic d'erreurs le vendredi"
        _render_formatted_insights(insights)

        mock_warning.assert_called_once_with(insights)
        mock_error.assert_not_called()

    @patch("ui.components.dashboard.st.error")
    @patch("ui.components.dashboard.st.warning")
    @patch("ui.components.dashboard.st.success")
    @patch("ui.components.dashboard.st.info")
    @patch("ui.components.dashboard.st.markdown")
    def test_parse_multiple_recommendations(
        self,
        mock_markdown: MagicMock,
        mock_info: MagicMock,
        mock_success: MagicMock,
        mock_warning: MagicMock,
        mock_error: MagicMock,
    ) -> None:
        """Parse and render multiple recommendations."""
        insights = """🔴 CRITIQUE: Sauce oubliée 15x
🟡 ATTENTION: Pic d'erreurs vendredi
💡 ACTION: Vérifier processus"""
        _render_formatted_insights(insights)

        assert mock_error.call_count == 1
        assert mock_warning.call_count == 1
        assert mock_info.call_count == 1

    @patch("ui.components.dashboard.st.error")
    @patch("ui.components.dashboard.st.warning")
    @patch("ui.components.dashboard.st.success")
    @patch("ui.components.dashboard.st.info")
    @patch("ui.components.dashboard.st.markdown")
    def test_parse_recommendation_with_multiline(
        self,
        mock_markdown: MagicMock,
        mock_info: MagicMock,
        mock_success: MagicMock,
        mock_warning: MagicMock,
        mock_error: MagicMock,
    ) -> None:
        """Parse recommendation with multiline text."""
        insights = """🔴 CRITIQUE: Sauce oubliée 15x
→ Former équipe 12h-14h
→ Réviser checklist"""
        _render_formatted_insights(insights)

        mock_error.assert_called_once()
        call_args = mock_error.call_args[0][0]
        assert "Sauce oubliée" in call_args
        assert "Former équipe" in call_args

    @patch("ui.components.dashboard.st.error")
    @patch("ui.components.dashboard.st.warning")
    @patch("ui.components.dashboard.st.success")
    @patch("ui.components.dashboard.st.info")
    @patch("ui.components.dashboard.st.markdown")
    def test_parse_empty_insights(
        self,
        mock_markdown: MagicMock,
        mock_info: MagicMock,
        mock_success: MagicMock,
        mock_warning: MagicMock,
        mock_error: MagicMock,
    ) -> None:
        """Handle empty insights gracefully."""
        _render_formatted_insights("")

        mock_error.assert_not_called()
        mock_warning.assert_not_called()


class TestRenderTrendCharts:
    """Tests for _render_trend_charts function."""

    def _create_mock_record(
        self,
        order_id: str,
        is_complete: bool = True,
        date_offset: int = 0,
    ) -> ValidationRecord:
        """Create a mock ValidationRecord."""
        expected_order = Order(
            order_id=order_id,
            source=OrderSource.UBER_EATS,
            items=[OrderItem(item=Item.GYOZA, quantity=2)],
        )
        detected_order = Order(
            order_id=order_id,
            source=OrderSource.UBER_EATS,
            items=[OrderItem(item=Item.GYOZA, quantity=2)],
        )

        comparison_result = ComparisonResult(
            is_complete=is_complete,
            missing_items=[],
            too_few_items=[],
            too_many_items=[],
            extra_items=[],
            matched_items=[
                ItemMatch(
                    item=Item.GYOZA,
                    expected_quantity=2,
                    detected_quantity=2,
                    is_match=is_complete,
                )
            ],
        )

        timestamp = datetime(2024, 1, 15 + date_offset, 12, 0, 0)

        return ValidationRecord(
            id=1,
            order_id=order_id,
            timestamp=timestamp,
            operator="test_operator",
            is_complete=is_complete,
            expected_order=expected_order,
            detected_order=detected_order,
            comparison_result=comparison_result,
        )

    @patch("ui.components.dashboard.st.plotly_chart")
    @patch("ui.components.dashboard.st.info")
    def test_render_trend_charts_with_data(
        self,
        mock_info: MagicMock,
        mock_plotly: MagicMock,
    ) -> None:
        """Render trend charts with validation records."""
        records = [
            self._create_mock_record("ORD-1", is_complete=True, date_offset=0),
            self._create_mock_record("ORD-2", is_complete=False, date_offset=1),
            self._create_mock_record("ORD-3", is_complete=True, date_offset=2),
        ]

        stats = Statistics(
            total_orders=3,
            complete_orders=2,
            error_rate=33.3,
            most_forgotten_items=[],
            errors_by_hour={},
            errors_by_day={},
        )

        _render_trend_charts(records, stats)

        mock_info.assert_not_called()
        assert mock_plotly.call_count == 2  # Completion rate + error count

    @patch("ui.components.dashboard.st.info")
    def test_render_trend_charts_empty_records(
        self,
        mock_info: MagicMock,
    ) -> None:
        """Handle empty records gracefully."""
        stats = Statistics(
            total_orders=0,
            complete_orders=0,
            error_rate=0.0,
            most_forgotten_items=[],
            errors_by_hour={},
            errors_by_day={},
        )

        _render_trend_charts([], stats)

        mock_info.assert_called_once_with("Aucune donnée pour afficher les tendances.")


class TestRenderErrorAnalysisCharts:
    """Tests for _render_error_analysis_charts function."""

    def _create_mock_record_with_errors(
        self,
        order_id: str,
        missing_items: list[ItemMismatch] | None = None,
        too_few_items: list[ItemMismatch] | None = None,
        hour: int = 12,
    ) -> ValidationRecord:
        """Create a mock ValidationRecord with errors."""
        expected_order = Order(
            order_id=order_id,
            source=OrderSource.UBER_EATS,
            items=[OrderItem(item=Item.GYOZA, quantity=2)],
        )
        detected_order = Order(
            order_id=order_id,
            source=OrderSource.UBER_EATS,
            items=[OrderItem(item=Item.GYOZA, quantity=1)],
        )

        comparison_result = ComparisonResult(
            is_complete=False,
            missing_items=missing_items or [],
            too_few_items=too_few_items or [],
            too_many_items=[],
            extra_items=[],
            matched_items=[],
        )

        timestamp = datetime(2024, 1, 15, hour, 0, 0)

        return ValidationRecord(
            id=1,
            order_id=order_id,
            timestamp=timestamp,
            operator="test_operator",
            is_complete=False,
            expected_order=expected_order,
            detected_order=detected_order,
            comparison_result=comparison_result,
        )

    @patch("ui.components.dashboard.st.plotly_chart")
    def test_render_error_analysis_with_pie_chart(
        self,
        mock_plotly: MagicMock,
    ) -> None:
        """Render error analysis with pie chart."""
        records = [
            self._create_mock_record_with_errors(
                "ORD-1",
                missing_items=[
                    ItemMismatch(
                        item=Item.SAUCE, expected_quantity=1, detected_quantity=0
                    )
                ],
            ),
            self._create_mock_record_with_errors(
                "ORD-2",
                too_few_items=[
                    ItemMismatch(
                        item=Item.GYOZA, expected_quantity=2, detected_quantity=1
                    )
                ],
            ),
        ]

        stats = Statistics(
            total_orders=2,
            complete_orders=0,
            error_rate=100.0,
            most_forgotten_items=[(Item.SAUCE, 1)],
            errors_by_hour={12: 2},
            errors_by_day={"Monday": 2},
        )

        _render_error_analysis_charts(records, stats)

        # Should render pie chart, heatmap, and bar charts
        assert mock_plotly.call_count >= 3

    @patch("ui.components.dashboard.st.plotly_chart")
    def test_render_error_analysis_heatmap(
        self,
        mock_plotly: MagicMock,
    ) -> None:
        """Render heatmap for errors by day and hour."""
        records = [
            self._create_mock_record_with_errors("ORD-1", hour=12),
            self._create_mock_record_with_errors("ORD-2", hour=14),
            self._create_mock_record_with_errors("ORD-3", hour=12),
        ]

        stats = Statistics(
            total_orders=3,
            complete_orders=0,
            error_rate=100.0,
            most_forgotten_items=[],
            errors_by_hour={12: 2, 14: 1},
            errors_by_day={"Monday": 3},
        )

        _render_error_analysis_charts(records, stats)

        # Verify heatmap was rendered
        assert mock_plotly.call_count >= 3


class TestRenderItemAnalysisCharts:
    """Tests for _render_item_analysis_charts function."""

    @patch("ui.components.dashboard.st.dataframe")
    @patch("ui.components.dashboard.st.plotly_chart")
    @patch("ui.components.dashboard.st.markdown")
    @patch("ui.components.dashboard.st.info")
    def test_render_item_analysis_with_items(
        self,
        mock_info: MagicMock,
        mock_markdown: MagicMock,
        mock_plotly: MagicMock,
        mock_dataframe: MagicMock,
    ) -> None:
        """Render item analysis with forgotten items."""
        stats = Statistics(
            total_orders=10,
            complete_orders=8,
            error_rate=20.0,
            most_forgotten_items=[
                (Item.SAUCE, 5),
                (Item.GYOZA, 3),
                (Item.MAKI_CALIFORNIA, 2),
            ],
            errors_by_hour={},
            errors_by_day={},
        )

        _render_item_analysis_charts(stats)

        mock_info.assert_not_called()
        mock_plotly.assert_called_once()
        mock_dataframe.assert_called_once()

    @patch("ui.components.dashboard.st.info")
    def test_render_item_analysis_no_items(
        self,
        mock_info: MagicMock,
    ) -> None:
        """Handle case with no forgotten items."""
        stats = Statistics(
            total_orders=10,
            complete_orders=10,
            error_rate=0.0,
            most_forgotten_items=[],
            errors_by_hour={},
            errors_by_day={},
        )

        _render_item_analysis_charts(stats)

        mock_info.assert_called_once_with("Aucun article oublié détecté.")


class TestCreateCsvExport:
    """Tests for _create_csv_export function."""

    def test_create_csv_export_complete_order(self) -> None:
        """Create CSV export for complete order."""
        record = ValidationRecord(
            id=1,
            order_id="ORD-123",
            timestamp=datetime(2024, 1, 15, 12, 0, 0),
            operator="Alice",
            is_complete=True,
            expected_order=Order(
                order_id="ORD-123",
                source=OrderSource.UBER_EATS,
                items=[OrderItem(item=Item.GYOZA, quantity=2)],
            ),
            detected_order=Order(
                order_id="ORD-123",
                source=OrderSource.UBER_EATS,
                items=[OrderItem(item=Item.GYOZA, quantity=2)],
            ),
            comparison_result=ComparisonResult(
                is_complete=True,
                missing_items=[],
                too_few_items=[],
                too_many_items=[],
                extra_items=[],
                matched_items=[],
            ),
        )

        stats = calculate_statistics([record])
        csv_data = _create_csv_export([record], stats)

        assert "ORD-123" in csv_data
        assert "Alice" in csv_data
        assert "Oui" in csv_data  # is_complete = True

    def test_create_csv_export_with_errors(self) -> None:
        """Create CSV export for order with errors."""
        record = ValidationRecord(
            id=1,
            order_id="ORD-456",
            timestamp=datetime(2024, 1, 15, 12, 0, 0),
            operator="Bob",
            is_complete=False,
            expected_order=Order(
                order_id="ORD-456",
                source=OrderSource.DELIVEROO,
                items=[
                    OrderItem(item=Item.GYOZA, quantity=2),
                    OrderItem(item=Item.SAUCE, quantity=1),
                ],
            ),
            detected_order=Order(
                order_id="ORD-456",
                source=OrderSource.DELIVEROO,
                items=[OrderItem(item=Item.GYOZA, quantity=1)],
            ),
            comparison_result=ComparisonResult(
                is_complete=False,
                missing_items=[
                    ItemMismatch(
                        item=Item.SAUCE, expected_quantity=1, detected_quantity=0
                    )
                ],
                too_few_items=[
                    ItemMismatch(
                        item=Item.GYOZA, expected_quantity=2, detected_quantity=1
                    )
                ],
                too_many_items=[],
                extra_items=[],
                matched_items=[],
            ),
        )

        stats = calculate_statistics([record])
        csv_data = _create_csv_export([record], stats)

        assert "ORD-456" in csv_data
        assert "Bob" in csv_data
        assert "Non" in csv_data  # is_complete = False
        assert "Sauce" in csv_data
        assert "Gyoza" in csv_data

    def test_create_csv_export_multiple_records(self) -> None:
        """Create CSV export with multiple records."""
        records = [
            ValidationRecord(
                id=i,
                order_id=f"ORD-{i}",
                timestamp=datetime(2024, 1, 15, 12, i, 0),
                operator="Alice",
                is_complete=True,
                expected_order=Order(
                    order_id=f"ORD-{i}",
                    source=OrderSource.UBER_EATS,
                    items=[OrderItem(item=Item.GYOZA, quantity=1)],
                ),
                detected_order=Order(
                    order_id=f"ORD-{i}",
                    source=OrderSource.UBER_EATS,
                    items=[OrderItem(item=Item.GYOZA, quantity=1)],
                ),
                comparison_result=ComparisonResult(
                    is_complete=True,
                    missing_items=[],
                    too_few_items=[],
                    too_many_items=[],
                    extra_items=[],
                    matched_items=[],
                ),
            )
            for i in range(3)
        ]

        stats = calculate_statistics(records)
        csv_data = _create_csv_export(records, stats)

        # Should have header + 3 data rows + summary section
        lines = csv_data.strip().split("\n")
        assert len(lines) >= 4  # At least header + 3 data rows
        assert "ORD-0" in csv_data
        assert "ORD-1" in csv_data
        assert "ORD-2" in csv_data
        assert "RÉSUMÉ" in csv_data  # Summary section should be present
