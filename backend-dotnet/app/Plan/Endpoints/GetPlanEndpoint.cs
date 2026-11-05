// ID 不使用路由 int constraint，以便格式和范围错误统一收敛到 422。
using AIIS.Backend.app.Plan.Contracts;
using AIIS.Backend.app.Plan.Services;
using AIIS.Backend.Common.Contracts;
using FastEndpoints;
namespace AIIS.Backend.app.Plan.Endpoints;

public sealed class GetPlanEndpoint(PlanService service) : EndpointWithoutRequest<ApiResponse<PlanOut>>
{
    public override void Configure() { Get("/api/v1/plans/{id}"); AllowAnonymous(); }
    public override async Task HandleAsync(CancellationToken ct)
    {
        int id = PlanQueryIn.Positive(HttpContext.Request.RouteValues["id"]?.ToString(), "id", 0);
        await Send.OkAsync(ApiResponse<PlanOut>.Success(await service.Get(id, ct)), ct);
    }
}
