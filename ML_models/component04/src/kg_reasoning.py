"""Simple CSV triple-based knowledge graph reasoning baseline."""
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
TRIPLES=pd.read_csv(ROOT/"data"/"knowledge_graph_triples.csv")
def recommend(emergency_type, severity_level, rainfall_mm=0, visibility_pct=80, terrain_type="forest", remote_area=0):
    actions=set(TRIPLES.loc[TRIPLES["subject"]==emergency_type,"object"].astype(str))
    reasons=[]
    if rainfall_mm >= 30:
        actions.update(TRIPLES.loc[TRIPLES["subject"]=="heavy_rain","object"].astype(str))
        reasons.append("Heavy rainfall matched graph context.")
    if visibility_pct < 25:
        actions.update(TRIPLES.loc[TRIPLES["subject"]=="poor_visibility","object"].astype(str))
        reasons.append("Poor visibility matched graph context.")
    if terrain_type in ("steep","rocky","ridge"):
        actions.update(TRIPLES.loc[TRIPLES["subject"]=="steep_terrain","object"].astype(str))
        reasons.append("Difficult terrain matched graph context.")
    if remote_area:
        actions.update(TRIPLES.loc[TRIPLES["subject"]=="remote_area","object"].astype(str))
        reasons.append("Remote area matched graph context.")
    # Remove relation/metadata nodes and return candidate action-like nodes only.
    non_actions={"Hazard","ResponseAction","EmergencyType","ResponseCategory"}
    valid=set(pd.read_csv(ROOT/"data"/"knowledge_graph_triples.csv")["object"].astype(str))
    actions={a for a in actions if a not in non_actions and not a.endswith("_risk") and a not in {"EmergencyType","ResponseCategory"}}
    if severity_level >= 4:
        actions.add("contact_local_emergency_services")
        reasons.append("High severity triggers escalation advice.")
    return {"actions":sorted(actions),"reasoning":reasons}
if __name__=="__main__":
    print(recommend("lost_hiker",4,38,18,"forest",1))
