from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import re

def generate_pdf_certificate(card_data: dict, filepath: str):
    c = canvas.Canvas(filepath, pagesize=letter)
    
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 750, "AGNI PARIKSHA - CERTIFICATE OF CONFORMANCE")
    
    c.setFont("Helvetica", 12)
    y = 710
    c.drawString(50, y, f"Part ID: {card_data.get('component_id')}")
    c.drawString(300, y, f"Lot ID: {card_data.get('lot_id')}")
    y -= 30
    
    c.drawString(50, y, f"Verdict: {card_data.get('disposition')}")
    c.drawString(300, y, f"Risk Tier: {card_data.get('risk_tier')}")
    y -= 40
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Top Contributing Parameters & Reasons:")
    c.setFont("Helvetica", 10)
    y -= 20
    
    for line in card_data.get('reasons', []):
        c.drawString(70, y, f"- {line}")
        y -= 15
        
    y -= 15
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Metrics:")
    c.setFont("Helvetica", 10)
    y -= 20
    c.drawString(70, y, f"Measured 168h: N/A (Projected: {card_data.get('pred_168h', 'N/A')})")
    y -= 15
    c.drawString(70, y, f"Safety-slope margin: {card_data.get('margin', 'N/A')}")
    y -= 15
    c.drawString(70, y, f"Conformal interval: {card_data.get('interval', 'N/A')}")
    
    y -= 40
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Recommended Disposition:")
    c.setFont("Helvetica", 10)
    y -= 20
    c.drawString(70, y, f"{card_data.get('disposition')}")
    
    if 'routing_rationale' in card_data and card_data['routing_rationale']:
        y -= 20
        c.drawString(70, y, f"Routing Rationale: {card_data['routing_rationale']}")
        
    # Footer
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(50, 50, "AGNI PARIKSHA Evaluation Pipeline - Commit c86c4b2f753af149fb561c389515efd5eb8fe8ea")
    
    c._doc.info.producer = "AGNI PARIKSHA"
    c._doc.info.creator = "AGNI PARIKSHA"
    c._doc.info.title = "QA Certificate"
    
    c.save()
    
    with open(filepath, 'rb') as f:
        pdf_data = f.read()
    
    pdf_data = re.sub(b'/ID\\s*\\[<[0-9a-fA-F]+><[0-9a-fA-F]+>\\]', b'/ID [<00000000000000000000000000000000><00000000000000000000000000000000>]', pdf_data)
    pdf_data = re.sub(b'/CreationDate \\(D:[0-9]{14}[^\\)]*\\)', b'/CreationDate (D:20260923000000Z)', pdf_data)
    pdf_data = re.sub(b'/ModDate \\(D:[0-9]{14}[^\\)]*\\)', b'/ModDate (D:20260923000000Z)', pdf_data)
    
    with open(filepath, 'wb') as f:
        f.write(pdf_data)

