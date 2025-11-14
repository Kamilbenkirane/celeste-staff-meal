"""Tests for validation explanation service."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from staff_meal.models import (
    ComparisonResult,
    Item,
    ItemMatch,
    ItemMismatch,
    Language,
    Order,
    OrderItem,
    OrderSource,
    Statistics,
    ValidationRecord,
)
from ui.services.explanation import (
    generate_dashboard_insights,
    generate_dashboard_insights_sync,
    generate_validation_explanation,
    generate_validation_explanation_async,
)


class TestGenerateValidationExplanationAsync:
    """Tests for generate_validation_explanation_async function."""

    @pytest.mark.asyncio
    async def test_generate_explanation_complete_order(self) -> None:
        """Generate explanation for complete order."""
        expected_order = Order(
            order_id="ORD-123",
            source=OrderSource.UBER_EATS,
            items=[OrderItem(item=Item.GYOZA, quantity=2)],
        )

        detected_order = Order(
            order_id="ORD-123",
            source=OrderSource.UBER_EATS,
            items=[OrderItem(item=Item.GYOZA, quantity=2)],
        )

        mock_output = MagicMock()
        mock_output.content = (
            "La commande est complète. Tous les articles sont présents."
        )

        mock_client = MagicMock()
        mock_client.generate = AsyncMock(return_value=mock_output)

        with patch("ui.services.explanation.create_client", return_value=mock_client):
            result = await generate_validation_explanation_async(
                expected_order, detected_order, Language.FRENCH
            )

        assert result == "La commande est complète. Tous les articles sont présents."
        mock_client.generate.assert_called_once()
        # Verify prompt includes language instruction
        call_args = mock_client.generate.call_args[1]
        assert "Generate the answer in French" in call_args["prompt"]

    @pytest.mark.asyncio
    async def test_generate_explanation_missing_items(self) -> None:
        """Generate explanation for order with missing items."""
        expected_order = Order(
            order_id="ORD-123",
            source=OrderSource.UBER_EATS,
            items=[
                OrderItem(item=Item.GYOZA, quantity=2),
                OrderItem(item=Item.SAUCE, quantity=1),
            ],
        )

        detected_order = Order(
            order_id="ORD-123",
            source=OrderSource.UBER_EATS,
            items=[OrderItem(item=Item.GYOZA, quantity=2)],
        )

        mock_output = MagicMock()
        mock_output.content = "Il manque 1x Sauce dans la commande."

        mock_client = MagicMock()
        mock_client.generate = AsyncMock(return_value=mock_output)

        with patch("ui.services.explanation.create_client", return_value=mock_client):
            result = await generate_validation_explanation_async(
                expected_order, detected_order, Language.FRENCH
            )

        assert "manque" in result.lower() or "missing" in result.lower()
        mock_client.generate.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_explanation_quantity_mismatch(self) -> None:
        """Generate explanation for order with quantity mismatch."""
        expected_order = Order(
            order_id="ORD-123",
            source=OrderSource.UBER_EATS,
            items=[OrderItem(item=Item.GYOZA, quantity=2)],
        )

        detected_order = Order(
            order_id="ORD-123",
            source=OrderSource.UBER_EATS,
            items=[OrderItem(item=Item.GYOZA, quantity=1)],
        )

        mock_output = MagicMock()
        mock_output.content = (
            "Il manque 1x Boite de 4 Gyoza. Quantité attendue: 2, détectée: 1."
        )

        mock_client = MagicMock()
        mock_client.generate = AsyncMock(return_value=mock_output)

        with patch("ui.services.explanation.create_client", return_value=mock_client):
            result = await generate_validation_explanation_async(
                expected_order, detected_order
            )

        assert len(result) > 0
        mock_client.generate.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_explanation_extra_items(self) -> None:
        """Generate explanation for order with extra items."""
        expected_order = Order(
            order_id="ORD-123",
            source=OrderSource.UBER_EATS,
            items=[OrderItem(item=Item.GYOZA, quantity=2)],
        )

        detected_order = Order(
            order_id="ORD-123",
            source=OrderSource.UBER_EATS,
            items=[
                OrderItem(item=Item.GYOZA, quantity=2),
                OrderItem(item=Item.SAUCE, quantity=1),
            ],
        )

        mock_output = MagicMock()
        mock_output.content = (
            "La commande contient un article supplémentaire: 1x Sauce."
        )

        mock_client = MagicMock()
        mock_client.generate = AsyncMock(return_value=mock_output)

        with patch("ui.services.explanation.create_client", return_value=mock_client):
            result = await generate_validation_explanation_async(
                expected_order, detected_order, Language.FRENCH
            )

        assert len(result) > 0
        mock_client.generate.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_explanation_english_language(self) -> None:
        """Generate explanation in English."""
        expected_order = Order(
            order_id="ORD-123",
            source=OrderSource.UBER_EATS,
            items=[OrderItem(item=Item.GYOZA, quantity=2)],
        )

        detected_order = Order(
            order_id="ORD-123",
            source=OrderSource.UBER_EATS,
            items=[OrderItem(item=Item.GYOZA, quantity=2)],
        )

        mock_output = MagicMock()
        mock_output.content = "The order is complete. All items are present."

        mock_client = MagicMock()
        mock_client.generate = AsyncMock(return_value=mock_output)

        with patch("ui.services.explanation.create_client", return_value=mock_client):
            result = await generate_validation_explanation_async(
                expected_order, detected_order, Language.ENGLISH
            )

        assert result == "The order is complete. All items are present."
        mock_client.generate.assert_called_once()
        # Verify prompt includes English language instruction
        call_args = mock_client.generate.call_args[1]
        assert "Generate the answer in English" in call_args["prompt"]

    @pytest.mark.asyncio
    async def test_generate_explanation_spanish_language(self) -> None:
        """Generate explanation in Spanish."""
        expected_order = Order(
            order_id="ORD-123",
            source=OrderSource.UBER_EATS,
            items=[OrderItem(item=Item.GYOZA, quantity=2)],
        )

        detected_order = Order(
            order_id="ORD-123",
            source=OrderSource.UBER_EATS,
            items=[OrderItem(item=Item.GYOZA, quantity=2)],
        )

        mock_output = MagicMock()
        mock_output.content = (
            "El pedido está completo. Todos los artículos están presentes."
        )

        mock_client = MagicMock()
        mock_client.generate = AsyncMock(return_value=mock_output)

        with patch("ui.services.explanation.create_client", return_value=mock_client):
            result = await generate_validation_explanation_async(
                expected_order, detected_order, Language.SPANISH
            )

        assert result == "El pedido está completo. Todos los artículos están presentes."
        mock_client.generate.assert_called_once()
        # Verify prompt includes Spanish language instruction
        call_args = mock_client.generate.call_args[1]
        assert "Generate the answer in Spanish" in call_args["prompt"]

    @pytest.mark.asyncio
    async def test_generate_explanation_default_language(self) -> None:
        """Generate explanation uses French as default language."""
        expected_order = Order(
            order_id="ORD-123",
            source=OrderSource.UBER_EATS,
            items=[OrderItem(item=Item.GYOZA, quantity=2)],
        )

        detected_order = Order(
            order_id="ORD-123",
            source=OrderSource.UBER_EATS,
            items=[OrderItem(item=Item.GYOZA, quantity=2)],
        )

        mock_output = MagicMock()
        mock_output.content = "La commande est complète."

        mock_client = MagicMock()
        mock_client.generate = AsyncMock(return_value=mock_output)

        with patch("ui.services.explanation.create_client", return_value=mock_client):
            # Call without language parameter (should default to French)
            result = await generate_validation_explanation_async(
                expected_order, detected_order
            )

        assert len(result) > 0
        mock_client.generate.assert_called_once()
        # Verify prompt includes French language instruction (default)
        call_args = mock_client.generate.call_args[1]
        assert "Generate the answer in French" in call_args["prompt"]

    @pytest.mark.asyncio
    async def test_generate_explanation_empty_output_raises_error(self) -> None:
        """Generate explanation raises ValueError when output is empty."""
        expected_order = Order(
            order_id="ORD-123",
            source=OrderSource.UBER_EATS,
            items=[OrderItem(item=Item.GYOZA, quantity=2)],
        )

        detected_order = Order(
            order_id="ORD-123",
            source=OrderSource.UBER_EATS,
            items=[OrderItem(item=Item.GYOZA, quantity=2)],
        )

        mock_output = MagicMock()
        mock_output.content = ""

        mock_client = MagicMock()
        mock_client.generate = AsyncMock(return_value=mock_output)

        with (
            patch("ui.services.explanation.create_client", return_value=mock_client),
            pytest.raises(ValueError, match="Failed to generate explanation"),
        ):
            await generate_validation_explanation_async(
                expected_order, detected_order, Language.FRENCH
            )

    @pytest.mark.asyncio
    async def test_generate_explanation_output_without_content_attribute(self) -> None:
        """Generate explanation handles output without content attribute."""
        expected_order = Order(
            order_id="ORD-123",
            source=OrderSource.UBER_EATS,
            items=[OrderItem(item=Item.GYOZA, quantity=2)],
        )

        detected_order = Order(
            order_id="ORD-123",
            source=OrderSource.UBER_EATS,
            items=[OrderItem(item=Item.GYOZA, quantity=2)],
        )

        mock_output = MagicMock()
        del mock_output.content  # Remove content attribute
        mock_output.__str__ = MagicMock(return_value="La commande est complète.")

        mock_client = MagicMock()
        mock_client.generate = AsyncMock(return_value=mock_output)

        with patch("ui.services.explanation.create_client", return_value=mock_client):
            result = await generate_validation_explanation_async(
                expected_order, detected_order, Language.FRENCH
            )

        assert result == "La commande est complète."


class TestGenerateValidationExplanation:
    """Tests for generate_validation_explanation sync wrapper."""

    def test_generate_explanation_sync_wrapper(self) -> None:
        """Sync wrapper calls async function correctly."""
        expected_order = Order(
            order_id="ORD-123",
            source=OrderSource.UBER_EATS,
            items=[OrderItem(item=Item.GYOZA, quantity=2)],
        )

        detected_order = Order(
            order_id="ORD-123",
            source=OrderSource.UBER_EATS,
            items=[OrderItem(item=Item.GYOZA, quantity=2)],
        )

        mock_output = MagicMock()
        mock_output.content = "La commande est complète."

        mock_client = MagicMock()
        mock_client.generate = AsyncMock(return_value=mock_output)

        with (
            patch("ui.services.explanation.create_client", return_value=mock_client),
            patch("ui.utils.runner") as mock_runner,
        ):
            mock_runner.run.return_value = "La commande est complète."
            result = generate_validation_explanation(
                expected_order, detected_order, Language.FRENCH
            )

        assert result == "La commande est complète."
        mock_runner.run.assert_called_once()


class TestGenerateDashboardInsights:
    """Tests for generate_dashboard_insights function."""

    def _create_mock_record(
        self,
        order_id: str,
        is_complete: bool = True,
        missing_items: list[ItemMismatch] | None = None,
        too_few_items: list[ItemMismatch] | None = None,
        hour: int = 12,
    ) -> ValidationRecord:
        """Create a mock ValidationRecord for testing."""
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
            missing_items=missing_items or [],
            too_few_items=too_few_items or [],
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

        timestamp = datetime(2024, 1, 15, hour, 0, 0)

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

    @pytest.mark.asyncio
    async def test_generate_dashboard_insights_with_data(self) -> None:
        """Generate dashboard insights with validation records."""
        records = [
            self._create_mock_record("ORD-1", is_complete=True),
            self._create_mock_record(
                "ORD-2",
                is_complete=False,
                missing_items=[
                    ItemMismatch(
                        item=Item.SAUCE, expected_quantity=1, detected_quantity=0
                    )
                ],
            ),
        ]

        stats = Statistics(
            total_orders=2,
            complete_orders=1,
            error_rate=50.0,
            most_forgotten_items=[(Item.SAUCE, 1)],
            errors_by_hour={12: 1},
            errors_by_day={"Monday": 1},
        )

        mock_output = MagicMock()
        mock_output.content = (
            "- Article Sauce fréquemment oublié\n- Taux d'erreur élevé à 50%"
        )

        mock_client = MagicMock()
        mock_client.generate = AsyncMock(return_value=mock_output)

        with patch("ui.services.explanation.create_client", return_value=mock_client):
            result = await generate_dashboard_insights(stats, records)

        assert len(result) > 0
        assert "Sauce" in result or "erreur" in result.lower()
        mock_client.generate.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_dashboard_insights_empty_records(self) -> None:
        """Generate dashboard insights returns message when no records."""
        stats = Statistics(
            total_orders=0,
            complete_orders=0,
            error_rate=0.0,
            most_forgotten_items=[],
            errors_by_hour={},
            errors_by_day={},
        )

        result = await generate_dashboard_insights(stats, [])

        assert result == "📊 Aucune donnée disponible pour générer des recommandations."

    @pytest.mark.asyncio
    async def test_generate_dashboard_insights_empty_output_raises_error(self) -> None:
        """Generate dashboard insights raises ValueError when output is empty."""
        records = [self._create_mock_record("ORD-1", is_complete=True)]

        stats = Statistics(
            total_orders=1,
            complete_orders=1,
            error_rate=0.0,
            most_forgotten_items=[],
            errors_by_hour={},
            errors_by_day={},
        )

        mock_output = MagicMock()
        mock_output.content = ""

        mock_client = MagicMock()
        mock_client.generate = AsyncMock(return_value=mock_output)

        with (
            patch("ui.services.explanation.create_client", return_value=mock_client),
            pytest.raises(ValueError, match="Failed to generate dashboard insights"),
        ):
            await generate_dashboard_insights(stats, records)

    @pytest.mark.asyncio
    async def test_generate_dashboard_insights_analyzes_error_types(self) -> None:
        """Generate dashboard insights analyzes different error types."""
        records = [
            self._create_mock_record(
                "ORD-1",
                is_complete=False,
                missing_items=[
                    ItemMismatch(
                        item=Item.SAUCE, expected_quantity=1, detected_quantity=0
                    )
                ],
            ),
            self._create_mock_record(
                "ORD-2",
                is_complete=False,
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

        mock_output = MagicMock()
        mock_output.content = "Recommandations basées sur les erreurs détectées."

        mock_client = MagicMock()
        mock_client.generate = AsyncMock(return_value=mock_output)

        with patch("ui.services.explanation.create_client", return_value=mock_client):
            result = await generate_dashboard_insights(stats, records)

        assert len(result) > 0
        # Verify prompt includes error type analysis
        call_args = mock_client.generate.call_args[1]
        prompt_text = call_args["prompt"]
        assert "erreurs" in prompt_text.lower() or "errors" in prompt_text.lower()


class TestGenerateDashboardInsightsSync:
    """Tests for generate_dashboard_insights_sync wrapper."""

    def test_generate_dashboard_insights_sync_wrapper(self) -> None:
        """Sync wrapper calls async function correctly."""
        records = [
            ValidationRecord(
                id=1,
                order_id="ORD-1",
                timestamp=datetime.now(),
                operator="test",
                is_complete=True,
                expected_order=Order(
                    order_id="ORD-1",
                    source=OrderSource.UBER_EATS,
                    items=[OrderItem(item=Item.GYOZA, quantity=1)],
                ),
                detected_order=Order(
                    order_id="ORD-1",
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
        ]

        stats = Statistics(
            total_orders=1,
            complete_orders=1,
            error_rate=0.0,
            most_forgotten_items=[],
            errors_by_hour={},
            errors_by_day={},
        )

        with patch("ui.utils.runner") as mock_runner:
            mock_runner.run.return_value = "Recommandations générées."
            result = generate_dashboard_insights_sync(stats, records)

        assert result == "Recommandations générées."
        mock_runner.run.assert_called_once()
