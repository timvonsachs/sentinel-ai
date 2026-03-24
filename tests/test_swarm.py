from sentinel.systems.swarm import SwarmSystem


def test_swarm_broadcast_returns_delivery():
    swarm = SwarmSystem()
    result = swarm.broadcast({"hello": "world"})
    assert result["delivered"] is True
