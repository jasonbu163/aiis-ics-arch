// 统一异常信封与 requestId；保留稳定事件，绝不回显异常/正文/连接串。
using System.Diagnostics;
using AIIS.Backend.Common.Contracts;
using Microsoft.AspNetCore.Http.Metadata;
using Serilog.Context;
namespace AIIS.Backend.Common.Errors;

public sealed class ErrorBoundary(RequestDelegate next, ILogger<ErrorBoundary> logger)
{
    public async Task InvokeAsync(HttpContext context)
    {
        string requestId = context.TraceIdentifier;
        context.Response.Headers["X-Request-Id"] = requestId;
        using var scope = LogContext.PushProperty("requestId", requestId);
        long started = Stopwatch.GetTimestamp();
        try
        {
            // 已匹配的JSON入口在框架开始空响应前拒绝缺失/不符的媒体类型。
            var accepts = context.GetEndpoint()?.Metadata.GetMetadata<IAcceptsMetadata>();
            if (HttpMethods.IsPost(context.Request.Method) && accepts?.ContentTypes.Contains("application/json", StringComparer.OrdinalIgnoreCase) == true &&
                !string.Equals(context.Request.ContentType?.Split(';')[0].Trim(), "application/json", StringComparison.OrdinalIgnoreCase))
                throw new PlanException(415, "plan_invalid_request");
            await next(context);
            // Accepts媒体匹配可直接返回415而不抛异常；未开始的响应仍走同一错误映射。
            if (context.Response.StatusCode == StatusCodes.Status415UnsupportedMediaType && !context.Response.HasStarted)
                throw new PlanException(415, "plan_invalid_request");
        }
        catch (Exception ex)
        {
            var error = ex as PlanException ?? DatabaseErrors.Translate(ex);
            logger.LogWarning("{event} {module} {errorCode} {result}", error.Status == 422 ? "plan_validation_failed" : "plan_request_failed", "plan", error.ErrorCode, "failure");
            context.Response.StatusCode = error.Status;
            context.Response.ContentLength = null;
            await context.Response.WriteAsJsonAsync(ApiError.From(error), CancellationToken.None);
        }
        finally
        {
            if (context.Response.StatusCode >= 400 || context.Request.Method == "POST")
                logger.LogInformation("{event} {module} {result} {elapsedMs}", "plan_request_finished", "plan", context.Response.StatusCode, Stopwatch.GetElapsedTime(started).TotalMilliseconds);
        }
    }
}
