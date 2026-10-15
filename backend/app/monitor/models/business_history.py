"""监控业务历史切片；不覆盖现场Core三模型。"""
from datetime import datetime
from typing import Optional
from sqlalchemy import func, Index, String, DateTime, Float, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from database import Base, IntPk, Timestamp, UpdatedAt
class HistoryProcessCurve(Base):
    """
    过程曲线历史表（专供 ECharts 绘制对比曲线）

    对应 PLC 点位（共 28 个字段 = 26 过程控制 + 2 能耗趋势）：
    - LineSpeedSet_mpm / LineSpeedAct_mpm        → 线速度 (2)
    - Z1~Z6TemSet / Z1~Z6TemAct                  → 6区炉温 SP/PV (12)
    - UncSetTension_P / UncActTension_P / Kg     → 开卷张力 (3)
    - RecSetTension_P / RecActTension_P / Kg     → 收卷张力 (3)
    - FurnSetTension_Kg / FurnActTension_Kg      → 炉内张力 (2)
    - CoolFan1/2SetFre / CoolFan1/2ActFre        → 风冷频率 (4)
    - N2_Total_m3 / ElectConsum                  → 能耗瞬时值 (2)
    """
    __tablename__ = "monitor_history_process_curves"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    device_id: Mapped[int] = mapped_column(Integer, index=True)
    coil_number: Mapped[Optional[str]] = mapped_column(String(50), index=True, comment="当前生产钢卷号")

    # ── 线速度 ──
    line_speed_set: Mapped[Optional[float]] = mapped_column(Float, comment="产线设定速度m/min")
    line_speed_act: Mapped[Optional[float]] = mapped_column(Float, comment="产线实际速度m/min")

    # ── 温度 SP/PV 结对（6区，用于评估 PID 控温精度）──
    z1_temp_set: Mapped[Optional[int]] = mapped_column(Integer, comment="1区设定温度℃")
    z1_temp_act: Mapped[Optional[int]] = mapped_column(Integer, comment="1区实际温度℃")
    z2_temp_set: Mapped[Optional[int]] = mapped_column(Integer, comment="2区设定温度℃")
    z2_temp_act: Mapped[Optional[int]] = mapped_column(Integer, comment="2区实际温度℃")
    z3_temp_set: Mapped[Optional[int]] = mapped_column(Integer, comment="3区设定温度℃")
    z3_temp_act: Mapped[Optional[int]] = mapped_column(Integer, comment="3区实际温度℃")
    z4_temp_set: Mapped[Optional[int]] = mapped_column(Integer, comment="4区设定温度℃")
    z4_temp_act: Mapped[Optional[int]] = mapped_column(Integer, comment="4区实际温度℃")
    z5_temp_set: Mapped[Optional[int]] = mapped_column(Integer, comment="5区设定温度℃")
    z5_temp_act: Mapped[Optional[int]] = mapped_column(Integer, comment="5区实际温度℃")
    z6_temp_set: Mapped[Optional[int]] = mapped_column(Integer, comment="6区设定温度℃")
    z6_temp_act: Mapped[Optional[int]] = mapped_column(Integer, comment="6区实际温度℃")

    # ── 张力控制 ──
    unc_set_tension_p: Mapped[Optional[float]] = mapped_column(Float, comment="开卷机张力设定%")
    unc_act_tension_p: Mapped[Optional[float]] = mapped_column(Float, comment="开卷机实际张力%")
    unc_set_tension_kg: Mapped[Optional[float]] = mapped_column(Float, comment="开卷机张力设定Kg")

    rec_set_tension_p: Mapped[Optional[float]] = mapped_column(Float, comment="收卷机张力设定%")
    rec_act_tension_p: Mapped[Optional[float]] = mapped_column(Float, comment="收卷机实际张力%")
    rec_set_tension_kg: Mapped[Optional[float]] = mapped_column(Float, comment="收卷机张力设定Kg")

    furn_set_tension_kg: Mapped[Optional[float]] = mapped_column(Float, comment="炉内张力设定Kg")
    furn_act_tension_kg: Mapped[Optional[float]] = mapped_column(Float, comment="炉内实际张力Kg")

    # ── 风冷系统 ──
    cool_fan1_set_fre: Mapped[Optional[float]] = mapped_column(Float, comment="风冷1设定频率Hz")
    cool_fan1_act_fre: Mapped[Optional[float]] = mapped_column(Float, comment="风冷1实际频率Hz")
    cool_fan2_set_fre: Mapped[Optional[float]] = mapped_column(Float, comment="风冷2设定频率Hz")
    cool_fan2_act_fre: Mapped[Optional[float]] = mapped_column(Float, comment="风冷2实际频率Hz")

    # ── 能耗趋势（瞬时值，供过程趋势图对比）──
    n2_total: Mapped[Optional[float]] = mapped_column(Float, comment="氮气累计量m³")
    elect_consum: Mapped[Optional[float]] = mapped_column(Float, comment="用电累计量KWh")

    # ── 质量监控指标 ──
    h2_flow: Mapped[Optional[float]] = mapped_column(Float, comment="耗氢量m³/h")
    n2_flow: Mapped[Optional[float]] = mapped_column(Float, comment="耗氮量m³/h")
    oxygen_content: Mapped[Optional[float]] = mapped_column(Float, comment="氧含量ppm")
    dew_point: Mapped[Optional[float]] = mapped_column(Float, comment="露点值℃")
    muffle_pressure: Mapped[Optional[float]] = mapped_column(Float, comment="马弗压力Pa")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

class HistoryEnergyConsumption(Base):
    """
    能耗统计历史表（供财务核算，按卷汇总）

    对应 PLC 点位：
    - N2_Total_m3：氮气总量
    - ElectConsum：用电量

    写入时机：钢卷生产结束时，记录该卷的能耗增量
    """
    __tablename__ = "monitor_history_energy_consumptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    device_id: Mapped[int] = mapped_column(Integer, index=True)
    coil_number: Mapped[Optional[str]] = mapped_column(String(50), index=True, comment="钢卷号")

    elect_consum: Mapped[Optional[float]] = mapped_column(Float, comment="本卷用电量KWh")
    n2_total: Mapped[Optional[float]] = mapped_column(Float, comment="本卷氮气量m³")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
