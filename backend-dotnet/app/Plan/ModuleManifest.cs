// 唯一 plan 模块声明：三个 Endpoint、一个 Service 和一个 Entity。
using AIIS.Backend.app.Plan.Endpoints;
using AIIS.Backend.app.Plan.Persistence;
using AIIS.Backend.app.Plan.Services;
using AIIS.Backend.Common.Modules;
namespace AIIS.Backend.app.Plan;

public static class ModuleManifest
{
    public static ModuleDefinition Define(bool enabled) => new("plan", enabled, [], ["POST /api/v1/plans", "GET /api/v1/plans/{id}", "GET /api/v1/plans"], [typeof(CreatePlanEndpoint), typeof(GetPlanEndpoint), typeof(ListPlansEndpoint)], typeof(PlanService), typeof(PlanEntity));
}
