"""
文件路径: /backend/core/base.py
功能描述: 核心基础类定义
主要功能:
    - 提供 BaseService 服务基类
    - 通用 CRUD 操作封装（异步版本）
"""
from typing import TypeVar, Generic, Optional, List, Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar('T')


class BaseService(Generic[T]):
    """
    服务基类
    
    提供通用的 CRUD 操作（异步版本）
    """
    
    def __init__(self, db: AsyncSession, model_class: type):
        self.db = db
        self.model_class = model_class
    
    async def get_by_id(self, id: int) -> Optional[T]:
        """获取单个记录"""
        result = await self.db.execute(
            select(self.model_class).where(self.model_class.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """获取所有记录"""
        result = await self.db.execute(
            select(self.model_class).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def list(self, page: int = 1, page_size: int = 20, filters: dict = None, order_by: str = None, desc: bool = False) -> tuple:
        """分页查询列表"""
        query = select(self.model_class)
        
        if filters:
            for key, value in filters.items():
                if value is not None:
                    query = query.where(getattr(self.model_class, key) == value)
        
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        if order_by and hasattr(self.model_class, order_by):
            order_column = getattr(self.model_class, order_by)
            if desc:
                order_column = order_column.desc()
            query = query.order_by(order_column)
        
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        result = await self.db.execute(query)
        items = result.scalars().all()
        
        return items, total
    
    async def create(self, obj: Any) -> T:
        """创建记录"""
        data = obj.model_dump() if hasattr(obj, 'model_dump') else obj
        db_obj = self.model_class(**data)
        self.db.add(db_obj)
        await self.db.flush()
        await self.db.refresh(db_obj)
        return db_obj
    
    async def update(self, id: int, obj: Any) -> Optional[T]:
        """更新记录"""
        db_obj = await self.get_by_id(id)
        if db_obj:
            data = obj.model_dump(exclude_unset=True) if hasattr(obj, 'model_dump') else obj
            for key, value in data.items():
                setattr(db_obj, key, value)
            await self.db.flush()
            await self.db.refresh(db_obj)
        return db_obj
    
    async def delete(self, id: int) -> bool:
        """删除记录"""
        db_obj = await self.get_by_id(id)
        if db_obj:
            await self.db.delete(db_obj)
            await self.db.flush()
            return True
        return False
