"""
Base repository with common CRUD operations.
Provides a foundation for all repositories.
"""

from typing import TypeVar, Generic, Optional, List, Type, Any, Dict
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from ..core.logging_config import get_logger
import uuid

from ...db.base import Base
from ...core.result import Result, Ok, Err

logger = get_logger(__name__)

T = TypeVar('T', bound=Base)


class BaseRepository(Generic[T]):
    """
    Base repository providing common CRUD operations.
    
    This class implements basic database operations that can be
    inherited by specific repositories.
    """
    
    def __init__(self, model: Type[T], db: Session):
        """
        Initialize base repository.
        
        Args:
            model: SQLAlchemy model class
            db: Database session
        """
        self.model = model
        self.db = db
    
    def create(self, entity: T) -> Result[T, str]:
        """
        Create a new entity.
        
        Args:
            entity: Entity to create
            
        Returns:
            Result containing created entity or error
        """
        try:
            self.db.add(entity)
            self.db.flush()
            return Ok(entity)
        except SQLAlchemyError as e:
            logger.error(f"Failed to create {self.model.__name__}: {e}")
            self.db.rollback()
            return Err(str(e))
    
    def get_by_id(self, entity_id: Any) -> Result[Optional[T], str]:
        """
        Get entity by ID.
        
        Args:
            entity_id: Entity ID (can be string or UUID)
            
        Returns:
            Result containing entity or None if not found
        """
        try:
            # Note: Our models use String IDs with UUID defaults,
            # so we keep entity_id as string for consistency
            # The database will handle the comparison correctly
            if isinstance(entity_id, uuid.UUID):
                entity_id = str(entity_id)
            
            entity = self.db.query(self.model).filter(
                self.model.id == entity_id
            ).first()
            return Ok(entity)
        except SQLAlchemyError as e:
            logger.error(f"Failed to get {self.model.__name__} by id {entity_id}: {e}")
            return Err(str(e))
    
    def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> Result[List[T], str]:
        """
        Get all entities with optional filtering and pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            filters: Optional dictionary of filters
            
        Returns:
            Result containing list of entities or error
        """
        try:
            query = self.db.query(self.model)
            
            # Apply filters if provided
            if filters:
                for key, value in filters.items():
                    if hasattr(self.model, key):
                        query = query.filter(getattr(self.model, key) == value)
            
            entities = query.offset(skip).limit(limit).all()
            return Ok(entities)
        except SQLAlchemyError as e:
            logger.error(f"Failed to get all {self.model.__name__}: {e}")
            return Err(str(e))
    
    def update(self, entity: T) -> Result[T, str]:
        """
        Update an existing entity.
        
        This method fetches the existing entity from the database and updates its fields.
        If the entity does not exist, an error is returned.
        
        Args:
            entity: Entity with updated values (must have 'id' attribute)
            
        Returns:
            Result containing updated entity or error
        
        Note:
            The entity must exist in the database. For create-or-update behavior,
            use the merge_entity() method instead.
        """
        try:
            # Ensure entity has an ID
            if not hasattr(entity, 'id') or entity.id is None:
                return Err(f"{self.model.__name__} must have an id for update")
            
            # Fetch the existing entity from database
            db_entity = self.db.query(self.model).filter(
                self.model.id == entity.id
            ).first()
            
            if not db_entity:
                return Err(f"{self.model.__name__} with id {entity.id} not found")
            
            # Update fields from the provided entity
            for column in self.model.__table__.columns:
                column_name = column.name
                # Skip primary key and system fields
                if column_name == 'id' or column_name.startswith('_'):
                    continue
                    
                if hasattr(entity, column_name):
                    setattr(db_entity, column_name, getattr(entity, column_name))
            
            self.db.flush()
            return Ok(db_entity)
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to update {self.model.__name__}: {e}")
            self.db.rollback()
            return Err(str(e))
    
    def delete(self, entity: T) -> Result[bool, str]:
        """
        Delete an entity.
        
        Args:
            entity: Entity to delete
            
        Returns:
            Result containing success boolean or error
        """
        try:
            self.db.delete(entity)
            self.db.flush()
            return Ok(True)
        except SQLAlchemyError as e:
            logger.error(f"Failed to delete {self.model.__name__}: {e}")
            self.db.rollback()
            return Err(str(e))
    
    def delete_by_id(self, entity_id: Any) -> Result[bool, str]:
        """
        Delete entity by ID.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            Result containing success boolean or error
        """
        try:
            result = self.get_by_id(entity_id)
            if result.is_err():
                return Err(result.unwrap_err())
            
            entity = result.unwrap()
            if not entity:
                return Err(f"{self.model.__name__} not found")
            
            return self.delete(entity)
        except SQLAlchemyError as e:
            logger.error(f"Failed to delete {self.model.__name__} by id {entity_id}: {e}")
            return Err(str(e))
    
    def exists(self, entity_id: Any) -> Result[bool, str]:
        """
        Check if entity exists by ID.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            Result containing existence boolean or error
        """
        try:
            # Convert UUID to string if needed for consistency
            if isinstance(entity_id, uuid.UUID):
                entity_id = str(entity_id)
            
            exists = self.db.query(
                self.db.query(self.model).filter(
                    self.model.id == entity_id
                ).exists()
            ).scalar()
            return Ok(exists)
        except SQLAlchemyError as e:
            logger.error(f"Failed to check existence of {self.model.__name__}: {e}")
            return Err(str(e))
    
    def count(self, filters: Optional[Dict[str, Any]] = None) -> Result[int, str]:
        """
        Count entities with optional filtering.
        
        Args:
            filters: Optional dictionary of filters
            
        Returns:
            Result containing count or error
        """
        try:
            query = self.db.query(self.model)
            
            # Apply filters if provided
            if filters:
                for key, value in filters.items():
                    if hasattr(self.model, key):
                        query = query.filter(getattr(self.model, key) == value)
            
            count = query.count()
            return Ok(count)
        except SQLAlchemyError as e:
            logger.error(f"Failed to count {self.model.__name__}: {e}")
            return Err(str(e))
    
    def commit(self) -> Result[bool, str]:
        """
        Commit the current transaction.
        
        Returns:
            Result containing success boolean or error
        """
        try:
            self.db.commit()
            return Ok(True)
        except SQLAlchemyError as e:
            logger.error(f"Failed to commit transaction: {e}")
            self.db.rollback()
            return Err(str(e))
    
    def rollback(self) -> None:
        """Rollback the current transaction."""
        self.db.rollback()
    
    def merge_entity(self, entity: T) -> Result[T, str]:
        """
        Merge an entity (create or update based on existence).
        
        This method uses SQLAlchemy's merge() which will:
        - Create the entity if it doesn't exist
        - Update it if it exists (based on primary key)
        
        Args:
            entity: Entity to merge
            
        Returns:
            Result containing merged entity or error
        
        Warning:
            Use this method carefully as it can create new records
            if the entity's ID doesn't exist in the database.
        """
        try:
            merged_entity = self.db.merge(entity)
            self.db.flush()
            return Ok(merged_entity)
        except SQLAlchemyError as e:
            logger.error(f"Failed to merge {self.model.__name__}: {e}")
            self.db.rollback()
            return Err(str(e))