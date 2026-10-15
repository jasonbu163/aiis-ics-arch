"""
文件路径: /backend/app/plan/services/async_service.py
功能描述: 生产计划管理异步业务服务
主要功能:
    - 编排计划 CRUD 与列表查询
    - 保持 FastAPI route 与数据库 CRUD 解耦
    - 不承担设备执行、任务调度或实绩生成
"""
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.performance.models import Performance
from app.plan.crud.async_crud import async_crud_plan
from app.plan.domain import (
    canonicalize_coil_no,
    ensure_same_canonical_coil,
    is_valid_coil_no,
    is_observable_plan_status,
)
from app.plan.models import Plan
from app.plan.schemas.plan import (
    PlanCreate,
    PlanLinkCandidate,
    PlanPerformanceLinkageResult,
    PlanUpdate,
    PlanXlsxImportError,
    PlanXlsxImportResult,
)
from app.plan.services.xlsx_io import (
    build_export_workbook,
    build_template_workbook,
    parse_plan_workbook,
)
from common.data_keys import PerformanceRecordSource, PlanObservationStatus
from common.error_codes import ErrorCode
from common.exceptions import BusinessException
from common.log import log_event


class AsyncPlanService:
    """生产计划意图的异步管理入口。"""

    @staticmethod
    async def list_plans(
        db: AsyncSession,
        *,
        page: int,
        page_size: int,
        coil_no: str | None,
        grade: str | None,
        material_status: str | None,
        status: str | None,
    ) -> dict[str, Any]:
        return await async_crud_plan.get_list_with_filters(
            db=db,
            page=page,
            page_size=page_size,
            coil_no=coil_no,
            grade=grade,
            material_status=material_status,
            status=status,
        )

    @staticmethod
    async def create_plan(db: AsyncSession, plan_data: PlanCreate) -> Plan:
        if not is_valid_coil_no(plan_data.coil_no):
            raise BusinessException(ErrorCode.PLAN_INVALID_COIL_NO)
        if await async_crud_plan.exists_by_canonical_coil_no(db, plan_data.coil_no):
            raise BusinessException(ErrorCode.PLAN_COIL_ALREADY_EXISTS)
        return await async_crud_plan.create(db, plan_data)

    @staticmethod
    async def get_plan(db: AsyncSession, plan_id: int) -> Plan | None:
        return await async_crud_plan.get_by_id(db, plan_id)

    @staticmethod
    async def update_plan(
        db: AsyncSession,
        plan_id: int,
        plan_data: PlanUpdate,
    ) -> Plan | None:
        return await async_crud_plan.update(db, plan_id, plan_data)

    @staticmethod
    async def delete_plan(db: AsyncSession, plan_id: int) -> bool:
        return await async_crud_plan.delete(db, plan_id)

    @staticmethod
    async def get_link_candidates(
        db: AsyncSession,
        *,
        performance_id: int,
    ) -> dict[str, Any]:
        performance = await AsyncPlanService._get_performance(db, performance_id)
        canonical_coil_no = AsyncPlanService._performance_canonical_coil(performance)
        plans = await async_crud_plan.list_by_canonical_coil_no(db, performance.coil_no)
        return {
            "performanceId": performance.id,
            "performanceCoilNo": performance.coil_no,
            "canonicalCoilNo": canonical_coil_no,
            "candidateCount": len(plans),
            "candidates": [
                AsyncPlanService._candidate_out(plan).model_dump(by_alias=True)
                for plan in plans
            ],
        }

    @staticmethod
    async def sync_observation(
        db: AsyncSession,
        *,
        performance_id: int,
        operator_id: int | None = None,
    ) -> PlanPerformanceLinkageResult:
        performance = await AsyncPlanService._get_performance(db, performance_id, with_lock=True)
        canonical_coil_no = AsyncPlanService._performance_canonical_coil(performance)

        if performance.plan_id is not None:
            plan = await async_crud_plan.get_by_id_with_lock(db, performance.plan_id)
            if plan is None:
                raise BusinessException(ErrorCode.PLAN_NOT_FOUND, code=404)
            AsyncPlanService._ensure_plan_can_observe(plan)
            if plan.status != PlanObservationStatus.OBSERVED.value:
                plan.status = PlanObservationStatus.OBSERVED.value
                await db.flush()
                await db.refresh(plan)
            return AsyncPlanService._linkage_result(
                performance,
                canonical_coil_no=canonical_coil_no,
                action="already_linked",
                linked=True,
                plan=plan,
                candidate_count=1,
            )

        AsyncPlanService._ensure_unplanned_linkable(performance)
        candidates = list(
            await async_crud_plan.list_by_canonical_coil_no(
                db,
                performance.coil_no,
                with_lock=True,
            )
        )
        if not candidates:
            return AsyncPlanService._linkage_result(
                performance,
                canonical_coil_no=canonical_coil_no,
                action="no_matching_plan",
                linked=False,
                candidate_count=0,
            )
        if len(candidates) > 1:
            raise BusinessException(ErrorCode.PLAN_LINK_CANDIDATE_CONFLICT)

        plan = candidates[0]
        AsyncPlanService._ensure_plan_can_observe(plan)
        await AsyncPlanService._ensure_plan_not_linked_elsewhere(db, plan.id, performance.id)
        return await AsyncPlanService._link_performance_to_plan(
            db,
            performance=performance,
            plan=plan,
            canonical_coil_no=canonical_coil_no,
            action="synced_observation",
            operator_id=operator_id,
        )

    @staticmethod
    async def link_existing_plan(
        db: AsyncSession,
        *,
        performance_id: int,
        plan_id: int,
        operator_id: int | None = None,
    ) -> PlanPerformanceLinkageResult:
        performance = await AsyncPlanService._get_performance(db, performance_id, with_lock=True)
        plan = await async_crud_plan.get_by_id_with_lock(db, plan_id)
        if plan is None:
            raise BusinessException(ErrorCode.PLAN_NOT_FOUND, code=404)

        canonical_coil_no = AsyncPlanService._performance_canonical_coil(performance)
        if not ensure_same_canonical_coil(performance.coil_no, plan.coil_no):
            raise BusinessException(ErrorCode.PLAN_COIL_CONFLICT)

        if performance.plan_id == plan.id:
            AsyncPlanService._ensure_plan_can_observe(plan)
            if plan.status != PlanObservationStatus.OBSERVED.value:
                plan.status = PlanObservationStatus.OBSERVED.value
                await db.flush()
                await db.refresh(plan)
            return AsyncPlanService._linkage_result(
                performance,
                canonical_coil_no=canonical_coil_no,
                action="already_linked",
                linked=True,
                plan=plan,
                candidate_count=1,
            )

        AsyncPlanService._ensure_unplanned_linkable(performance)
        AsyncPlanService._ensure_plan_can_observe(plan)
        await AsyncPlanService._ensure_plan_not_linked_elsewhere(db, plan.id, performance.id)
        return await AsyncPlanService._link_performance_to_plan(
            db,
            performance=performance,
            plan=plan,
            canonical_coil_no=canonical_coil_no,
            action="linked_existing_plan",
            operator_id=operator_id,
        )

    @staticmethod
    async def backfill_plan_from_performance(
        db: AsyncSession,
        *,
        performance_id: int,
        plan_data: PlanCreate,
        operator_id: int | None = None,
    ) -> PlanPerformanceLinkageResult:
        performance = await AsyncPlanService._get_performance(db, performance_id, with_lock=True)
        canonical_coil_no = AsyncPlanService._performance_canonical_coil(performance)
        AsyncPlanService._ensure_unplanned_linkable(performance)

        if not is_valid_coil_no(plan_data.coil_no):
            raise BusinessException(ErrorCode.PLAN_INVALID_COIL_NO)
        if not ensure_same_canonical_coil(performance.coil_no, plan_data.coil_no):
            raise BusinessException(ErrorCode.PLAN_COIL_CONFLICT)
        if await async_crud_plan.exists_by_canonical_coil_no(db, plan_data.coil_no):
            raise BusinessException(ErrorCode.PLAN_COIL_ALREADY_EXISTS)

        plan = await async_crud_plan.create(db, plan_data)
        return await AsyncPlanService._link_performance_to_plan(
            db,
            performance=performance,
            plan=plan,
            canonical_coil_no=canonical_coil_no,
            action="backfilled_plan",
            operator_id=operator_id,
        )

    @staticmethod
    def build_xlsx_template() -> bytes:
        return build_template_workbook()

    @staticmethod
    async def build_xlsx_export(
        db: AsyncSession,
        *,
        plan_ids: list[int] | None = None,
        coil_no: str | None = None,
        grade: str | None = None,
        material_status: str | None = None,
        status: str | None = None,
        operator_id: int | None = None,
    ) -> bytes:
        plans = await async_crud_plan.list_for_export(
            db,
            plan_ids=plan_ids,
            coil_no=coil_no,
            grade=grade,
            material_status=material_status,
            status=status,
        )
        log_event(
            "INFO",
            "plan_xlsx_exported",
            operator_id=operator_id,
            exported_count=len(plans),
            has_selected_ids=bool(plan_ids),
        )
        return build_export_workbook(plans)

    @staticmethod
    async def import_xlsx(
        db: AsyncSession,
        *,
        content: bytes,
        dry_run: bool,
        conflict_strategy: str,
        operator_id: int | None = None,
    ) -> PlanXlsxImportResult:
        if conflict_strategy != "reject":
            raise BusinessException(ErrorCode.PLAN_XLSX_UNSUPPORTED_CONFLICT_STRATEGY)

        parsed = parse_plan_workbook(content)
        errors = list(parsed.errors)

        for row in parsed.rows:
            existing_plans = await async_crud_plan.list_by_canonical_coil_no(db, row.plan.coil_no)
            if existing_plans:
                errors.append(
                    PlanXlsxImportError(
                        row=row.row_number,
                        field="coil_no",
                        error_code=ErrorCode.PLAN_COIL_ALREADY_EXISTS.value,
                        message=ErrorCode.PLAN_COIL_ALREADY_EXISTS.value,
                    )
                )

        if errors:
            log_event(
                "INFO",
                "plan_xlsx_import_rejected",
                operator_id=operator_id,
                dry_run=dry_run,
                error_count=len(errors),
            )
            return PlanXlsxImportResult(
                dry_run=dry_run,
                valid=False,
                created_count=0,
                error_count=len(errors),
                errors=errors,
            )

        if dry_run:
            return PlanXlsxImportResult(
                dry_run=True,
                valid=True,
                created_count=0,
                error_count=0,
                errors=[],
            )

        try:
            for row in parsed.rows:
                await async_crud_plan.create(db, row.plan)
        except IntegrityError as exc:
            raise BusinessException(ErrorCode.PLAN_XLSX_VALIDATION_FAILED) from exc

        log_event(
            "INFO",
            "plan_xlsx_imported",
            operator_id=operator_id,
            imported_count=len(parsed.rows),
        )
        return PlanXlsxImportResult(
            dry_run=False,
            valid=True,
            created_count=len(parsed.rows),
            error_count=0,
            errors=[],
        )

    @staticmethod
    async def _get_performance(
        db: AsyncSession,
        performance_id: int,
        *,
        with_lock: bool = False,
    ) -> Performance:
        query = select(Performance).where(Performance.id == performance_id)
        if with_lock:
            query = query.with_for_update()
        result = await db.execute(query)
        performance = result.scalar_one_or_none()
        if performance is None:
            raise BusinessException(ErrorCode.PLAN_PERFORMANCE_NOT_FOUND, code=404)
        return performance

    @staticmethod
    def _performance_canonical_coil(performance: Performance) -> str:
        canonical_coil_no = canonicalize_coil_no(performance.coil_no)
        if canonical_coil_no is None:
            raise BusinessException(ErrorCode.PLAN_COIL_CONFLICT)
        return canonical_coil_no

    @staticmethod
    def _ensure_unplanned_linkable(performance: Performance) -> None:
        if performance.plan_id is not None:
            raise BusinessException(ErrorCode.PLAN_PERFORMANCE_ALREADY_LINKED)
        if performance.record_source != PerformanceRecordSource.UNPLANNED_PLC.value:
            raise BusinessException(ErrorCode.PLAN_PERFORMANCE_NOT_UNPLANNED)

    @staticmethod
    def _ensure_plan_can_observe(plan: Plan) -> None:
        if not is_observable_plan_status(plan.status):
            raise BusinessException(ErrorCode.PLAN_INVALID_STATE)

    @staticmethod
    async def _ensure_plan_not_linked_elsewhere(
        db: AsyncSession,
        plan_id: int,
        performance_id: int,
    ) -> None:
        result = await db.execute(
            select(Performance.id)
            .where(Performance.plan_id == plan_id, Performance.id != performance_id)
            .limit(1)
        )
        if result.scalar_one_or_none() is not None:
            raise BusinessException(ErrorCode.PLAN_LINK_CANDIDATE_CONFLICT)

    @staticmethod
    async def _link_performance_to_plan(
        db: AsyncSession,
        *,
        performance: Performance,
        plan: Plan,
        canonical_coil_no: str,
        action: str,
        operator_id: int | None,
    ) -> PlanPerformanceLinkageResult:
        performance.plan_id = plan.id
        plan.status = PlanObservationStatus.OBSERVED.value
        await db.flush()
        await db.refresh(performance)
        await db.refresh(plan)
        log_event(
            "INFO",
            "plan_performance_linked",
            operator_id=operator_id,
            performance_id=performance.id,
            plan_id=plan.id,
            action=action,
        )
        return AsyncPlanService._linkage_result(
            performance,
            canonical_coil_no=canonical_coil_no,
            action=action,
            linked=True,
            plan=plan,
            candidate_count=1,
        )

    @staticmethod
    def _candidate_out(plan: Plan) -> PlanLinkCandidate:
        return PlanLinkCandidate(
            id=plan.id,
            coil_no=plan.coil_no,
            grade=plan.grade,
            spec=plan.spec,
            weight=plan.weight,
            status=plan.status,
            priority=plan.priority,
        )

    @staticmethod
    def _linkage_result(
        performance: Performance,
        *,
        canonical_coil_no: str,
        action: str,
        linked: bool,
        plan: Plan | None = None,
        candidate_count: int = 0,
    ) -> PlanPerformanceLinkageResult:
        return PlanPerformanceLinkageResult(
            performance_id=performance.id,
            performance_coil_no=performance.coil_no,
            canonical_coil_no=canonical_coil_no,
            action=action,
            linked=linked,
            plan_id=plan.id if plan is not None else performance.plan_id,
            plan_status=plan.status if plan is not None else None,
            candidate_count=candidate_count,
        )


async_plan_service = AsyncPlanService()
