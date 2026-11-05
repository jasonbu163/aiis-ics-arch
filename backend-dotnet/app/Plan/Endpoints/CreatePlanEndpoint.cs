// 创建入口仅绑定严格 DTO、调用 Service 并返回信封，无 SQL 或事务控制。
using AIIS.Backend.app.Plan.Contracts;
using AIIS.Backend.app.Plan.Services;
using AIIS.Backend.Common.Contracts;
using AIIS.Backend.Common.Serialization;
using FastEndpoints;
namespace AIIS.Backend.app.Plan.Endpoints;

public sealed class CreatePlanEndpoint(PlanService service) : Endpoint<CreatePlanIn, ApiResponse<PlanOut>>
{
    public override void Configure()
    {
        Post("/api/v1/plans"); AllowAnonymous(); RequestBinder(new CreatePlanJson());
        Description(x => x.Accepts<CreatePlanIn>("application/json").Produces<ApiResponse<PlanOut>>(200).Produces<ApiError>(422).Produces<ApiError>(409).Produces<ApiError>(503));
    }
    public override async Task HandleAsync(CreatePlanIn request, CancellationToken ct) => await Send.OkAsync(ApiResponse<PlanOut>.Success(await service.Create(request, ct)), ct);
}
