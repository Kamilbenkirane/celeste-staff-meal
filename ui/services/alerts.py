"""Alert system for dashboard - detect anomalies and threshold breaches."""

from pydantic import BaseModel, Field

from staff_meal.models import Statistics, ValidationRecord


class Alert(BaseModel):
    """Alert information."""

    severity: str = Field(..., description="Alert severity: critical, warning, info")
    title: str = Field(..., description="Alert title")
    message: str = Field(..., description="Alert message")
    emoji: str = Field("⚠️", description="Alert emoji")


def detect_alerts(
    stats: Statistics,
    records: list[ValidationRecord],
    error_threshold: float = 20.0,
    completion_threshold: float = 95.0,
) -> list[Alert]:
    """Detect alerts based on statistics and thresholds.

    Args:
        stats: Current statistics.
        records: List of validation records.
        error_threshold: Error rate threshold for critical alert (default: 20%).
        completion_threshold: Completion rate threshold for warning (default: 95%).

    Returns:
        List of Alert objects.
    """
    alerts: list[Alert] = []

    if not records:
        return alerts

    # Alert: High error rate
    if stats.error_rate > error_threshold:
        alerts.append(
            Alert(
                severity="critical",
                title="🔴 Taux d'erreur critique",
                message=f"Le taux d'erreur est de {stats.error_rate:.1f}%, dépassant le seuil de {error_threshold}%",
                emoji="🔴",
            )
        )

    # Alert: Low completion rate
    completion_rate = (stats.complete_orders / stats.total_orders * 100) if stats.total_orders > 0 else 0.0
    if completion_rate < completion_threshold:
        alerts.append(
            Alert(
                severity="warning",
                title="🟡 Taux de complétude sous objectif",
                message=f"Le taux de complétude est de {completion_rate:.1f}%, en dessous de l'objectif de {completion_threshold}%",
                emoji="🟡",
            )
        )

    # Alert: Spike in errors (compare last 7 days vs previous 7 days)
    if len(records) >= 14:
        recent_records = sorted(records, key=lambda r: r.timestamp, reverse=True)[:7]
        older_records = sorted(records, key=lambda r: r.timestamp, reverse=True)[7:14]

        recent_errors = sum(1 for r in recent_records if not r.is_complete)
        older_errors = sum(1 for r in older_records if not r.is_complete)

        if older_errors > 0:
            error_increase = ((recent_errors - older_errors) / older_errors * 100) if older_errors > 0 else 0.0
            if error_increase > 50:  # 50% increase
                alerts.append(
                    Alert(
                        severity="warning",
                        title="⚠️ Pic d'erreurs détecté",
                        message=f"Augmentation de {error_increase:.0f}% des erreurs sur les 7 derniers jours ({recent_errors} vs {older_errors})",
                        emoji="⚠️",
                    )
                )

    # Alert: Frequently forgotten items
    if stats.most_forgotten_items:
        top_item, top_count = stats.most_forgotten_items[0]
        if top_count >= 5:  # Item forgotten 5+ times
            alerts.append(
                Alert(
                    severity="warning",
                    title="📌 Article fréquemment oublié",
                    message=f"L'article '{top_item.value}' a été oublié {top_count} fois",
                    emoji="📌",
                )
            )

    # Alert: Peak error hours
    if stats.errors_by_hour:
        max_errors = max(stats.errors_by_hour.values())
        peak_hours = [h for h, count in stats.errors_by_hour.items() if count == max_errors and count > 0]
        if peak_hours and max_errors >= 3:
            hours_str = ", ".join([f"{h}h" for h in sorted(peak_hours)])
            alerts.append(
                Alert(
                    severity="info",
                    title="⏰ Heures critiques identifiées",
                    message=f"Pic d'erreurs détecté aux heures: {hours_str} ({max_errors} erreurs)",
                    emoji="⏰",
                )
            )

    return alerts


__all__ = ["Alert", "detect_alerts"]
