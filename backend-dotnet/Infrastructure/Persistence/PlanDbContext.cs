// 每请求 scoped EF Context；模型组装不打开连接、不创建表、不播种。
using AIIS.Backend.app.Plan.Persistence;
using Microsoft.EntityFrameworkCore;
namespace AIIS.Backend.Infrastructure.Persistence;

public sealed class PlanDbContext(DbContextOptions<PlanDbContext> options) : DbContext(options)
{
    public DbSet<PlanEntity> Plans => Set<PlanEntity>();
    protected override void OnModelCreating(ModelBuilder builder) => builder.ApplyConfiguration(new PlanEntityConfiguration());
}
