from pathlib import Path
from agnipariksha.qa_cards.pdf_export import generate_pdf_certificate

def test_deterministic_pdf_render(tmp_path):
    data = {
        'component_id': 'TEST_COMP',
        'lot_id': 'TEST_LOT',
        'disposition': 'FULL_BURN_IN',
        'risk_tier': 'MEDIUM',
        'reasons': ['Slope exceeded threshold'],
        'pred_168h': 34.5,
        'margin': 0.05,
        'interval': 2.3,
        'routing_rationale': 'none'
    }
    
    first_pdf = tmp_path / 'test_render_1.pdf'
    second_pdf = tmp_path / 'test_render_2.pdf'
    generate_pdf_certificate(data, str(first_pdf))
    generate_pdf_certificate(data, str(second_pdf))
    
    with Path(first_pdf).open('rb') as f:
        b1 = f.read()
    with Path(second_pdf).open('rb') as f:
        b2 = f.read()
        
    assert b1 == b2, "PDF renders are not byte-identical"
