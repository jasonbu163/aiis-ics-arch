"""Shared synthetic mapping sample identity; no application imports or database access."""

def identity(**changes):
    return dict(dict(equipmentId="line-A", sampleId="sample-A", sampledAt="2026-10-16T10:00:00.123Z", quality="good"), **changes)
