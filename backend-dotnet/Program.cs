// 薄入口：配置/日志/静态模块/唯一 scoped Context；启动不连接或改变数据库。
using AIIS.Backend.app.Plan;
using AIIS.Backend.app.Plan.Persistence;
using AIIS.Backend.app.Plan.Services;
using AIIS.Backend.Common.Errors;
using AIIS.Backend.Common.Modules;
using AIIS.Backend.Common.Serialization;
using AIIS.Backend.Configuration;
using AIIS.Backend.Infrastructure.Logging;
using AIIS.Backend.Infrastructure.Persistence;
using FastEndpoints;
using FastEndpoints.OpenApi;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Options;
using Serilog;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddBackendOptions(builder.Configuration);
builder.Host.UseSerilog((context, _, logger) => BackendLogging.Configure(logger, context.Configuration["LoggingOptions:Directory"] ?? "logs"));
builder.Services.AddDbContext<PlanDbContext>((sp, options) =>
{
    var database = sp.GetRequiredService<IOptions<DatabaseOptions>>().Value;
    options.UseMySQL(database.EffectiveConnectionString(), mysql => mysql.CommandTimeout(database.CommandTimeoutSeconds));
});
builder.Services.AddScoped<PlanQueries>();
builder.Services.AddScoped<PlanService>();
builder.Services.AddFastEndpoints();
builder.Services.OpenApiDocument(options => { options.DocumentName = "v1"; options.Title = "AIIS Plan learning slice"; options.Version = "v1"; options.EnableJWTBearerAuth = false; options.ConfigureOpenApi = PlanOpenApi.Configure; });
var app = builder.Build();
var modules = ModuleRegistry.Validate([ModuleManifest.Define(app.Services.GetRequiredService<IOptions<PlanModuleOptions>>().Value.Enabled)]);
var endpoints = modules.SelectMany(x => x.Endpoints).ToHashSet();
app.UseMiddleware<ErrorBoundary>();
app.UseFastEndpoints(options =>
{
    options.Endpoints.Filter = definition => endpoints.Contains(definition.EndpointType);
    options.Errors.StatusCode = 422;
    options.Errors.ResponseBuilder = (errors, _, _) => AIIS.Backend.Common.Contracts.ApiError.From(new PlanException(422, "plan_invalid_request", errors.Select(e => new FieldError(e.PropertyName, "invalid_binding")).ToArray()));
});
app.MapGet("/health", () => Results.Ok(new { status = "alive" }));
app.MapOpenApi("/openapi/{documentName}.json");
app.Lifetime.ApplicationStarted.Register(() => app.Logger.LogInformation("{event}", "backend_started"));
app.Lifetime.ApplicationStopped.Register(() => app.Logger.LogInformation("{event}", "backend_stopped"));
app.Run();

public partial class Program { }
