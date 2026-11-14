"""PLC 来源登记事务、冲突仲裁和提交结果。"""
from uuid import uuid4

from sqlalchemy.exc import OperationalError

from ..crud import async_source_registry as crud
from ..crud import async_v2


class RegistryError(Exception):
    def __init__(self, code, status):
        self.key = 'acquisition_sources.' + code
        self.status = status
        super().__init__(self.key)


async def ensure_ready(db, profile):
    await async_v2.target_now(db, profile['target'])


async def list_sources(db, profile, page, page_size):
    try:
        await ensure_ready(db, profile)
        return await crud.page(db, page, page_size)
    except Exception:
        raise RegistryError('not_ready', 503) from None


def matches(binding, body):
    return (binding.instance_id == crud.key(body.instance_id)
            and binding.source_generation == crud.key(body.source_generation)
            and binding.source_type == body.source_type)


async def register(db, profile, body):
    # Two missing-key inserts can deadlock on MySQL gap locks.
    for attempt in range(3):
        commit_attempted = False
        try:
            await ensure_ready(db, profile)
            binding = await crud.binding_for_update(db, body.plc_id)
            if binding is not None and not matches(binding, body):
                raise RegistryError('source_conflict', 409)
            if binding is None:
                if await crud.generation_exists(db, body.plc_id, body.source_generation):
                    raise RegistryError('generation_reused', 409)
                revision = str(uuid4())
                binding = await crud.insert_binding(db, body, revision)
                if not matches(binding, body):
                    raise RegistryError('source_conflict', 409)
                outcome = 'created' if binding.registration_revision == revision else 'unchanged'
            else:
                outcome = 'unchanged'
            result = await crud.source(db, body.plc_id)
            commit_attempted = True
            await db.commit()
            return outcome, result
        except RegistryError:
            await db.rollback()
            raise
        except OperationalError as error:
            try:
                await db.rollback()
            except Exception:
                raise RegistryError('commit_outcome_unknown' if commit_attempted else 'not_ready', 503) from None
            errno = error.orig.args[0] if getattr(error.orig, 'args', ()) else None
            if not commit_attempted and errno in (1205, 1213) and attempt < 2:
                continue
            raise RegistryError('commit_outcome_unknown' if commit_attempted else 'not_ready', 503) from None
        except Exception:
            try:
                await db.rollback()
            except Exception:
                commit_attempted = True
            raise RegistryError('commit_outcome_unknown' if commit_attempted else 'not_ready', 503) from None
    raise RegistryError('not_ready', 503)


async def update(db, profile, body):
    commit_attempted = False
    try:
        await ensure_ready(db, profile)
        binding = await crud.binding_for_update(db, body.plc_id)
        if binding is None:
            raise RegistryError('not_found', 404)
        expected = body.expected
        if (binding.instance_id != crud.key(expected.instance_id)
                or binding.source_generation != crud.key(expected.source_generation)
                or binding.registration_revision != expected.registration_revision):
            raise RegistryError('revision_conflict', 409)
        previous = await crud.source(db, body.plc_id)
        if body.action == 'delete':
            await crud.delete_binding(db, binding)
            outcome = 'deleted'
            result = previous
        elif body.action == 'takeover':
            replacement = body.replacement
            if await crud.generation_exists(db, body.plc_id, replacement.source_generation, binding):
                raise RegistryError('generation_reused', 409)
            await crud.update_binding(db, binding, str(uuid4()), replacement.source_type, replacement)
            outcome = 'replaced'
        elif body.source_type != binding.source_type:
            await crud.update_binding(db, binding, str(uuid4()), body.source_type)
            outcome = 'updated'
        else:
            outcome = 'unchanged'
        if body.action != 'delete':
            result = await crud.source(db, body.plc_id)
        commit_attempted = True
        await db.commit()
        return outcome, result, previous
    except RegistryError:
        await db.rollback()
        raise
    except Exception:
        try:
            await db.rollback()
        except Exception:
            commit_attempted = True
        raise RegistryError('commit_outcome_unknown' if commit_attempted else 'not_ready', 503) from None
