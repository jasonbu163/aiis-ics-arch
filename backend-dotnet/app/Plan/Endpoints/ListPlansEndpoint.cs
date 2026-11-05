// 分页与过滤入参解析后交 Service，Endpoint 不访问数据库。
using AIIS.Backend.app.Plan.Contracts;
using AIIS.Backend.app.Plan.Services;
using AIIS.Backend.Common.Contracts;
using FastEndpoints;
namespace AIIS.Backend.app.Plan.Endpoints;

public sealed class ListPlansEndpoint(PlanService service) : EndpointWithoutRequest<ApiResponse<PlanPageOut>>
{
    public override void Configure() { Get("/api/v1/plans"); AllowAnonymous(); }
    public override async Task HandleAsync(CancellationToken ct) => await Send.OkAsync(ApiResponse<PlanPageOut>.Success(await service.List(PlanQueryIn.Parse(HttpContext.Request.Query), ct)), ct);
}
