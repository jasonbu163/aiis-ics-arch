"""新增公共能源价格快照表；不修改十四表 Core root 或写入价格 seed。"""
from alembic import op
import sqlalchemy as sa

revision = "a6c8e0f2b4d6"
down_revision = "d4e6f8a0b2c4"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "energy_prices",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        *(sa.Column(name, sa.Numeric(10, 4), nullable=False)
          for name in ("electric_price", "hydrogen_price", "argon_price")),
        *(sa.Column(name, sa.Text(), nullable=True)
          for name in ("electric_remark", "hydrogen_remark", "argon_remark", "remark")),
        sa.Column("operator", sa.String(50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        *(sa.CheckConstraint(f"{name} >= 0 AND {name} <= 999999.9999", name=f"ck_energy_prices_{name}_range")
          for name in ("electric_price", "hydrogen_price", "argon_price")),
        *(sa.CheckConstraint(f"char_length({name}) <= {limit}", name=f"ck_energy_prices_{name}_length")
          for name, limit in (("electric_remark", 500), ("hydrogen_remark", 500), ("argon_remark", 500), ("remark", 2000))),
    )
    op.create_index("ix_energy_prices_created_at_id", "energy_prices", ["created_at", "id"], unique=False)


def downgrade():
    op.drop_table("energy_prices")
