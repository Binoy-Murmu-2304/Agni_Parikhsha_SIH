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

def test_api_risk_tier_assertions():
    with client as c:
        res_lots = c.get("/lots")
        assert res_lots.status_code == 200
        lots = res_lots.json()
        assert len(lots) > 0
        
        for lot in lots[:3]:
            lot_id = lot['lot_id']
            res_comps = c.get(f"/lots/{lot_id}/components?per_page=200")
            assert res_comps.status_code == 200
            comps = res_comps.json().get('components', [])
            for comp in comps:
                assert comp['risk_tier'] in ('HIGH', 'MEDIUM', 'LOW'), f"Invalid risk_tier: {comp.get('risk_tier')}"
                assert comp['risk_tier'] is not None
                assert str(comp['risk_tier']).upper() != 'NAN'

        if len(lots) > 0:
            first_lot_id = lots[0]['lot_id']
            res_comps = c.get(f"/lots/{first_lot_id}/components?per_page=1")
            comps = res_comps.json().get('components', [])
            if len(comps) > 0:
                cid = comps[0]['component_id']
                res_c = c.get(f"/components/{cid}")
                assert res_c.status_code == 200
                comp_detail = res_c.json()
                assert comp_detail['risk_tier'] in ('HIGH', 'MEDIUM', 'LOW')
                assert str(comp_detail['risk_tier']).upper() != 'NAN'

def test_api_lot_report():
    with client as c:
        res_lots = c.get("/lots")
        assert res_lots.status_code == 200
        lots = res_lots.json()
        assert len(lots) > 0
        first_lot = lots[0]['lot_id']

        # Single lot report
        res_rpt = c.get(f"/lots/{first_lot}/report")
        assert res_rpt.status_code == 200
        assert res_rpt.headers["content-type"] == "application/pdf"
        assert len(res_rpt.content) > 1000

        # Fleet report
        res_fleet = c.get("/lots/all/report")
        assert res_fleet.status_code == 200
        assert res_fleet.headers["content-type"] == "application/pdf"
        assert len(res_fleet.content) > 1000



