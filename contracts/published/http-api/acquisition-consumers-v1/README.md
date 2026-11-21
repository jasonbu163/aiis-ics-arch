# Acquisition Consumers v1

A consumer reads committed samples for one PLC/DB in stable stream order. The API manages the starting position, run state, lease, pending delivery and ACK. The authorized client sends the target POST. Point data stays in the acquisition facts tables.

[OpenAPI](openapi.json) · [JSON Schema](schema.json) · [Acceptance vectors](vectors.json) · [Sample POST and receipt](../plc-facts-v2/README.md) · [中文](README.zh-CN.md)

## Request sequence

1. Create the consumer with `PUT /api/v1/acquisition-consumers/{consumerId}`, binding one source and a dedicated `external` target. `now` starts after the creation watermark. `retained` also includes backfilled events that were unexpired at creation. A repeat creation returns the original starting position.
2. Set `run-state` to `running` and acquire a lease. Renew, release and progress requests use the `X-Consumer-Lease-Id` and `X-Consumer-Lease-Generation` headers. `next` returns one event or `empty` without advancing the cursor.
3. Persist `pending/{deliveryId}` with the frozen configuration and serializer versions, target identity and exact POST body SHA-256. The bound target POST requires the service Bearer, both lease headers, `X-Consumer-Id` and `X-Delivery-Id`. Its `sampleId` is the delivery ID and its `sourceSeq` is the event sequence.
4. After a matching `committed/created` or `committed/duplicate` receipt, submit an ACK. The ACK and progress update share one transaction. Read consumer state after a restart. Retry a lost POST receipt with the identical identity and body bytes while source registration and sample retention allow it.
5. On `503 acquisition_consumer.commit_outcome_unknown`, read state and replay the original mutation. Creation and pending use the consumer and delivery IDs respectively. Keep the same `operationId` and input for other mutations. A stale lease cannot submit a new bound target write or advance progress. A duplicate successful ACK may return its previous result.
6. `410 acquisition_consumer.gap` means the required fact expired or cannot be read. Error `data` includes `eventSeq` and `lastConfirmedSeq`. Keep the cursor at its confirmed position.

The service Bearer grants a precise consumer, source and set of operations. Bound target streams additionally require fenced, digest-checked writes. Unbound v2 endpoints retain their development contract. The v1 target adapter covers a same-backend `plc-facts-v2` target. The consumer stores only delivery metadata, version identifiers and request fingerprints. The client retains the frozen configuration needed to reconstruct the body.
