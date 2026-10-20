"""
Domain Knowledge Graph Reasoning Engine for Hiking Emergencies (Component 4)
Uses NetworkX to construct an ontological directed graph from knowledge_graph_triples.csv
Performs multi-hop reasoning connecting environmental context, emergency categories, hazards, and response actions.
"""
from pathlib import Path
from typing import Dict, List, Any
import networkx as nx
import pandas as pd

class KnowledgeGraphEngine:
    def __init__(self, data_path: Path = None):
        if data_path is None:
            # Look in standard locations
            current_dir = Path(__file__).resolve().parent
            candidate = current_dir / "data" / "knowledge_graph_triples.csv"
            if not candidate.exists():
                candidate = current_dir.parent.parent / "datasets" / "component04" / "knowledge_graph_triples.csv"
            self.data_path = candidate
        else:
            self.data_path = Path(data_path)

        self.graph = nx.DiGraph()
        self._load_graph()

    def _load_graph(self):
        if not self.data_path.exists():
            raise FileNotFoundError(f"Knowledge Graph triples file not found at: {self.data_path}")

        df = pd.read_csv(self.data_path)
        for _, row in df.iterrows():
            sub = str(row["subject"]).strip()
            rel = str(row["relation"]).strip()
            obj = str(row["object"]).strip()
            obj_type = str(row["object_type"]).strip() if "object_type" in row and pd.notna(row["object_type"]) else "General"
            
            self.graph.add_node(sub)
            self.graph.add_node(obj, node_type=obj_type)
            self.graph.add_edge(sub, obj, relation=rel)

    def recommend(
        self,
        emergency_type: str,
        severity_level: int,
        rainfall_mm: float = 0,
        visibility_pct: float = 80,
        terrain_type: str = "forest",
        remote_area: int = 0,
        phone_battery_pct: float = 50,
        temperature_c: float = 24
    ) -> Dict[str, Any]:
        """
        Executes multi-hop traversal to derive prioritized response actions and reasoning paths.
        """
        actions_with_priority = []
        reasoning_paths = []
        active_hazards = []

        # 1. Direct Emergency Type Actions
        if self.graph.has_node(emergency_type):
            for neighbor in self.graph.neighbors(emergency_type):
                edge_data = self.graph.get_edge_data(emergency_type, neighbor)
                rel = edge_data.get("relation", "relates_to")
                if neighbor not in {"ResponseCategory", "EmergencyType"} and not neighbor.endswith("_risk"):
                    actions_with_priority.append((neighbor, 2))  # Base priority 2
                    reasoning_paths.append(f"({emergency_type}) --[{rel}]--> ({neighbor})")

        # 2. Contextual Inferences: Weather, Terrain, and Environmental Hazards
        context_triggers = []
        if rainfall_mm >= 30:
            context_triggers.append("heavy_rain")
        if visibility_pct < 25:
            context_triggers.append("poor_visibility")
        if str(terrain_type).lower() in {"steep", "rocky", "ridge"}:
            context_triggers.append("steep_terrain")
        if remote_area == 1:
            context_triggers.append("remote_area")
        if phone_battery_pct < 20:
            context_triggers.append("low_battery")
        if temperature_c >= 33:
            context_triggers.append("high_temperature")

        # Traverse: Context -> Hazard -> Suggested Action (Multi-hop)
        for trigger in context_triggers:
            if self.graph.has_node(trigger):
                for hazard in self.graph.neighbors(trigger):
                    h_edge = self.graph.get_edge_data(trigger, hazard).get("relation", "may_indicate")
                    active_hazards.append(hazard)
                    reasoning_paths.append(f"({trigger}) --[{h_edge}]--> ({hazard})")

                    for action in self.graph.neighbors(hazard):
                        a_edge = self.graph.get_edge_data(hazard, action).get("relation", "suggests")
                        actions_with_priority.append((action, 1))  # Hazard-induced actions take High Priority 1
                        reasoning_paths.append(f"({hazard}) --[{a_edge}]--> ({action})")

        # 3. Urgency & Severity Escalation Rule
        if severity_level >= 4:
            actions_with_priority.append(("contact_local_emergency_services", 1))
            reasoning_paths.append(f"(Severity: {severity_level}/5 >= 4) --[triggers_escalation]--> (contact_local_emergency_services)")
        elif severity_level == 3:
            actions_with_priority.append(("notify_trail_contact_and_prepare_evacuation", 2))
            reasoning_paths.append(f"(Severity: 3/5 Moderate) --[triggers_alert]--> (notify_trail_contact_and_prepare_evacuation)")

        # Prioritize, deduplicate while preserving priority
        seen = set()
        sorted_actions = []
        # Sort by priority ascending (1 = highest priority)
        actions_with_priority.sort(key=lambda x: x[1])
        for act, priority in actions_with_priority:
            if act not in seen and act not in {"ResponseAction", "Hazard", "EmergencyType", "ResponseCategory"}:
                seen.add(act)
                sorted_actions.append(act)

        # Fallback if empty
        if not sorted_actions:
            sorted_actions = ["share_gps_location", "contact_rescue_authority", "stay_in_safe_location"]
            reasoning_paths.append("(Fallback) --[default_safety]--> (share_gps_location)")

        return {
            "emergency_type": emergency_type,
            "severity_level": severity_level,
            "actions": sorted_actions,
            "reasoning_paths": reasoning_paths,
            "active_hazards": list(set(active_hazards)),
            "graph_node_count": self.graph.number_of_nodes(),
            "graph_edge_count": self.graph.number_of_edges()
        }

if __name__ == "__main__":
    engine = KnowledgeGraphEngine()
    result = engine.recommend("lost_hiker", 4, rainfall_mm=38, visibility_pct=18, terrain_type="forest", remote_area=1)
    print("Derived Actions:", result["actions"])
    print("Reasoning Paths:")
    for path in result["reasoning_paths"]:
        print("  *", path)
