#!/usr/bin/env python3
"""Mock API server for testing OpenWebUI endpoints."""

from fastapi import FastAPI, HTTPException
from typing import List, Dict, Any
import uvicorn

app = FastAPI(title="Mock OpenWebUI API")

# Mock data
mock_groups = [
    {"id": "1", "name": "Demo Group A", "description": "Demo group for testing"},
    {"id": "2", "name": "Demo Group B", "description": "Another demo group"},
]

mock_users = [
    {"id": "1", "email": "demo@example.com", "name": "Demo User"},
]

mock_group_users = {
    "1": [{"id": "1", "email": "demo@example.com", "name": "Demo User"}],
    "2": [],
}

@app.get("/api/v1/groups")
async def list_groups() -> List[Dict[str, Any]]:
    """List all groups."""
    print(f"Received request for groups: {mock_groups}")
    return mock_groups

@app.get("/api/v1/users")
async def list_users() -> List[Dict[str, Any]]:
    """List all users."""
    return mock_users

@app.get("/api/v1/groups/{group_id}/users")
async def list_group_users(group_id: str) -> List[Dict[str, Any]]:
    """List users in a group."""
    if group_id not in mock_group_users:
        raise HTTPException(status_code=404, detail="Group not found")
    return mock_group_users[group_id]

@app.post("/api/v1/groups/{group_id}/users/add")
async def add_user_to_group(group_id: str, user_data: Dict[str, Any]):
    """Add user to group."""
    if group_id not in mock_group_users:
        raise HTTPException(status_code=404, detail="Group not found")
    
    user_id = user_data.get("user_id")
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")
    
    # Mock: add user to group
    if user_id not in [u["id"] for u in mock_group_users[group_id]]:
        user = next((u for u in mock_users if u["id"] == user_id), None)
        if user:
            mock_group_users[group_id].append(user)
    
    return {"message": "User added to group"}

@app.delete("/api/v1/groups/{group_id}/users/{user_id}/remove")
async def remove_user_from_group(group_id: str, user_id: str):
    """Remove user from group."""
    if group_id not in mock_group_users:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Mock: remove user from group
    mock_group_users[group_id] = [u for u in mock_group_users[group_id] if u["id"] != user_id]
    
    return {"message": "User removed from group"}

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8081)
