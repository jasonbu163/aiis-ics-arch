"""实时快照和过程历史的事务、去重及持久回执。"""
from ..domain import ObservationError, digest, identifier, reject, sampled_time, scalar, task_no, wire_time
from ..profile import permitted


def _fields(value, required, allowed):
    if not isinstance(value, dict) or not required.issubset(value) or not set(value).issubset(allowed):
        reject()


def normalize(document, producer, target):
    outer = {"contractVersion", "producerId", "eventId", "mappingId", "mappingRevision", "sourceRefs", "data"}
    _fields(document, {"sourceRefs", "data"}, outer)
    if any(value is None for key, value in document.items() if key != "data"):
        reject()
    if producer["kind"] == "sma" and set(document) != outer:
        reject()
    if document.get("contractVersion", "aiis.metric-ingest/v1") != "aiis.metric-ingest/v1":
        reject("contract_version")
    if document.get("producerId", producer["producerId"]) != producer["producerId"]:
        reject("forbidden", 403)
    pair_present = ("mappingId" in document, "mappingRevision" in document)
    if pair_present[0] != pair_present[1]:
        reject()
    if pair_present[0]:
        identifier(document["mappingId"])
        identifier(document["mappingRevision"], 32)
    data = document["data"]
    allowed_data = {"equipmentId", "groupKey", "taskNo", "sampledAt", "quality", "values"}
    required_data = {"taskNo", "sampledAt", "values"}
    if producer["kind"] == "sma":
        required_data = allowed_data
    _fields(data, required_data, allowed_data)
    if any(value is None for key, value in data.items() if key != "quality"):
        reject()
    if producer["kind"] == "sma" and data.get("quality") is None:
        reject("quality")
    pairs = {(grant["equipmentId"], grant["groupKey"]) for grant in producer["grants"]}
    if "equipmentId" not in data or "groupKey" not in data:
        if producer["kind"] != "external" or len(pairs) != 1:
            reject()
        fixed_equipment, fixed_group = next(iter(pairs))
    else:
        fixed_equipment = fixed_group = None
    equipment = identifier(data.get("equipmentId", fixed_equipment))
    group = identifier(data.get("groupKey", fixed_group))
    allow = permitted(producer, equipment, group, target)
    quality = data.get("quality")
    if quality is None and target == "latest" and producer["kind"] == "external":
        quality = "unknown"
    if quality not in ("good", "bad", "unknown") or target == "history" and quality != "good":
        reject("quality")
    values = data["values"]
    if not isinstance(values, dict) or not 1 <= len(values) <= 100:
        reject("values")
    for key, value in values.items():
        identifier(key)
        if value is None:
            reject("values")
    refs = document["sourceRefs"]
    if not isinstance(refs, list) or not 1 <= len(refs) <= 128:
        reject("source_refs")
    refs = [dict(ref) if isinstance(ref, dict) else reject("source_refs") for ref in refs]
    if producer["kind"] == "external":
        if len(refs) != 1:
            reject("source_refs")
        ref = refs[0]
        _fields(ref, {"kind", "sourceEventId"}, {"kind", "sourceId", "sourceEventId", "observedAt"})
        if ref["kind"] != "external_event" or any(v is None for v in ref.values()):
            reject("source_refs")
        if ref.get("sourceId", producer["sourceId"]) != producer["sourceId"]:
            reject("forbidden", 403)
        ref["sourceId"] = identifier(producer["sourceId"], 128)
        identifier(ref["sourceEventId"], 128)
        if "observedAt" in ref:
            sampled_time(ref["observedAt"])
        source_key = [ref["sourceId"], ref["sourceEventId"]]
    else:
        allowed_ref = {"kind", "instanceId", "plcId", "sampleId", "pointId", "sourceGeneration", "configRevision", "observedAt"}
        required_ref = {"kind", "instanceId", "plcId", "sampleId", "pointId"}
        for ref in refs:
            _fields(ref, required_ref, allowed_ref)
            if ref["kind"] != "plc_fact" or any(v is None for v in ref.values()):
                reject("source_refs")
            for key, value in ref.items():
                if key not in ("kind", "observedAt"):
                    identifier(value, 128)
            if "observedAt" in ref:
                sampled_time(ref["observedAt"])
        if len({(r["instanceId"], r["plcId"], r["sampleId"]) for r in refs}) != 1:
            reject("source_refs")
        if len({(r["instanceId"], r["plcId"], r["sampleId"], r["pointId"]) for r in refs}) != len(refs):
            reject("source_refs")
        source_key = [refs[0]["instanceId"], refs[0]["plcId"], refs[0]["sampleId"]]
    event = document.get("eventId")
    if event is None:
        event = "auto-" + digest([producer["producerId"], equipment, group, source_key, target]).hex()
    identifier(event, 128)
    stamp = sampled_time(data["sampledAt"])
    return {"target": target, "producerId": producer["producerId"], "eventId": event,
            "mappingId": document.get("mappingId"), "mappingRevision": document.get("mappingRevision"),
            "sourceRefs": refs, "sourceKey": digest(source_key), "equipmentId": equipment,
            "groupKey": group, "taskNo": task_no(data["taskNo"]), "sampledAt": stamp,
            "quality": quality, "values": values, "allowed": allow}


def fingerprint(data):
    return digest({key: wire_time(value) if key == "sampledAt" else value
                   for key, value in data.items() if key not in {"allowed", "sourceKey"}})


def receipt_data(receipt):
    return {"target": receipt.target, "producerId": receipt.producer_id, "eventId": receipt.event_id,
            "outcome": receipt.outcome, "recordId": str(receipt.result_record_id) if receipt.result_record_id else None}

