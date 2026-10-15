"""新增小时价格表；保留所有旧追加记录；downgrade 会丢失小时表全部新数据。"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import DATETIME

revision = "b8d0f2a4c6e8"
down_revision = "a6c8e0f2b4d6"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "energy_price_hours",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        *(sa.Column(name, sa.Numeric(10, 4), nullable=False)
          for name in ("electric_price", "hydrogen_price", "argon_price")),
        *(sa.Column(name, sa.Text(), nullable=True)
          for name in ("electric_remark", "hydrogen_remark", "argon_remark", "remark")),
        sa.Column("operator", sa.String(50), nullable=False),
        sa.Column("observed_at", sa.DateTime().with_variant(DATETIME(fsp=6), "mysql"), nullable=False),
        sa.Column("hour_start", sa.DateTime().with_variant(DATETIME(fsp=6), "mysql"), nullable=False),
        sa.Column("created_at", sa.DateTime().with_variant(DATETIME(fsp=6), "mysql"), server_default=sa.text("(UTC_TIMESTAMP(6))"), nullable=False),
        sa.Column("updated_at", sa.DateTime().with_variant(DATETIME(fsp=6), "mysql"), server_default=sa.text("(UTC_TIMESTAMP(6))"), nullable=False),
        sa.UniqueConstraint("hour_start", name="uq_energy_price_hours_hour_start"),
        sa.PrimaryKeyConstraint("id"),
        *(sa.CheckConstraint(f"{name} >= 0 AND {name} <= 999999.9999", name=f"ck_energy_price_hours_{name}_range")
          for name in ("electric_price", "hydrogen_price", "argon_price")),
        *(sa.CheckConstraint(f"char_length({name}) <= {limit}", name=f"ck_energy_price_hours_{name}_length")
          for name, limit in (("electric_remark", 500), ("hydrogen_remark", 500), ("argon_remark", 500), ("remark", 2000))),
    )
    op.create_index("ix_energy_price_hours_observed_at_id", "energy_price_hours", ["observed_at", "id"], unique=False)


def downgrade():
    op.drop_table("energy_price_hours")
