import os
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import matplotlib.pyplot as plt
import io

def generate_trajectory_chart(part_df, lot_df, param_name, img_buffer):
    """
    Generates a matplotlib chart of the part trajectory vs lot distribution
    and saves it to the provided BytesIO buffer.
    """
    plt.figure(figsize=(6, 4))
    
    # Plot lot distribution (all parts except this one)
    for pid, group in lot_df.groupby('part_id'):
        if pid != part_df['part_id'].iloc[0]:
            group = group.sort_values('timepoint_hours')
            plt.plot(group['timepoint_hours'], group['value'], color='lightgray', alpha=0.5, linewidth=1)
            
    # Plot this part
    part_df = part_df.sort_values('timepoint_hours')
    plt.plot(part_df['timepoint_hours'], part_df['value'], color='red', linewidth=2.5, marker='o', label='This Part')
    
    plt.title(f"Trajectory for {param_name}")
    plt.xlabel("Timepoint (Hours)")
    plt.ylabel("Value")
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(img_buffer, format='png', dpi=150)
    plt.close()
    
def create_pdf_certificate(
    part_id: str,
    lot_id: str,
    verdict: str,
    cri_score: float,
    part_df: pd.DataFrame,
    lot_df: pd.DataFrame,
    attribution_scores: dict,
    output_path: str
):
    """
    Generates a PDF certificate for a REVIEW or REJECT part.
    """
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    
    # Header
    elements.append(Paragraph("<b>AGNI-PARIKSHA</b> - Latent Defect Certificate", styles['Title']))
    elements.append(Spacer(1, 12))
    
    # Part Identity & Verdict
    elements.append(Paragraph(f"<b>Part ID:</b> {part_id}", styles['Normal']))
    elements.append(Paragraph(f"<b>Lot ID:</b> {lot_id}", styles['Normal']))
    elements.append(Paragraph(f"<b>Verdict:</b> <font color='{'red' if verdict == 'REJECT' else 'orange'}'>{verdict}</font>", styles['Normal']))
    elements.append(Paragraph(f"<b>CRI Score:</b> {cri_score:.1f}/100", styles['Normal']))
    elements.append(Spacer(1, 12))
    
    # Attribution
    if attribution_scores:
        elements.append(Paragraph("<b>Top Contributing Parameters:</b>", styles['Heading3']))
        sorted_attrs = sorted(attribution_scores.items(), key=lambda x: x[1], reverse=True)
        for param, score in sorted_attrs[:3]:
            elements.append(Paragraph(f"- {param}: {score:.2f} (influence score)", styles['Normal']))
        elements.append(Spacer(1, 12))
        
    # Counterfactual
    param_highest = sorted_attrs[0][0] if attribution_scores else "Iddq"
    elements.append(Paragraph("<b>Counterfactual:</b>", styles['Heading3']))
    elements.append(Paragraph(f"This part would likely PASS if <i>{param_highest}</i> had remained closer to the lot median at the final checkpoint.", styles['Normal']))
    elements.append(Spacer(1, 12))
    
    # Chart
    if not part_df.empty and not lot_df.empty:
        img_buffer = io.BytesIO()
        generate_trajectory_chart(part_df, lot_df, param_highest, img_buffer)
        img_buffer.seek(0)
        img = Image(img_buffer, width=400, height=260)
        elements.append(img)
        elements.append(Spacer(1, 12))
        
    # Table of Readings
    elements.append(Paragraph("<b>Readings Table:</b>", styles['Heading3']))
    table_data = [["Timepoint", "Value"]]
    part_sorted = part_df.sort_values('timepoint_hours')
    for _, row in part_sorted.iterrows():
        table_data.append([f"{row['timepoint_hours']}h", f"{row['value']:.4f}"])
        
    t = Table(table_data, colWidths=[100, 100])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ]))
    elements.append(t)
    elements.append(Spacer(1, 30))
    
    # Signature
    elements.append(Paragraph("Inspector Signature: ___________________________", styles['Normal']))
    elements.append(Paragraph("Date: ___________________________", styles['Normal']))
    
    doc.build(elements)
    
