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
Batch task progress persistence

Handles storing and loading batch task progress to/from disk.
Storage location: config directory / batch_progress/
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from loguru import logger

from api.schemas.batch import (
    BatchProgress,
    ModuleStatus,
    ModuleStatusDetail,
    UnfinishedBatchInfo,
    GlobalConfig,
    BatchModuleRequest,
)


class BatchPersistence:
    """
    Batch task progress persistence manager
    
    Features:
    - Store batch task state to JSON files
    - Load and resume unfinished tasks
    - Auto cleanup of old completed tasks
    """
    
    def __init__(self, storage_dir: Optional[str] = None):
        if storage_dir is None:
            from api.config import api_config
            config_dir = Path(api_config.data_dir) / "batch_progress"
            storage_dir = config_dir
        
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Batch persistence initialized at: {self.storage_dir}")
    
    def _get_state_path(self, batch_id: str) -> Path:
        """Get path for batch state file"""
        return self.storage_dir / f"batch_{batch_id}_state.json"
    
    def _get_modules_path(self, batch_id: str) -> Path:
        """Get path for batch modules file"""
        return self.storage_dir / f"batch_{batch_id}_modules.json"
    
    def save_batch_state(
        self,
        batch_id: str,
        status: str,
        progress: BatchProgress,
        global_config: GlobalConfig,
        created_at: str,
        started_at: Optional[str] = None,
        completed_at: Optional[str] = None,
        current_module_index: int = -1,
    ) -> bool:
        """
        Save batch task state to disk
        
        Args:
            batch_id: Batch task ID
            status: Current status
            progress: Batch progress info
            global_config: Global configuration
            created_at: Creation timestamp (ISO format)
            started_at: Start timestamp (ISO format)
            completed_at: Completion timestamp (ISO format)
            current_module_index: Current executing module index
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            state_data = {
                "batch_id": batch_id,
                "status": status,
                "progress": progress.model_dump(),
                "global_config": global_config.model_dump(),
                "created_at": created_at,
                "started_at": started_at,
                "completed_at": completed_at,
                "current_module_index": current_module_index,
            }
            
            state_path = self._get_state_path(batch_id)
            with open(state_path, 'w', encoding='utf-8') as f:
                json.dump(state_data, f, ensure_ascii=False, indent=2)
            
            logger.debug(f"Saved batch state: {batch_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to save batch state {batch_id}: {e}")
            return False
    
    def save_modules_state(
        self,
        batch_id: str,
        modules: List[Dict[str, Any]]
    ) -> bool:
        """
        Save batch modules state to disk
        
        Args:
            batch_id: Batch task ID
            modules: List of module states
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            modules_path = self._get_modules_path(batch_id)
            with open(modules_path, 'w', encoding='utf-8') as f:
                json.dump({"modules": modules}, f, ensure_ascii=False, indent=2)
            
            logger.debug(f"Saved modules state: {batch_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to save modules state {batch_id}: {e}")
            return False
    
    def load_batch_state(self, batch_id: str) -> Optional[Dict[str, Any]]:
        """
        Load batch task state from disk
        
        Args:
            batch_id: Batch task ID
            
        Returns:
            Batch state dict or None if not found
        """
        try:
            state_path = self._get_state_path(batch_id)
            if not state_path.exists():
                return None
            
            with open(state_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load batch state {batch_id}: {e}")
            return None
    
    def load_modules_state(self, batch_id: str) -> Optional[List[Dict[str, Any]]]:
        """
        Load batch modules state from disk
        
        Args:
            batch_id: Batch task ID
            
        Returns:
            List of module states or None if not found
        """
        try:
            modules_path = self._get_modules_path(batch_id)
            if not modules_path.exists():
                return None
            
            with open(modules_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("modules", [])
        except Exception as e:
            logger.error(f"Failed to load modules state {batch_id}: {e}")
            return None
    
    def delete_batch(self, batch_id: str) -> bool:
        """
        Delete batch task files from disk
        
        Args:
            batch_id: Batch task ID
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            state_path = self._get_state_path(batch_id)
            modules_path = self._get_modules_path(batch_id)
            
            if state_path.exists():
                state_path.unlink()
            if modules_path.exists():
                modules_path.unlink()
            
            logger.info(f"Deleted batch files: {batch_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete batch {batch_id}: {e}")
            return False
    
    def get_unfinished_batches(self) -> List[UnfinishedBatchInfo]:
        """
        Get all unfinished batch tasks
        
        Returns:
            List of unfinished batch info
        """
        unfinished = []
        
        try:
            if not self.storage_dir.exists():
                return unfinished
            
            for state_file in self.storage_dir.glob("batch_*_state.json"):
                batch_id = state_file.stem.replace("batch_", "").replace("_state", "")
                state_data = self.load_batch_state(batch_id)
                
                if state_data is None:
                    continue
                
                status = state_data.get("status", "")
                if status in ["pending", "running"]:
                    progress_data = state_data.get("progress", {})
                    progress = BatchProgress(**progress_data)
                    
                    unfinished.append(UnfinishedBatchInfo(
                        batch_id=batch_id,
                        created_at=state_data.get("created_at", ""),
                        progress=progress,
                        module_count=progress.total
                    ))
        except Exception as e:
            logger.error(f"Failed to get unfinished batches: {e}")
        
        return unfinished
    
    def get_history_batches(self) -> List[Dict[str, Any]]:
        """
        Get all completed/failed/cancelled batch tasks for history
        
        Returns:
            List of batch info dicts with batch_id, created_at, completed_at, status
        """
        history = []
        
        try:
            if not self.storage_dir.exists():
                return history
            
            for state_file in self.storage_dir.glob("batch_*_state.json"):
                batch_id = state_file.stem.replace("batch_", "").replace("_state", "")
                state_data = self.load_batch_state(batch_id)
                
                if state_data is None:
                    continue
                
                status = state_data.get("status", "")
                if status in ["completed", "failed", "cancelled"]:
                    history.append({
                        "batch_id": batch_id,
                        "created_at": state_data.get("created_at", ""),
                        "completed_at": state_data.get("completed_at"),
                        "status": status,
                    })
        except Exception as e:
            logger.error(f"Failed to get history batches: {e}")
        
        history.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return history
    
    def cleanup_completed_batches(self, max_age_hours: int = 24) -> int:
        """
        Clean up old completed batch files
        
        Args:
            max_age_hours: Maximum age in hours for completed batches
            
        Returns:
            Number of batches cleaned up
        """
        cleaned = 0
        
        try:
            if not self.storage_dir.exists():
                return 0
            
            cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)
            
            for state_file in self.storage_dir.glob("batch_*_state.json"):
                try:
                    with open(state_file, 'r', encoding='utf-8') as f:
                        state_data = json.load(f)
                    
                    status = state_data.get("status", "")
                    completed_at = state_data.get("completed_at")
                    
                    if status in ["completed", "failed", "cancelled"] and completed_at:
                        try:
                            completed_time = datetime.fromisoformat(completed_at).timestamp()
                            if completed_time < cutoff_time:
                                batch_id = state_file.stem.replace("batch_", "").replace("_state", "")
                                self.delete_batch(batch_id)
                                cleaned += 1
                        except Exception:
                            logger.debug(f"Failed to parse completed_at timestamp for batch {batch_id}")
                except Exception:
                    logger.debug(f"Failed to read state file for cleanup: {state_file}")
        except Exception as e:
            logger.error(f"Failed to cleanup completed batches: {e}")
        
        if cleaned > 0:
            logger.info(f"Cleaned up {cleaned} old completed batches")
        
        return cleaned


batch_persistence = BatchPersistence()
