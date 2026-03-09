"""
Disease System for The World
- Sickness spreading
- Doctors/healers treating patients
- Quarantine mechanics
- Health system
"""

import random
from dataclasses import dataclass
from typing import Optional, List, Dict


# Disease types
DISEASES = {
    "cold": {
        "name": "Common Cold",
        "severity": 1,
        "symptoms": ["sneezing", "coughing"],
        "contagious": True,
        "duration": 4,
        "mortality": 0.0,
    },
    "flu": {
        "name": "Influenza",
        "severity": 2,
        "symptoms": ["fever", "aches", "fatigue"],
        "contagious": True,
        "duration": 7,
        "mortality": 0.02,
    },
    "plague": {
        "name": "The Plague",
        "severity": 3,
        "symptoms": ["fever", "buboes", "delirium"],
        "contagious": True,
        "duration": 10,
        "mortality": 0.25,
    },
    "food_poisoning": {
        "name": "Food Poisoning",
        "severity": 2,
        "symptoms": ["vomiting", "diarrhea"],
        "contagious": False,
        "duration": 2,
        "mortality": 0.01,
    },
    "infection": {
        "name": "Infection",
        "severity": 2,
        "symptoms": ["swelling", "fever", "pain"],
        "contagious": False,
        "duration": 5,
        "mortality": 0.05,
    },
    "wounds": {
        "name": "Wounds",
        "severity": 1,
        "symptoms": ["bleeding", "pain"],
        "contagious": False,
        "duration": 4,
        "mortality": 0.02,
    },
}


@dataclass
class Disease:
    """A disease affecting an agent"""
    type: str
    days_remaining: int
    symptoms: List[str]
    severity: int


class DiseaseSystem:
    """Manages disease spread and treatment"""
    
    def __init__(self):
        self.quarantine_zone: Optional[tuple] = None
        self.quarantined_agents: List[str] = []
        self.outbreak_severity = 0  # 0-3
        
    def infect(self, agent, disease_type: str) -> bool:
        """Infect an agent with a disease"""
        if disease_type not in DISEASES:
            return False
        
        if not hasattr(agent, 'diseases'):
            agent.diseases = []
        
        # Check if already infected
        for d in agent.diseases:
            if d.type == disease_type:
                return False
        
        disease_data = DISEASES[disease_type]
        disease = Disease(
            type=disease_type,
            days_remaining=disease_data['duration'],
            symptoms=disease_data['symptoms'],
            severity=disease_data['severity']
        )
        agent.diseases.append(disease)
        
        # Reduce happiness
        agent.needs['happiness'] -= disease_data['severity'] * 10
        
        return True
    
    def spread_disease(self, agents: List, world=None) -> List[str]:
        """Process disease spread between agents"""
        events = []
        
        # Find infected agents
        infected = [a for a in agents if hasattr(a, 'diseases') and a.diseases]
        if not infected:
            return events
        
        for inf_agent in infected:
            for disease in inf_agent.diseases:
                disease_data = DISEASES[disease.type]
                
                # Check if contagious
                if not disease_data['contagious']:
                    continue
                
                # Spread to nearby agents
                for other in agents:
                    if other == inf_agent or not other.alive:
                        continue
                    
                    # Check distance (reduced from 20)
                    dist = ((inf_agent.x - other.x)**2 + (inf_agent.y - other.y)**2) ** 0.5
                    if dist > 30:  # Increased from 20
                        continue
                    
                    # Check quarantine
                    if other.biography.name in self.quarantined_agents:
                        continue
                    
                    # Random chance to infect (15% base, reduced from 30%)
                    chance = 0.15 * disease_data['severity']
                    if random.random() < chance:
                        if self.infect(other, disease.type):
                            if world:
                                world.log_event(f"🤒 {other.biography.name} caught {disease_data['name']}!")
                            events.append(f"{other.biography.name} infected with {disease.type}")
        
        return events
    
    def process_diseases(self, agents: List, world=None) -> List[str]:
        """Process disease progression each day"""
        events = []
        
        for agent in agents:
            if not hasattr(agent, 'diseases') or not agent.diseases:
                continue
            
            to_remove = []
            for disease in agent.diseases:
                disease.days_remaining -= 1
                
                # Check for death
                disease_data = DISEASES[disease.type]
                if random.random() < disease_data['mortality']:
                    agent.alive = False
                    agent.biography.record_death(f"died of {disease_data['name']}")
                    if world:
                        world.log_event(f"☠️ {agent.biography.name} died of {disease_data['name']}!")
                    events.append(f"{agent.biography.name} died of {disease.type}")
                    to_remove.append(disease)
                    continue
                
                # Check if cured
                if disease.days_remaining <= 0:
                    to_remove.append(disease)
                    agent.needs['happiness'] += 10  # Recovery bonus
            
            # Remove finished diseases
            for d in to_remove:
                if d in agent.diseases:
                    agent.diseases.remove(d)
        
        return events
    
    def heal_agent(self, healer, patient, world=None) -> str:
        """Healer treats a patient"""
        if not hasattr(healer, 'job') or healer.job != 'healer':
            return f"{healer.biography.name} is not a healer!"
        
        if not hasattr(patient, 'diseases') or not patient.diseases:
            return f"{patient.biography.name} is not sick!"
        
        # Healing effectiveness based on skill
        heal_power = healer.skills.get('healing', 10)
        
        # Use herbs if available
        herbs_used = 0
        if healer.inventory.get('herbs', 0) > 0:
            healer.inventory['herbs'] -= 1
            herbs_used = 1
            heal_power *= 1.5
        
        # Remove one disease
        disease = patient.diseases[0]
        patient.diseases.remove(disease)
        
        # Gain healing skill
        healer.skills['healing'] = min(100, healer.skills.get('healing', 10) + 2)
        
        # Restore some health
        if hasattr(patient, 'health'):
            patient.health = min(100, patient.health + heal_power)
        
        patient.needs['happiness'] += 15
        
        disease_name = DISEASES[disease.type]['name']
        
        if world:
            world.log_event(f"💊 {healer.biography.name} healed {patient.biography.name} of {disease_name}!")
        
        return f"{healer.biography.name} healed {patient.biography.name}!"
    
    def quarantine_agent(self, agent, world=None) -> str:
        """Quarantine a sick agent"""
        if not hasattr(agent, 'diseases') or not agent.diseases:
            return f"{agent.biography.name} is not sick!"
        
        if agent.biography.name in self.quarantined_agents:
            return f"{agent.biography.name} is already quarantined!"
        
        self.quarantined_agents.append(agent.biography.name)
        
        # Move to quarantine zone
        if not self.quarantine_zone:
            self.quarantine_zone = (50, 50)
        
        agent.x = self.quarantine_zone[0]
        agent.y = self.quarantine_zone[1]
        
        if world:
            world.log_event(f"🚫 {agent.biography.name} has been quarantined!")
        
        return f"{agent.biography.name} quarantined!"
    
    def release_quarantine(self, agent, world=None) -> str:
        """Release an agent from quarantine"""
        if agent.biography.name not in self.quarantined_agents:
            return f"{agent.biography.name} is not quarantined!"
        
        self.quarantined_agents.remove(agent.biography.name)
        
        if world:
            world.log_event(f"✅ {agent.biography.name} released from quarantine!")
        
        return f"{agent.biography.name} released from quarantine!"
    
    def trigger_plague(self, world, severity=2) -> str:
        """Trigger a plague outbreak"""
        if not world.agents:
            return "No agents to infect!"
        
        self.outbreak_severity = severity
        
        # Infect random agents
        infection_count = 0
        for agent in world.agents:
            if random.random() < 0.3 * severity:
                if self.infect(agent, 'plague'):
                    infection_count += 1
        
        if world:
            if severity >= 3:
                world.log_event(f"💀 A DEADLY PLAGUE HAS STRUCKEN! {infection_count} infected!")
            else:
                world.log_event(f"🤒 A plague has broken out! {infection_count} infected!")
        
        return f"Plague outbreak! {infection_count} infected."
    
    def get_sick_agents(self, agents: List) -> List:
        """Get list of sick agents"""
        return [a for a in agents if hasattr(a, 'diseases') and a.diseases]
    
    def get_quarantine_count(self) -> int:
        """Get number of quarantined agents"""
        return len(self.quarantined_agents)


# Global disease system instance
disease_system = DiseaseSystem()
