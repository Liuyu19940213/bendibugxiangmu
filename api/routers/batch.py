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
Batch task API endpoints

Provides batch video generation workflow management.
"""

from fastapi import APIRouter, HTTPException
from loguru import logger

from api.batch_manager import batch_manager
from api.batch_persistence import batch_persistence
from api.schemas.batch import (
    BatchRunRequest,
    BatchRunResponse,
    BatchStatusResponse,
    BatchCancelResponse,
    ModuleStatusResponse,
    ModuleStatusDetail,
    CheckUnfinishedResponse,
    ResumeBatchResponse,
    ResumeBatchRequest,
    ModuleStatus,
    BatchHistoryItem,
    BatchHistoryDetail,
    ModuleTraceMeta,
)


router = APIRouter(prefix="/batch", tags=["Batch Tasks"])


@router.post("/run", response_model=BatchRunResponse)
async def run_batch(request: BatchRunRequest):
    """
    Start a batch run
    
    Args:
        request: Batch run request with modules and global config
        
    Returns:
        Batch ID for tracking progress
    """
    try:
        if not request.modules:
            raise HTTPException(status_code=400, detail="No modules provided")
        
        enabled_modules = [m for m in request.modules if m.enabled]
        if not enabled_modules:
            raise HTTPException(status_code=400, detail="No enabled modules")
        
        batch_id = batch_manager.create_batch(
            modules=request.modules,
            global_config=request.global_config,
        )
        
        await batch_manager.start_batch(batch_id)
        
        logger.info(f"Batch {batch_id} started with {len(enabled_modules)} modules")
        
        return BatchRunResponse(
            success=True,
            message="批量任务已启动",
            batch_id=batch_id,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start batch: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{batch_id}", response_model=BatchStatusResponse)
async def get_batch_status(batch_id: str):
    """
    Get batch task status
    
    Args:
        batch_id: Batch task ID
        
    Returns:
        Batch status with progress and module details
    """
    batch_state = batch_manager.get_batch(batch_id)
    
    if not batch_state:
        state_data = batch_persistence.load_batch_state(batch_id)
        if state_data:
            batch_manager.load_unfinished_batch(batch_id)
            batch_state = batch_manager.get_batch(batch_id)
    
    if not batch_state:
        raise HTTPException(status_code=404, detail=f"Batch {batch_id} not found")
    
    progress = batch_manager.get_progress(batch_id)
    
    modules = [
        ModuleStatusDetail(
            id=m.id,
            book_name=m.book_name,
            status=m.status,
            enabled=m.enabled,
            error_message=m.error_message,
            sort_order=m.sort_order,
            result=m.result,
        )
        for m in batch_state.modules
    ]
    
    return BatchStatusResponse(
        batch_id=batch_id,
        status=batch_state.status,
        progress=progress,
        modules=modules,
        created_at=batch_state.created_at,
        started_at=batch_state.started_at,
        completed_at=batch_state.completed_at,
    )


@router.post("/{batch_id}/cancel", response_model=BatchCancelResponse)
async def cancel_batch(batch_id: str):
    """
    Cancel a batch task
    
    Args:
        batch_id: Batch task ID
        
    Returns:
        Cancellation confirmation
    """
    success = batch_manager.cancel_batch(batch_id)
    
    if not success:
        raise HTTPException(status_code=400, detail=f"Cannot cancel batch {batch_id}")
    
    logger.info(f"Batch {batch_id} cancelled")
    
    return BatchCancelResponse(
        success=True,
        message="批量任务已取消",
        batch_id=batch_id,
    )


@router.get("/{batch_id}/modules/{module_id}", response_model=ModuleStatusResponse)
async def get_module_status(batch_id: str, module_id: str):
    """
    Get status of a specific module in batch
    
    Args:
        batch_id: Batch task ID
        module_id: Module ID
        
    Returns:
        Module status detail
    """
    module_status = batch_manager.get_module_status(batch_id, module_id)
    
    if not module_status:
        batch_state = batch_manager.get_batch(batch_id)
        if not batch_state:
            raise HTTPException(status_code=404, detail=f"Batch {batch_id} not found")
        raise HTTPException(status_code=404, detail=f"Module {module_id} not found in batch {batch_id}")
    
    return ModuleStatusResponse(
        batch_id=batch_id,
        module=module_status,
    )


@router.get("/unfinished/check", response_model=CheckUnfinishedResponse)
async def check_unfinished():
    """
    Check for unfinished batch tasks
    
    Returns:
        List of unfinished batch tasks
    """
    try:
        in_memory_unfinished = batch_manager.get_unfinished_batches()
        
        disk_unfinished = batch_persistence.get_unfinished_batches()
        
        all_unfinished = []
        seen_ids = set()
        
        for b in in_memory_unfinished:
            if b["batch_id"] not in seen_ids:
                all_unfinished.append(b)
                seen_ids.add(b["batch_id"])
        
        for b in disk_unfinished:
            if b.batch_id not in seen_ids:
                all_unfinished.append({
                    "batch_id": b.batch_id,
                    "created_at": b.created_at,
                    "progress": b.progress.model_dump(),
                    "module_count": b.module_count,
                })
                seen_ids.add(b.batch_id)
        
        return CheckUnfinishedResponse(
            has_unfinished=len(all_unfinished) > 0,
            unfinished_batches=[
                batch_persistence.UnfinishedBatchInfo(**b) if isinstance(b, dict) else b
                for b in all_unfinished
            ] if all_unfinished else [],
        )
    except Exception as e:
        logger.error(f"Failed to check unfinished batches: {e}")
        return CheckUnfinishedResponse(has_unfinished=False, unfinished_batches=[])


@router.post("/resume", response_model=ResumeBatchResponse)
async def resume_batch(request: ResumeBatchRequest):
    """
    Resume an unfinished batch task
    
    Args:
        request: Resume batch request with batch ID
        
    Returns:
        Resume confirmation
    """
    try:
        if batch_manager.get_batch(request.batch_id):
            await batch_manager.start_batch(request.batch_id)
        else:
            loaded = batch_manager.load_unfinished_batch(request.batch_id)
            if not loaded:
                raise HTTPException(status_code=404, detail=f"Batch {request.batch_id} not found")
            await batch_manager.start_batch(request.batch_id)
        
        logger.info(f"Batch {request.batch_id} resumed")
        
        return ResumeBatchResponse(
            success=True,
            message="批量任务已恢复",
            batch_id=request.batch_id,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to resume batch: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{batch_id}")
async def delete_batch(batch_id: str):
    """
    Delete a batch task
    
    Args:
        batch_id: Batch task ID
        
    Returns:
        Deletion confirmation
    """
    success = batch_manager.delete_batch(batch_id)
    
    if not success:
        raise HTTPException(status_code=404, detail=f"Batch {batch_id} not found")
    
    logger.info(f"Batch {batch_id} deleted")
    
    return {"success": True, "message": "批量任务已删除", "batch_id": batch_id}


@router.get("/history/list", response_model=list[BatchHistoryItem])
async def get_batch_history():
    """
    Get all completed batch task history
    
    Returns:
        List of batch history items
    """
    try:
        items: list[BatchHistoryItem] = []
        history_batches = batch_persistence.get_history_batches()
        for b in history_batches:
            loaded = batch_manager.load_unfinished_batch(b["batch_id"])
            state = batch_manager.get_batch(b["batch_id"]) if loaded else None
            if state:
                items.append(BatchHistoryItem(
                    batch_id=state.batch_id,
                    created_at=state.created_at,
                    completed_at=state.completed_at,
                    status=state.status,
                    total_modules=len(state.modules),
                    completed_modules=len([m for m in state.modules if m.status == ModuleStatus.COMPLETED]),
                    failed_modules=len([m for m in state.modules if m.status == ModuleStatus.FAILED]),
                    global_config=state.global_config.model_dump() if state.global_config else None,
                ))
        return items
    except Exception as e:
        logger.error(f"Failed to get batch history: {e}")
        return []


@router.get("/history/{batch_id}", response_model=BatchHistoryDetail)
async def get_batch_history_detail(batch_id: str):
    """
    Get batch history detail with copy traceability metadata
    
    Args:
        batch_id: Batch task ID
        
    Returns:
        Batch history detail with traceability per module
    """
    loaded = batch_manager.load_unfinished_batch(batch_id)
    state = batch_manager.get_batch(batch_id) if loaded else None
    if not state:
        raise HTTPException(status_code=404, detail=f"Batch {batch_id} not found")

    modules: list[ModuleTraceMeta] = []
    for m in state.modules:
        result = m.result or {}
        trace = result.get("trace", {})
        modules.append(ModuleTraceMeta(
            source_hash=trace.get("source_hash", ""),
            originality=trace.get("originality"),
            reference_count=trace.get("reference_count", 0),
            char_count=trace.get("char_count", 0),
            rewrite_date=trace.get("rewrite_date"),
            book_name=m.book_name,
        ))

    return BatchHistoryDetail(
        batch_id=state.batch_id,
        created_at=state.created_at,
        started_at=state.started_at,
        completed_at=state.completed_at,
        status=state.status,
        global_config=state.global_config.model_dump() if state.global_config else None,
        modules=modules,
    )
