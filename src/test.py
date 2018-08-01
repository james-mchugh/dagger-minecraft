import MalmoPython as mp
import time

agent = mp.AgentHost()
mission = mp.MissionSpec()
records = mp.MissionRecordSpec()

agent.startMission(mission, records)

world_state = agent.getWorldState()
while not world_state.has_mission_begun:
    time.sleep(1)
    world_state = agent.getWorldState()

obs = []
while world_state.is_mission_running:
    if world_state.observations:
        obs.append(str(world_state.observations[0]))
    world_state = agent.getWorldState()

with open("tmp.txt", "w") as f:
    f.write("\n".join(obs))
