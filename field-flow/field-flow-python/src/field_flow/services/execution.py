"""唯一执行服务：身份接纳、typed ACK后的T3及保守失败状态。"""
from field_flow.domain import Failure, require
from field_flow.infrastructure.s7_int_pdu import ValidatedWriteAck


class Execution:
    def __init__(self, state, owner, clock):
        self.state, self.owner, self.clock = state, owner, clock

    async def apply(self, intent):
        require(not self.owner.stopped.is_set(), "canceled")
        require(self.state.healthy, "audit_unhealthy")
        self.clock.check(); intent.validate_time()
        deadline = intent.deadline()
        status = await self.state.admit(intent)
        if status != "pending":
            require(status != "unknown", "target_unknown")
            require(status != "in_flight", "command_in_flight")
            return status
        self.clock.check()
        try:
            proof = await self.owner.submit("write", intent.flow_id, intent.target.db, intent.target.offset, intent, deadline)
            require(isinstance(proof, ValidatedWriteAck), "missing_ack_proof")
            await self.state.finish(intent, "confirmed", "s7_protocol")
            return "confirmed"
        except Failure as exc:
            current = await self.state.status(intent)
            if current == "in_flight":
                await self.state.finish(intent, str(exc) if str(exc) in ("expired", "canceled") else "unknown", str(exc))
            elif current == "pending" and str(exc) in ("expired", "canceled"):
                await self.state.finish(intent, str(exc), str(exc))
            raise
