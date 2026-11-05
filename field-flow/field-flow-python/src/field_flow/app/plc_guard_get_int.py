"""单轮先读目标INT；负数才GET，严格解析后交唯一Execution。"""
from field_flow.domain import parse_input


async def once(http, flow, plc, execution, owner):
    sample = await owner.read(flow.id, flow.target.db_number, flow.target.byte_offset)
    if sample.value >= 0:
        return "guard_false"
    incoming = await http.get(flow.get_url)
    intent = parse_input(incoming, flow, plc)
    return "idle" if intent is None else await execution.apply(intent)
