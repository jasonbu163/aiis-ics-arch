"""单轮GET→严格typed条件→执行服务；无调度、SQL或PLC协议调用。"""
from field_flow.domain import parse_input


async def once(http, flow, plc, execution):
    incoming = await http.get(flow.get_url)
    intent = parse_input(incoming, flow, plc)
    return "idle" if intent is None else await execution.apply(intent)
