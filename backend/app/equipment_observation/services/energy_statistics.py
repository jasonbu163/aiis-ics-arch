"""基于明确表计配置计算可解释的能耗，缺少连续性证据时不补零。"""
from decimal import Decimal, InvalidOperation


def _missing(reason, latest=None, latest_state="missing"):
    return {"state": "incomplete", "reason": reason, "amount": None, "latest": latest, "latestState": latest_state}


def _value(value):
    if isinstance(value, bool) or value is None:
        return None
    try:
        result = Decimal(str(value))
        return result if result.is_finite() else None
    except (InvalidOperation, ValueError, TypeError):
        return None


def summarize(mode, unit, rows, start, end, rules):
    """rows 为单一表计、单一组、单一指标的已解码原始事件。"""
    if start >= end:
        raise ValueError("invalid interval")
    ordered = sorted(rows, key=lambda row: row["observedAt"])
    latest, latest_state = None, "missing"
    if ordered:
        last_time = ordered[-1]["observedAt"]
        latest_rows = [row for row in ordered if row["observedAt"] == last_time]
        values = [_value(row.get("value")) for row in latest_rows]
        if any(row.get("quality") != "good" for row in latest_rows) or any(value is None for value in values):
            latest_state = "incomplete"
        elif len(set(values)) != 1:
            latest_state = "conflict"
        else:
            latest, latest_state = values[0], "known"
    if mode == "instantaneous":
        return {"state": "reading", "reason": "instantaneous_not_usage", "amount": None,
                "latest": latest, "latestState": latest_state}
    if not unit:
        return _missing("unit_unknown", latest, latest_state)
    if mode == "cumulative":
        samples = [row for row in ordered if start <= row["observedAt"] <= end]
        if not samples or samples[0]["observedAt"] != start or samples[-1]["observedAt"] != end:
            return _missing("boundary_missing", latest, latest_state)
        if not rules.get("continuityConfirmed"):
            return _missing("continuity_unknown", latest, latest_state)
        gap = rules.get("maxGapSeconds")
        if type(gap) is not int or gap <= 0:
            return _missing("gap_rule_unknown", latest, latest_state)
        previous_time, previous_value = None, None
        first = None
        for row in samples:
            value = _value(row.get("value"))
            if row.get("quality") != "good" or value is None:
                return _missing("bad_or_missing_sample", latest, latest_state)
            stamp = row["observedAt"]
            if previous_time is not None:
                if stamp == previous_time and value != previous_value:
                    return _missing("same_time_conflict", latest, latest_state)
                if (stamp - previous_time).total_seconds() > gap:
                    return _missing("sample_gap", latest, latest_state)
                if value < previous_value:
                    return _missing("counter_decreased", latest, latest_state)
            first = value if first is None else first
            previous_time, previous_value = stamp, value
        return {"state": "complete", "reason": None, "amount": previous_value - first,
                "latest": latest, "latestState": latest_state}
    if mode == "interval":
        intervals = [row for row in ordered if row.get("intervalStartAt") is not None
                     and row.get("intervalEndAt") is not None
                     and row["intervalStartAt"] < end and row["intervalEndAt"] > start]
        intervals.sort(key=lambda row: (row["intervalStartAt"], row["intervalEndAt"]))
        cursor, amount = start, Decimal(0)
        for row in intervals:
            left, right = row["intervalStartAt"], row["intervalEndAt"]
            value = _value(row.get("value"))
            if left < start or right > end:
                return _missing("cross_boundary", latest, latest_state)
            if row.get("quality") != "good" or value is None or left >= right:
                return _missing("bad_or_missing_sample", latest, latest_state)
            if left < cursor:
                return _missing("interval_overlap", latest, latest_state)
            if left > cursor:
                return _missing("interval_gap", latest, latest_state)
            cursor, amount = right, amount + value
        if cursor != end:
            return _missing("interval_gap", latest, latest_state)
        return {"state": "complete", "reason": None, "amount": amount, "latest": latest, "latestState": latest_state}
    return _missing("mode_unknown", latest, latest_state)
