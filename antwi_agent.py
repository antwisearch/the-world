#!/usr/bin/env python3
"""
Antwi's Agent - LLM playing the turn-based game
Reads SKILL.md and takes actions autonomously
"""

import json
import requests

BASE_URL = "http://localhost:8080"
AGENT_ID = "7f209761"  # My agent ID

def get_my_status():
    """Get my current status"""
    resp = requests.get(f"{BASE_URL}/agent/{AGENT_ID}")
    data = resp.json()
    return data.get("agent", {})

def decide_actions(agent):
    """Decide what actions to take based on needs and inventory"""
    actions = []
    ap_remaining = 3
    
    needs = agent.get("needs", {})
    inventory = agent.get("inventory", {})
    
    # Strategy from SKILL.md:
    # 1. Balance needs - don't let any drop below 25%
    # 2. Gather early - build resource reserves
    # 3. Build shelter for survival
    
    # Priority 1: Check critical needs
    if needs.get("food", 100) < 30:
        actions.append({"action": "gather_food"})
        ap_remaining -= 1
    elif needs.get("water", 100) < 30:
        # Need to find water source first
        actions.append({"action": "rest"})  # Can't drink without water
        ap_remaining -= 1
    
    # Priority 2: Build resources for shelter (need 10 wood)
    wood = inventory.get("wood", 0)
    while ap_remaining > 0 and wood < 10:
        actions.append({"action": "gather_wood"})
        ap_remaining -= 1
        wood += 2
    
    # Use remaining AP
    while ap_remaining > 0:
        if needs.get("happiness", 100) < 50:
            actions.append({"action": "rest"})
        else:
            actions.append({"action": "gather_food"})  # Always good to have food
        ap_remaining -= 1
    
    return actions

def take_actions(actions):
    """Execute actions via WebSocket (simplified: use internal API)"""
    # For now, just print what I would do
    # In real implementation, would send via WebSocket
    print(f"Actions to take: {json.dumps(actions, indent=2)}")
    return actions

def main():
    print("=== Antwi's Agent ===")
    print("Reading SKILL.md and preparing actions...\n")
    
    # Get my status
    agent = get_my_status()
    print(f"Name: {agent.get('name')}")
    print(f"Job: {agent.get('job')}")
    print(f"Position: ({agent.get('position', {}).get('x')}, {agent.get('position', {}).get('y')})")
    print(f"Needs: {agent.get('needs')}")
    print(f"Inventory: {agent.get('inventory')}")
    print(f"Skills: {agent.get('skills')}")
    print()
    
    # Decide actions
    actions = decide_actions(agent)
    
    print("My turn - Actions (3 AP):")
    for i, action in enumerate(actions, 1):
        print(f"  {i}. {action['action']}")
    print()
    
    # Execute
    take_actions(actions)
    
    print("\nStrategy explanation:")
    print("- I have 2 wood, need 10 for shelter")
    print("- Gathering wood is priority")
    print("- Food needs at 80% - OK for now")
    print("- Will build shelter once I have 10 wood")

if __name__ == "__main__":
    main()