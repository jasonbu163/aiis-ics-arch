"""复用有界HTTP client；单次GET及整体deadline，不跟随重定向/环境代理。"""
import asyncio
import json
import httpx
from field_flow.domain import Failure, require


class HttpClient:
    def __init__(self, config):
        self.config = config
        self.client = httpx.AsyncClient(trust_env=False, follow_redirects=False,
            limits=httpx.Limits(max_connections=config.max_connections, max_keepalive_connections=config.max_connections),
            timeout=httpx.Timeout(config.total_timeout_ms/1000, connect=config.connect_timeout_ms/1000, pool=config.pool_wait_ms/1000))

    async def get(self, url):
        try:
            async with asyncio.timeout(self.config.total_timeout_ms/1000):
                async with self.client.stream("GET", url) as response:
                    require(response.status_code == 200, "http_status")
                    require(response.headers.get("content-type", "").split(";", 1)[0].strip().lower() == "application/json", "http_content_type")
                    body = bytearray()
                    async for piece in response.aiter_bytes():
                        require(len(body)+len(piece) <= self.config.max_body_bytes, "http_body_size")
                        body.extend(piece)
                    def unique(pairs):
                        result = {}
                        for k, v in pairs:
                            require(k not in result, "input_schema"); result[k] = v
                        return result
                    return json.loads(body.decode("utf-8", errors="strict"), object_pairs_hook=unique,
                                      parse_constant=lambda _: (_ for _ in ()).throw(Failure("input_schema")))
        except (asyncio.TimeoutError, httpx.TimeoutException):
            raise Failure("http_deadline") from None
        except httpx.HTTPError:
            raise Failure("http_error") from None
        except (UnicodeError, ValueError):
            raise Failure("input_schema") from None

    async def close(self):
        await self.client.aclose()
