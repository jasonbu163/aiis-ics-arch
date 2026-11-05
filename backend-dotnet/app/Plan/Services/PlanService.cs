// 创建事务唯一 owner：预查、一次 DB 时间、显式默认、保存和确认提交。
using System.Data;
using AIIS.Backend.app.Plan.Contracts;
using AIIS.Backend.app.Plan.Domain;
using AIIS.Backend.app.Plan.Persistence;
using AIIS.Backend.Common.Errors;
using AIIS.Backend.Infrastructure.Persistence;
using Microsoft.EntityFrameworkCore;
namespace AIIS.Backend.app.Plan.Services;

public sealed class PlanService(PlanDbContext db, PlanQueries queries, ILogger<PlanService> logger)
{
    public async Task<PlanOut> Create(CreatePlanIn input, CancellationToken ct)
    {
        if (!PlanRules.ValidCoil(input.CoilNo)) throw new PlanException(422, "plan_invalid_coil_no");
        bool commitAttempted = false;
        Microsoft.EntityFrameworkCore.Storage.IDbContextTransaction? transaction = null;
        try
        {
            transaction = await db.Database.BeginTransactionAsync(IsolationLevel.ReadCommitted, ct);
            if (await queries.CanonicalExists(input.CoilNo, ct)) throw new PlanException(409, "plan_coil_already_exists");
            // 同连接校验实际 DB 日历/时区，应用绝不修改未知数据库的配置。
            var time = await db.Database.SqlQuery<DatabaseClock>($"SELECT CURRENT_TIMESTAMP AS `LocalTime`, TIMESTAMPDIFF(SECOND, UTC_TIMESTAMP, CURRENT_TIMESTAMP) AS `OffsetSeconds`, @@session.time_zone AS `SessionZone`, @@global.time_zone AS `ServerZone`").SingleAsync(ct);
            if (time.OffsetSeconds != 28800 || time.SessionZone is not ("+08:00" or "Asia/Shanghai") || time.ServerZone is not ("+08:00" or "Asia/Shanghai")) throw new PlanException(503, "plan_database_unavailable");
            var entity = new PlanEntity
            {
                CoilNo = input.CoilNo, Grade = input.Grade, Spec = input.Spec, Weight = input.Weight,
                Thickness = input.Thickness, Width = input.Width, MaterialStatus = input.MaterialStatus,
                Density = input.Density, EntryLength = input.EntryLength, Uncoiler1Tension = input.Uncoiler1Tension,
                ExitTension = input.ExitTension, Process1Tension = input.Process1Tension, EntryLoopTension = input.EntryLoopTension,
                ExitLoopTension = input.ExitLoopTension, EntryUnitTension = input.EntryUnitTension, EntryLoopUnitTension = input.EntryLoopUnitTension,
                ProcessUnitTension = input.ProcessUnitTension, ExitLoopUnitTension = input.ExitLoopUnitTension, ExitUnitTension = input.ExitUnitTension,
                Priority = input.Priority, Remark = input.Remark, Status = "planned", CreatedAt = time.LocalTime, UpdatedAt = time.LocalTime
            };
            queries.Add(entity);
            await db.SaveChangesAsync(ct);
            commitAttempted = true;
            await transaction.CommitAsync(ct);
            logger.LogInformation("{event} {module} {planId} {result}", "plan_created", "plan", entity.Id, "success");
            return PlanOut.From(entity);
        }
        catch (Exception ex)
        {
            var error = ex as PlanException ?? DatabaseErrors.Translate(ex, commitAttempted);
            if (!commitAttempted && transaction is not null)
            {
                try
                {
                    await transaction.RollbackAsync(CancellationToken.None);
                    logger.LogInformation("{event} {module} {errorCode}", "plan_transaction_rolled_back", "plan", error.ErrorCode);
                }
                catch { logger.LogWarning("{event} {module}", "plan_rollback_unconfirmed", "plan"); }
            }
            if (DatabaseErrors.IsCoilConflict(ex)) logger.LogWarning("{event} {module} {errorCode} {databaseErrorNumber}", "plan_unique_conflict", "plan", error.ErrorCode, 1062);
            logger.LogWarning("{event} {module} {errorCode} {result}", commitAttempted ? "plan_commit_unconfirmed" : "plan_transaction_failed", "plan", error.ErrorCode, "failure");
            throw error;
        }
        finally
        {
            if (transaction is not null)
            {
                try { await transaction.DisposeAsync(); }
                catch { logger.LogWarning("{event} {module}", "plan_transaction_dispose_unconfirmed", "plan"); }
            }
        }
    }
    public async Task<PlanOut> Get(int id, CancellationToken ct)
    {
        try { return PlanOut.From(await queries.Find(id, ct) ?? throw new PlanException(404, "plan_not_found")); }
        catch (Exception ex) when (ex is not PlanException) { throw DatabaseErrors.Translate(ex); }
    }
    public async Task<PlanPageOut> List(PlanQueryIn input, CancellationToken ct)
    {
        try
        {
            var result = await queries.List(input, ct);
            return new(result.Items.Select(PlanOut.From).ToArray(), result.Total, input.Page, input.PageSize, (int)(((long)result.Total + input.PageSize - 1) / input.PageSize));
        }
        catch (Exception ex) { throw DatabaseErrors.Translate(ex); }
    }
}
public sealed class DatabaseClock
{
    public DateTime LocalTime { get; set; }
    public long OffsetSeconds { get; set; }
    public string SessionZone { get; set; } = "";
    public string ServerZone { get; set; } = "";
}
