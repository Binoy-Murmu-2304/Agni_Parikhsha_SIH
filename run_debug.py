from fastapi.testclient import TestClient
from agnipariksha.api.main import app

client = TestClient(app)

with client as c:
    payload = [{
        "lot_id": "LOT_API",
        "component_id": "COMP_API_1",
        "family": "DIGITAL_IC",
        "value_0h": 10.0,
        "value_24h": 10.0,
        "is_defective": 0,
        "mechanism": "NONE"
    }]
    response = c.post("/lots/screen", json=payload)
    data = response.json()
    print(data)
