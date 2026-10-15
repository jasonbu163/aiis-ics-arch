"""
File Path: /backend/app/performance/domain.py
Description: Pure rules for PLC-observed production records.
Main Features:
    - Classifies raw coil values into stable observation states
    - Normalizes numeric coil identifiers without losing string identities
"""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from math import isfinite

from common.data_keys import PerformanceDurationSource, PerformanceObservationStatus


@dataclass(frozen=True)
class CoilObservation:
    """A normalized coil observation without persistence concerns."""

    status: PerformanceObservationStatus
    coil_no: str | None


@dataclass(frozen=True)
class PerformanceDuration:
    """Derived duration value and its stable source key."""

    seconds: int | None
    source: PerformanceDurationSource


class InvalidPerformanceTimeRange(ValueError):
    """Raised when manual production times would create a negative duration."""


def classify_coil_no(value: object) -> CoilObservation:
    """Classify a decoded PLC coil value using the B6.1 observation contract."""
    if isinstance(value, bool) or value is None:
        return CoilObservation(PerformanceObservationStatus.UNKNOWN, None)

    if isinstance(value, str):
        coil_no = value.strip()
        if not coil_no:
            return CoilObservation(PerformanceObservationStatus.NOT_IN_PRODUCTION, None)
        return CoilObservation(PerformanceObservationStatus.IN_PRODUCTION, coil_no)

    if isinstance(value, Decimal):
        return _classify_decimal(value)

    if isinstance(value, int):
        return _classify_decimal(Decimal(value))

    if isinstance(value, float):
        if not isfinite(value):
            return CoilObservation(PerformanceObservationStatus.UNKNOWN, None)
        return _classify_decimal(Decimal(str(value)))

    return CoilObservation(PerformanceObservationStatus.UNKNOWN, None)


def normalize_parent_coil_no(coil_no: str, parent_coil_no: str | None) -> str:
    """Keep root records self-referential while preserving child coil ancestry."""
    return parent_coil_no if parent_coil_no and parent_coil_no.strip() else coil_no


def derive_performance_duration(
    *,
    start_time: datetime | None,
    end_time: datetime | None,
    first_observed_at: datetime | None,
    last_observed_at: datetime | None,
) -> PerformanceDuration:
    """Derive total duration using manual time first, then PLC observation time."""
    if start_time is not None and end_time is not None:
        if end_time < start_time:
            raise InvalidPerformanceTimeRange("performance_invalid_time_range")
        return PerformanceDuration(
            seconds=int((end_time - start_time).total_seconds()),
            source=PerformanceDurationSource.MANUAL_TIME,
        )

    if first_observed_at is not None and last_observed_at is not None:
        if last_observed_at < first_observed_at:
            return PerformanceDuration(None, PerformanceDurationSource.UNAVAILABLE)
        return PerformanceDuration(
            seconds=int((last_observed_at - first_observed_at).total_seconds()),
            source=PerformanceDurationSource.PLC_OBSERVED,
        )

    return PerformanceDuration(None, PerformanceDurationSource.UNAVAILABLE)


def apply_performance_duration(performance: object) -> None:
    """Write derived duration fields onto a Performance-like object."""
    duration = derive_performance_duration(
        start_time=getattr(performance, "start_time", None),
        end_time=getattr(performance, "end_time", None),
        first_observed_at=getattr(performance, "first_observed_at", None),
        last_observed_at=getattr(performance, "last_observed_at", None),
    )
    setattr(performance, "total_duration_seconds", duration.seconds)
    setattr(performance, "total_duration_source", duration.source.value)


def _classify_decimal(value: Decimal) -> CoilObservation:
    if not value.is_finite() or value < 0:
        return CoilObservation(PerformanceObservationStatus.UNKNOWN, None)
    if value == 0:
        return CoilObservation(PerformanceObservationStatus.NOT_IN_PRODUCTION, None)

    try:
        normalized = format(value.normalize(), "f")
    except InvalidOperation:
        return CoilObservation(PerformanceObservationStatus.UNKNOWN, None)

    return CoilObservation(PerformanceObservationStatus.IN_PRODUCTION, normalized)
