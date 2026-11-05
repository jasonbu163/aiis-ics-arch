// 只负责参数化查询和添加实体，不提交事务、不操作 HTTP。
using AIIS.Backend.app.Plan.Contracts;
using AIIS.Backend.Infrastructure.Persistence;
using Microsoft.EntityFrameworkCore;
namespace AIIS.Backend.app.Plan.Persistence;

public sealed class PlanQueries(PlanDbContext db)
{
    public Task<bool> CanonicalExists(string coilNo, CancellationToken ct) => db.Plans.FromSqlInterpolated($"SELECT * FROM plans WHERE LOWER(TRIM(coil_no)) = LOWER(TRIM({coilNo}))").AsNoTracking().AnyAsync(ct);
    public Task<PlanEntity?> Find(int id, CancellationToken ct) => db.Plans.AsNoTracking().SingleOrDefaultAsync(x => x.Id == id, ct);
    public void Add(PlanEntity entity) => db.Plans.Add(entity);
    public async Task<(List<PlanEntity> Items, int Total)> List(PlanQueryIn input, CancellationToken ct)
    {
        var query = db.Plans.AsNoTracking();
        if (!string.IsNullOrEmpty(input.CoilNo)) query = query.Where(x => EF.Functions.Like(x.CoilNo, "%" + input.CoilNo + "%"));
        if (!string.IsNullOrEmpty(input.Grade)) query = query.Where(x => x.Grade == input.Grade);
        if (!string.IsNullOrEmpty(input.MaterialStatus)) query = query.Where(x => x.MaterialStatus == input.MaterialStatus);
        if (!string.IsNullOrEmpty(input.Status)) query = query.Where(x => x.Status == input.Status);
        int total = await query.CountAsync(ct);
        var items = await query.OrderByDescending(x => x.CreatedAt).ThenByDescending(x => x.Id).Skip(input.Offset).Take(input.PageSize).ToListAsync(ct);
        return (items, total);
    }
}
