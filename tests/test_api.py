from fastapi.testclient import TestClient
from agnipariksha.api.main import app

client = TestClient(app)

def test_api_routing_digital_ic():
    with client as c:
        payload = []
        for i in range(8):
            payload.append({
                "lot_id": "LOT_API_DIGITAL",
                "component_id": f"COMP_API_{i}",
                "family": "DIGITAL_IC",
                "value_0h": 10.0,
                "value_24h": 10.0,
                "is_defective": 0,
                "mechanism": "NONE"
            })
        response = c.post("/lots/screen", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 8
        for d in data:
            if d['disposition'] != 'FULL_BURN_IN':
                print("TRIGGER FIELDS:", {k:v for k,v in d.items() if 'trigger' in k or 'verdict' in k})
            assert d['disposition'] == 'FULL_BURN_IN'

def test_api_routing_mems_gyroscope():
    with client as c:
        payload = []
        for i in range(8):
            payload.append({
                "lot_id": "LOT_API_MEMS",
                "component_id": f"COMP_API_{i}",
                "family": "MEMS_GYROSCOPE",
                "value_0h": 0.1,
                "value_24h": 0.101,
                "is_defective": 0,
                "mechanism": "NONE"
            })
        response = c.post("/lots/screen", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 8
        for d in data:
            if d['disposition'] != 'GREEN':
                print("TRIGGER FIELDS:", {k:v for k,v in d.items() if 'trigger' in k or 'verdict' in k})
            assert d['disposition'] == 'GREEN'

def test_api_metrics():
    with client as c:
        response = c.get("/metrics")
        assert response.status_code == 200
        data = response.json()
        assert "DIGITAL_IC" in data
