"""单轮GET与原typed解析；两次业务提前返回后才交Execution。"""
from field_flow.domain import parse_input


async def once(http, flow, plc, execution):
    incoming = await http.get(flow.get_url)
    intent = parse_input(incoming, flow, plc)
    if intent is None:
        return "idle"
    if intent.value <= 0:
        return "guard_false"
    if intent.value > 100:
        return "guard_false"
    return await execution.apply(intent)
