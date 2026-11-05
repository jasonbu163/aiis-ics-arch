// plans 显式 SQL 类型、列名和四个命名索引；不声明 server defaults 或迁移。
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
namespace AIIS.Backend.app.Plan.Persistence;

public sealed class PlanEntityConfiguration : IEntityTypeConfiguration<PlanEntity>
{
    public void Configure(EntityTypeBuilder<PlanEntity> b)
    {
        b.ToTable("plans");
        b.HasKey(x => x.Id);
        b.Property(x => x.Id).HasColumnName("id").HasColumnType("int").ValueGeneratedOnAdd();
        b.Property(x => x.CoilNo).HasColumnName("coil_no").HasColumnType("varchar(50)").IsRequired();
        b.Property(x => x.Grade).HasColumnName("grade").HasColumnType("varchar(20)").IsRequired();
        b.Property(x => x.Spec).HasColumnName("spec").HasColumnType("varchar(50)").IsRequired();
        b.Property(x => x.MaterialStatus).HasColumnName("material_status").HasColumnType("varchar(20)").IsRequired();
        b.Property(x => x.Status).HasColumnName("status").HasColumnType("varchar(20)").IsRequired();
        b.Property(x => x.Priority).HasColumnName("priority").HasColumnType("smallint");
        b.Property(x => x.Remark).HasColumnName("remark").HasColumnType("varchar(500)");
        b.Property(x => x.CreatedAt).HasColumnName("created_at").HasColumnType("datetime(0)");
        b.Property(x => x.UpdatedAt).HasColumnName("updated_at").HasColumnType("datetime(0)");
        b.Property(x => x.Weight).HasColumnName("weight").HasColumnType("decimal(12,4)").HasPrecision(12, 4);
        b.Property(x => x.Thickness).HasColumnName("thickness").HasColumnType("decimal(10,3)").HasPrecision(10, 3);
        b.Property(x => x.Width).HasColumnName("width").HasColumnType("decimal(10,2)").HasPrecision(10, 2);
        b.Property(x => x.Density).HasColumnName("density").HasColumnType("decimal(10,2)").HasPrecision(10, 2);
        b.Property(x => x.EntryLength).HasColumnName("entry_length").HasColumnType("decimal(10,2)").HasPrecision(10, 2);
        b.Property(x => x.Uncoiler1Tension).HasColumnName("uncoiler1_tension").HasColumnType("decimal(10,2)").HasPrecision(10, 2);
        b.Property(x => x.ExitTension).HasColumnName("exit_tension").HasColumnType("decimal(10,2)").HasPrecision(10, 2);
        b.Property(x => x.Process1Tension).HasColumnName("process1_tension").HasColumnType("decimal(10,2)").HasPrecision(10, 2);
        b.Property(x => x.EntryLoopTension).HasColumnName("entry_loop_tension").HasColumnType("decimal(10,2)").HasPrecision(10, 2);
        b.Property(x => x.ExitLoopTension).HasColumnName("exit_loop_tension").HasColumnType("decimal(10,2)").HasPrecision(10, 2);
        b.Property(x => x.EntryUnitTension).HasColumnName("entry_unit_tension").HasColumnType("decimal(12,4)").HasPrecision(12, 4);
        b.Property(x => x.EntryLoopUnitTension).HasColumnName("entry_loop_unit_tension").HasColumnType("decimal(12,4)").HasPrecision(12, 4);
        b.Property(x => x.ProcessUnitTension).HasColumnName("process_unit_tension").HasColumnType("decimal(12,4)").HasPrecision(12, 4);
        b.Property(x => x.ExitLoopUnitTension).HasColumnName("exit_loop_unit_tension").HasColumnType("decimal(12,4)").HasPrecision(12, 4);
        b.Property(x => x.ExitUnitTension).HasColumnName("exit_unit_tension").HasColumnType("decimal(12,4)").HasPrecision(12, 4);
        b.HasIndex(x => x.CoilNo).IsUnique().HasDatabaseName("ix_plans_coil_no");
        b.HasIndex(x => x.Id).HasDatabaseName("ix_plans_id");
        b.HasIndex(x => x.Priority).HasDatabaseName("ix_plans_priority");
        b.HasIndex(x => x.Status).HasDatabaseName("ix_plans_status");
    }
}
