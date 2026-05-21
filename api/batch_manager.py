# Copyright (C) 2025 AIDC-AI
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Batch task manager

Manages batch task execution with persistence support.
"""

import asyncio
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from loguru import logger

from api.schemas.batch import (
    BatchProgress,
    ModuleStatus,
    ModuleStatusDetail,
    GlobalConfig,
    BatchModuleRequest,
)
from api.batch_persistence import batch_persistence


@dataclass
class BatchModuleState:
    """Internal module state"""
    id: str
    book_name: str
    raw_text: str
    enabled: bool
    status: ModuleStatus = ModuleStatus.IDLE
    error_message: Optional[str] = None
    config_override: Optional[Dict[str, Any]] = None
    sort_order: int = 0
    result: Optional[Dict[str, Any]] = None


@dataclass
class BatchState:
    """Internal batch task state"""
    batch_id: str
    global_config: GlobalConfig
    status: ModuleStatus = ModuleStatus.PENDING
    modules: List[BatchModuleState] = field(default_factory=list)
    created_at: str = ""
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    current_module_index: int = -1


class BatchManager:
    """
    Batch task manager for handling batch video generation
    
    Features:
    - In-memory storage with persistence
    - Sequential module execution
    - Progress tracking
    - Resume capability
    """
    
    def __init__(self):
        self._batches: Dict[str, BatchState] = {}
        self._batch_tasks: Dict[str, asyncio.Task] = {}
        self._running = False
        self._execution_callback: Optional[Callable] = None
    
    async def start(self):
        """Start batch manager"""
        if self._running:
            logger.warning("Batch manager already running")
            return
        
        self._running = True
        batch_persistence.cleanup_completed_batches()
        logger.info("✅ Batch manager started")
    
    async def stop(self):
        """Stop batch manager and cancel all tasks"""
        self._running = False
        
        for batch_id, task in self._batch_tasks.items():
            if not task.done():
                task.cancel()
                logger.info(f"Cancelled batch task: {batch_id}")
        
        self._batch_tasks.clear()
        logger.info("✅ Batch manager stopped")
    
    def set_execution_callback(self, callback: Callable):
        """
        Set callback for module execution
        
        Args:
            callback: Async function(module, global_config) -> result dict
        """
        self._execution_callback = callback
    
    def create_batch(
        self,
        modules: List[BatchModuleRequest],
        global_config: GlobalConfig
    ) -> str:
        """
        Create a new batch task
        
        Args:
            modules: List of module requests
            global_config: Global configuration
            
        Returns:
            Created batch ID
        """
        batch_id = str(uuid.uuid4())
        
        module_states = [
            BatchModuleState(
                id=m.id,
                book_name=m.book_name,
                raw_text=m.raw_text,
                enabled=m.enabled,
                config_override=m.config_override,
                sort_order=m.sort_order,
            )
            for m in modules
        ]
        
        batch_state = BatchState(
            batch_id=batch_id,
            global_config=global_config,
            modules=module_states,
            created_at=datetime.now().isoformat(),
        )
        
        self._batches[batch_id] = batch_state
        
        batch_persistence.save_batch_state(
            batch_id=batch_id,
            status=batch_state.status,
            progress=self.get_progress(batch_id),
            global_config=global_config,
            created_at=batch_state.created_at,
        )
        
        batch_persistence.save_modules_state(
            batch_id=batch_id,
            modules=self._modules_to_dict(batch_state.modules),
        )
        
        logger.info(f"Created batch {batch_id} with {len(modules)} modules")
        return batch_id
    
    def _modules_to_dict(self, modules: List[BatchModuleState]) -> List[Dict[str, Any]]:
        """Convert module states to dict list"""
        return [
            {
                "id": m.id,
                "book_name": m.book_name,
                "raw_text": m.raw_text,
                "enabled": m.enabled,
                "status": m.status,
                "error_message": m.error_message,
                "config_override": m.config_override,
                "sort_order": m.sort_order,
                "result": m.result,
            }
            for m in modules
        ]
    
    async def start_batch(self, batch_id: str) -> bool:
        """
        Start executing a batch task
        
        Args:
            batch_id: Batch task ID
            
        Returns:
            True if started, False otherwise
        """
        batch_state = self._batches.get(batch_id)
        if not batch_state:
            logger.error(f"Batch {batch_id} not found")
            return False
        
        if batch_state.status != ModuleStatus.PENDING:
            logger.warning(f"Batch {batch_id} is not in pending state")
            return False
        
        batch_state.status = ModuleStatus.RUNNING
        batch_state.started_at = datetime.now().isoformat()
        
        async def _execute_batch():
            await self._execute_modules(batch_id)
        
        task = asyncio.create_task(_execute_batch())
        self._batch_tasks[batch_id] = task
        
        self._persist_batch(batch_id)
        logger.info(f"Started batch execution: {batch_id}")
        return True
    
    async def _execute_modules(self, batch_id: str):
        """
        Execute all modules in batch sequentially
        
        Args:
            batch_id: Batch task ID
        """
        batch_state = self._batches.get(batch_id)
        if not batch_state:
            return
        
        enabled_modules = [m for m in batch_state.modules if m.enabled]
        total_modules = len(enabled_modules)
        
        logger.info(f"Executing batch {batch_id}: {total_modules} modules")
        
        try:
            for idx, module in enumerate(enabled_modules):
                if not self._running:
                    logger.info(f"Batch {batch_id} interrupted")
                    break
                
                batch_state.current_module_index = idx
                module.status = ModuleStatus.RUNNING
                
                self._persist_batch(batch_id)
                self._report_progress(batch_id)
                
                try:
                    logger.info(f"Batch {batch_id}: Executing module {idx + 1}/{total_modules}: {module.book_name}")
                    
                    if self._execution_callback:
                        result = await self._execution_callback(
                            module=module,
                            global_config=batch_state.global_config,
                            batch_id=batch_id,
                            module_index=idx,
                            total_modules=total_modules,
                        )
                        module.result = result
                        module.status = ModuleStatus.COMPLETED
                        logger.info(f"Batch {batch_id}: Module {module.book_name} completed")
                    else:
                        module.status = ModuleStatus.SKIPPED
                        module.error_message = "No execution callback configured"
                        logger.warning(f"Batch {batch_id}: No execution callback")
                
                except Exception as e:
                    module.status = ModuleStatus.FAILED
                    module.error_message = str(e)
                    logger.error(f"Batch {batch_id}: Module {module.book_name} failed: {e}")
                
                self._persist_batch(batch_id)
                self._report_progress(batch_id)
            
            enabled_modules = [m for m in batch_state.modules if m.enabled]
            if all(m.status in [ModuleStatus.COMPLETED, ModuleStatus.FAILED, ModuleStatus.SKIPPED] 
                   for m in enabled_modules):
                batch_state.status = ModuleStatus.COMPLETED
                batch_state.completed_at = datetime.now().isoformat()
            else:
                batch_state.status = ModuleStatus.RUNNING
            
        except Exception as e:
            logger.error(f"Batch {batch_id} execution error: {e}")
            batch_state.status = ModuleStatus.FAILED
            batch_state.completed_at = datetime.now().isoformat()
        
        self._persist_batch(batch_id)
        self._report_progress(batch_id)
        logger.info(f"Batch {batch_id} execution finished: {batch_state.status}")
    
    def _persist_batch(self, batch_id: str):
        """Persist batch state to disk"""
        batch_state = self._batches.get(batch_id)
        if not batch_state:
            return
        
        batch_persistence.save_batch_state(
            batch_id=batch_id,
            status=batch_state.status,
            progress=self.get_progress(batch_id),
            global_config=batch_state.global_config,
            created_at=batch_state.created_at,
            started_at=batch_state.started_at,
            completed_at=batch_state.completed_at,
            current_module_index=batch_state.current_module_index,
        )
        
        batch_persistence.save_modules_state(
            batch_id=batch_id,
            modules=self._modules_to_dict(batch_state.modules),
        )
    
    def _report_progress(self, batch_id: str):
        """Report progress via callback if configured"""
        pass
    
    def get_batch(self, batch_id: str) -> Optional[BatchState]:
        """Get batch by ID"""
        return self._batches.get(batch_id)
    
    def get_progress(self, batch_id: str) -> BatchProgress:
        """
        Get batch progress
        
        Args:
            batch_id: Batch task ID
            
        Returns:
            Batch progress
        """
        batch_state = self._batches.get(batch_id)
        if not batch_state:
            return BatchProgress()
        
        modules = batch_state.modules
        total = len([m for m in modules if m.enabled])
        completed = len([m for m in modules if m.status == ModuleStatus.COMPLETED])
        failed = len([m for m in modules if m.status == ModuleStatus.FAILED])
        skipped = len([m for m in modules if m.status == ModuleStatus.SKIPPED])
        
        current_module = None
        current_module_id = None
        if 0 <= batch_state.current_module_index < len(modules):
            current_module = modules[batch_state.current_module_index]
            if current_module.enabled:
                current_module_id = current_module.id
        
        percent = (completed / total * 100) if total > 0 else 0
        
        return BatchProgress(
            total=total,
            completed=completed,
            failed=failed,
            skipped=skipped,
            current_book=current_module.book_name if current_module else None,
            percent=round(percent, 1),
            current_module_id=current_module_id,
        )
    
    def get_module_status(self, batch_id: str, module_id: str) -> Optional[ModuleStatusDetail]:
        """
        Get status of a specific module
        
        Args:
            batch_id: Batch task ID
            module_id: Module ID
            
        Returns:
            Module status detail or None
        """
        batch_state = self._batches.get(batch_id)
        if not batch_state:
            return None
        
        for module in batch_state.modules:
            if module.id == module_id:
                return ModuleStatusDetail(
                    id=module.id,
                    book_name=module.book_name,
                    status=module.status,
                    enabled=module.enabled,
                    error_message=module.error_message,
                    sort_order=module.sort_order,
                    result=module.result,
                )
        
        return None
    
    def cancel_batch(self, batch_id: str) -> bool:
        """
        Cancel a batch task
        
        Args:
            batch_id: Batch task ID
            
        Returns:
            True if cancelled, False otherwise
        """
        batch_state = self._batches.get(batch_id)
        if not batch_state:
            return False
        
        if batch_state.status in [ModuleStatus.COMPLETED, ModuleStatus.FAILED, ModuleStatus.CANCELLED]:
            return False
        
        task = self._batch_tasks.get(batch_id)
        if task and not task.done():
            task.cancel()
        
        batch_state.status = ModuleStatus.CANCELLED
        batch_state.completed_at = datetime.now().isoformat()
        
        for module in batch_state.modules:
            if module.status in [ModuleStatus.PENDING, ModuleStatus.RUNNING]:
                module.status = ModuleStatus.SKIPPED
        
        self._persist_batch(batch_id)
        logger.info(f"Cancelled batch: {batch_id}")
        return True
    
    def load_unfinished_batch(self, batch_id: str) -> bool:
        """
        Load an unfinished batch from disk
        
        Args:
            batch_id: Batch task ID
            
        Returns:
            True if loaded, False otherwise
        """
        state_data = batch_persistence.load_batch_state(batch_id)
        if not state_data:
            return False
        
        modules_data = batch_persistence.load_modules_state(batch_id)
        if not modules_data:
            return False
        
        try:
            global_config = GlobalConfig(**state_data.get("global_config", {}))
            
            module_states = []
            for m in modules_data:
                module_states.append(BatchModuleState(
                    id=m["id"],
                    book_name=m["book_name"],
                    raw_text=m.get("raw_text", ""),
                    enabled=m.get("enabled", True),
                    status=m.get("status", "idle"),
                    error_message=m.get("error_message"),
                    config_override=m.get("config_override"),
                    sort_order=m.get("sort_order", 0),
                    result=m.get("result"),
                ))
            
            batch_state = BatchState(
                batch_id=batch_id,
                global_config=global_config,
                status=state_data.get("status", "pending"),
                modules=module_states,
                created_at=state_data.get("created_at", ""),
                started_at=state_data.get("started_at"),
                completed_at=state_data.get("completed_at"),
                current_module_index=state_data.get("current_module_index", -1),
            )
            
            self._batches[batch_id] = batch_state
            logger.info(f"Loaded unfinished batch: {batch_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to load batch {batch_id}: {e}")
            return False
    
    def get_unfinished_batches(self) -> List[Dict[str, Any]]:
        """
        Get all unfinished batches
        
        Returns:
            List of unfinished batch info
        """
        return [
            {
                "batch_id": b.batch_id,
                "created_at": b.created_at,
                "progress": self.get_progress(b.batch_id).model_dump(),
                "module_count": len(b.modules),
            }
            for b in self._batches.values()
            if b.status in [ModuleStatus.PENDING, ModuleStatus.RUNNING]
        ]
    
    def delete_batch(self, batch_id: str) -> bool:
        """
        Delete a batch from memory and disk
        
        Args:
            batch_id: Batch task ID
            
        Returns:
            True if deleted, False otherwise
        """
        if batch_id in self._batches:
            del self._batches[batch_id]
        
        if batch_id in self._batch_tasks:
            task = self._batch_tasks[batch_id]
            if not task.done():
                task.cancel()
            del self._batch_tasks[batch_id]
        
        batch_persistence.delete_batch(batch_id)
        logger.info(f"Deleted batch: {batch_id}")
        return True


batch_manager = BatchManager()
