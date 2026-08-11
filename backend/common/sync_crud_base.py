"""
文件路径: /backend/common/sync_crud_base.py
功能描述: 核心基础类定义（同步后台业务通道）
主要功能:
    - 提供 BaseService 服务基类
    - 通用 CRUD 操作封装（同步版本）
"""
from typing import TypeVar, Generic, Optional, List, Any, Tuple
from sqlalchemy import select, func
from sqlalchemy.orm import Session

T = TypeVar('T')


class SyncBaseCRUD(Generic[T]):
    """
    服务基类
    
    提供通用的 CRUD 操作（同步版本）
    """
    
    def __init__(self, db: Session, model_class: type):
        self.db = db
        self.model_class = model_class
    
    def get_by_id(self, id: int) -> Optional[T]:
        """获取单个记录"""
        # 同步模式下，直接使用 db.get 是最高效的主键查询方式
        return self.db.get(self.model_class, id)
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """获取所有记录"""
        result = self.db.execute(
            select(self.model_class).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    def list(
        self, 
        page: int = 1, 
        page_size: int = 20, 
        filters: dict = None, 
        order_by: str = None, 
        desc: bool = False
    ) -> Tuple[List[T], int]:
        """分页查询列表"""
        query = select(self.model_class)
        
        if filters:
            for key, value in filters.items():
                if value is not None:
                    query = query.where(getattr(self.model_class, key) == value)
        
        # 计算总记录数
        # 同步模式下，直接使用 db.execute 是最高效的查询方式
        # 注意：这里使用 subquery 是为了避免重复计算子查询结果
        count_query = select(func.count()).select_from(query.subquery())
        total_result = self.db.execute(count_query)
        total = total_result.scalar()
        
        # 排序
        if order_by and hasattr(self.model_class, order_by):
            order_column = getattr(self.model_class, order_by)
            if desc:
                order_column = order_column.desc()
            query = query.order_by(order_column)
        
        # 分页查询
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        result = self.db.execute(query)
        items = list(result.scalars().all())
        
        return items, total
    
    def create(self, obj: Any) -> T:
        """创建记录"""
        data = obj.model_dump() if hasattr(obj, 'model_dump') else obj
        db_obj = self.model_class(**data)
        self.db.add(db_obj)
        self.db.flush()
        self.db.refresh(db_obj)
        return db_obj
    
    def update(self, id: int, obj: Any) -> Optional[T]:
        """更新记录"""
        db_obj = self.get_by_id(id)
        if db_obj:
            data = obj.model_dump(exclude_unset=True) if hasattr(obj, 'model_dump') else obj
            for key, value in data.items():
                setattr(db_obj, key, value)
            self.db.flush()
            self.db.refresh(db_obj)
        return db_obj
    
    def delete(self, id: int) -> bool:
        """删除记录"""
        db_obj = self.get_by_id(id)
        if db_obj:
            self.db.delete(db_obj)
            self.db.flush()
            return True
        return False
