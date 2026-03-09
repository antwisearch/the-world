"""
Story Archive - Saves agent stories/diaries to JSON files
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional


class StoryArchive:
    """Manages agent story archives"""
    
    def __init__(self, base_dir: str = "stories"):
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)
    
    def _agent_dir(self, agent_id: str) -> str:
        """Get agent's story directory"""
        agent_dir = os.path.join(self.base_dir, f"agent_{agent_id}")
        os.makedirs(agent_dir, exist_ok=True)
        return agent_dir
    
    def save_diary(self, agent_id: str, agent_name: str, heartbeat: int, 
                   actions: List[Dict], diary: str, position: Dict,
                   mood: str = None, discovered: List[str] = None) -> str:
        """Save a diary entry for an agent"""
        
        entry = {
            "heartbeat": heartbeat,
            "timestamp": datetime.now().isoformat(),
            "agent_id": agent_id,
            "agent_name": agent_name,
            "position": position,
            "actions": actions,
            "diary": diary,
            "mood": mood or "neutral",
            "discovered": discovered or []
        }
        
        # Save to heartbeat file
        filename = f"hb_{heartbeat:04d}.json"
        filepath = os.path.join(self._agent_dir(agent_id), filename)
        
        with open(filepath, 'w') as f:
            json.dump(entry, f, indent=2)
        
        # Update agent's master file
        self._update_master(agent_id, agent_name, heartbeat)
        
        return filepath
    
    def _update_master(self, agent_id: str, agent_name: str, heartbeat: int):
        """Update agent's master index"""
        master_path = os.path.join(self._agent_dir(agent_id), "master.json")
        
        if os.path.exists(master_path):
            with open(master_path, 'r') as f:
                master = json.load(f)
        else:
            master = {
                "agent_id": agent_id,
                "agent_name": agent_name,
                "created": datetime.now().isoformat(),
                "heartbeats": [],
                "total_actions": 0
            }
        
        master["last_heartbeat"] = heartbeat
        master["heartbeats"].append(heartbeat)
        master["total_heartbeats"] = len(master["heartbeats"])
        
        with open(master_path, 'w') as f:
            json.dump(master, f, indent=2)
    
    def get_diary(self, agent_id: str, heartbeat: int) -> Optional[Dict]:
        """Get a specific diary entry"""
        filename = f"hb_{heartbeat:04d}.json"
        filepath = os.path.join(self._agent_dir(agent_id), filename)
        
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
        return None
    
    def get_all_diaries(self, agent_id: str, limit: int = 50) -> List[Dict]:
        """Get all diaries for an agent"""
        agent_dir = self._agent_dir(agent_id)
        diaries = []
        
        for filename in sorted(os.listdir(agent_dir)):
            if filename.startswith("hb_") and filename.endswith(".json"):
                filepath = os.path.join(agent_dir, filename)
                with open(filepath, 'r') as f:
                    diaries.append(json.load(f))
                
                if len(diaries) >= limit:
                    break
        
        return diaries
    
    def get_recent_events(self, limit: int = 100) -> List[Dict]:
        """Get recent events from all agents"""
        events = []
        
        for agent_id in os.listdir(self.base_dir):
            agent_dir = os.path.join(self.base_dir, agent_id)
            if os.path.isdir(agent_dir):
                # Get the latest diary
                diaries = self.get_all_diaries(agent_id.replace("agent_", ""), limit=1)
                if diaries:
                    events.append({
                        "agent_id": diaries[0]["agent_id"],
                        "agent_name": diaries[0]["agent_name"],
                        "heartbeat": diaries[0]["heartbeat"],
                        "diary_preview": diaries[0]["diary"][:200] + "..." if len(diaries[0]["diary"]) > 200 else diaries[0]["diary"],
                        "mood": diaries[0].get("mood", "neutral")
                    })
        
        # Sort by heartbeat descending
        events.sort(key=lambda x: x["heartbeat"], reverse=True)
        return events[:limit]
    
    def get_agent_summary(self, agent_id: str) -> Optional[Dict]:
        """Get summary of agent's story"""
        master_path = os.path.join(self._agent_dir(agent_id), "master.json")
        
        if os.path.exists(master_path):
            with open(master_path, 'r') as f:
                return json.load(f)
        return None
    
    def search_diaries(self, query: str, agent_id: str = None) -> List[Dict]:
        """Search diary entries for text"""
        results = []
        query_lower = query.lower()
        
        search_dirs = [self._agent_dir(agent_id)] if agent_id else [
            os.path.join(self.base_dir, d) 
            for d in os.listdir(self.base_dir)
            if os.path.isdir(os.path.join(self.base_dir, d))
        ]
        
        for search_dir in search_dirs:
            if not os.path.exists(search_dir):
                continue
                
            for filename in os.listdir(search_dir):
                if filename.startswith("hb_") and filename.endswith(".json"):
                    filepath = os.path.join(search_dir, filename)
                    with open(filepath, 'r') as f:
                        entry = json.load(f)
                        
                        if query_lower in entry.get("diary", "").lower():
                            results.append(entry)
        
        return results


# Global archive instance
archive = None

def get_archive(base_dir: str = "stories") -> StoryArchive:
    """Get or create the global archive"""
    global archive
    if archive is None:
        archive = StoryArchive(base_dir)
    return archive