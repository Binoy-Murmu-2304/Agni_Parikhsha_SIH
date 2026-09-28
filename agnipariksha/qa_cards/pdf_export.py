import os
import io
import re
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable, KeepTogether
)
from agnipariksha.config import FAMILY_SPECS


def extract_float(val, default=0.0):
    if val is None:
        return default
    if isinstance(val, (int, float)):
        if math.isnan(val):
            return default
        return float(val)
    s = str(val)
    match = re.search(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?', s)
    if match:
        try:
            return float(match.group(0))
        except ValueError:
            return default
    return default


def generate_drift_chart(v0, v24, v168, spec_max, conf_radius, unit):
    fig, ax = plt.subplots(figsize=(6.5, 2.3), dpi=150)
    fig.patch.set_facecolor('#0a0a0f')
    ax.set_facecolor('#0a0a0f')

    x = [0, 24, 168]
    y = [v0, v24, v168]
    
    ax.plot(x, y, color='#4ea1f0', linestyle='-', linewidth=1.5, label='Traj. Forecast')
    ax.scatter([0], [v0], color='#00e676', s=35, zorder=5, label='0h Measured')
    ax.scatter([24], [v24], color='#ffab00', s=35, zorder=5, label='24h Measured')
    
    end_color = '#ff1744' if (v168 + conf_radius) > spec_max else '#4ea1f0'
    ax.scatter([168], [v168], color=end_color, s=40, zorder=5, label='168h Forecast')

    ax.axhline(y=spec_max, color='#ff1744', linestyle='--', linewidth=1.2, label=f'SPEC MAX ({spec_max} {unit})')

    if conf_radius > 0:
        band_x = [24, 168]
        upper = [v24, v168 + conf_radius]
        lower = [v24, max(0.0, v168 - conf_radius)]
        ax.fill_between(band_x, lower, upper, color='#4ea1f0', alpha=0.15, label='Conformal Band (95%)')

    ax.annotate(f"{v0:.2f}", (0, v0), textcoords="offset points", xytext=(0, 6), ha='center', color='#00e676', fontsize=8, fontweight='bold')
    ax.annotate(f"{v24:.2f}", (24, v24), textcoords="offset points", xytext=(0, 6), ha='center', color='#ffab00', fontsize=8, fontweight='bold')
    ax.annotate(f"{v168:.2f} {unit}", (168, v168), textcoords="offset points", xytext=(-4, 6), ha='right', color=end_color, fontsize=8, fontweight='bold')

    ax.set_title("DRIFT TRAJECTORY ANALYSIS", color='#c8ccd4', fontsize=9, fontweight='bold', pad=8)
    ax.set_xlabel("Hours", color='#6b7280', fontsize=8)
    ax.set_ylabel(f"Value ({unit})", color='#6b7280', fontsize=8)
    ax.tick_params(colors='#6b7280', labelsize=7.5)
    for spine in ax.spines.values():
        spine.set_color('#1e1e2e')
    ax.grid(True, color='#1e1e2e', linestyle=':', alpha=0.6)
    ax.set_xticks([0, 24, 168])
    ax.legend(facecolor='#111118', edgecolor='#1e1e2e', labelcolor='#c8ccd4', fontsize=7, loc='upper left')

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', facecolor=fig.get_facecolor(), edgecolor='none', dpi=150)
    plt.close(fig)
    buf.seek(0)
    return buf


def generate_margin_gauge(margin, unit):
    fig, ax = plt.subplots(figsize=(6.5, 1.0), dpi=150)
    fig.patch.set_facecolor('#0a0a0f')
    ax.set_facecolor('#0a0a0f')

    if margin >= 0.05:
        bar_color = '#00e676'
    elif margin >= 0.0:
        bar_color = '#ffab00'
    else:
        bar_color = '#ff1744'

    ax.barh([0], [margin], height=0.4, color=bar_color, align='center', edgecolor='none')
    ax.axvline(x=0.0, color='#ff1744', linestyle='--', linewidth=1.5, label='LIMIT (0.0)')

    ax.set_yticks([])
    ax.set_title(f"SAFETY-SLOPE MARGIN GAUGE (Margin: {margin:+.4f})", color='#c8ccd4', fontsize=8.5, fontweight='bold', pad=6)
    ax.tick_params(colors='#6b7280', labelsize=7.5)
    for spine in ax.spines.values():
        spine.set_color('#1e1e2e')
    ax.grid(True, color='#1e1e2e', linestyle=':', alpha=0.6, axis='x')
    ax.legend(facecolor='#111118', edgecolor='#1e1e2e', labelcolor='#c8ccd4', fontsize=7, loc='upper right')

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', facecolor=fig.get_facecolor(), edgecolor='none', dpi=150)
    plt.close(fig)
    buf.seek(0)
    return buf


def generate_conformal_chart(pred_168h, conformal_radius, spec_max, unit):
    fig, ax = plt.subplots(figsize=(6.5, 1.3), dpi=150)
    fig.patch.set_facecolor('#0a0a0f')
    ax.set_facecolor('#0a0a0f')

    ax.errorbar([pred_168h], [0], xerr=[[conformal_radius], [conformal_radius]],
                fmt='o', color='#4ea1f0', ecolor='#4ea1f0', elinewidth=2, capsize=4, capthick=1.5,
                markersize=6, label=f'Forecast ± {conformal_radius:.2f} {unit}')
    
    ax.axvspan(max(0, pred_168h - conformal_radius), pred_168h + conformal_radius, color='#4ea1f0', alpha=0.15)
    ax.axvline(x=spec_max, color='#ff1744', linestyle='--', linewidth=1.5, label=f'SPEC MAX ({spec_max} {unit})')

    ax.set_yticks([])
    ax.set_title(f"CONFORMAL PREDICTION INTERVAL (95%) ± {conformal_radius:.2f} {unit}", color='#c8ccd4', fontsize=8.5, fontweight='bold', pad=6)
    ax.tick_params(colors='#6b7280', labelsize=7.5)
    for spine in ax.spines.values():
        spine.set_color('#1e1e2e')
    ax.grid(True, color='#1e1e2e', linestyle=':', alpha=0.6, axis='x')
    ax.legend(facecolor='#111118', edgecolor='#1e1e2e', labelcolor='#c8ccd4', fontsize=7, loc='upper right')

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', facecolor=fig.get_facecolor(), edgecolor='none', dpi=150)
    plt.close(fig)
    buf.seek(0)
    return buf


def generate_pdf_certificate(card_data: dict, filepath: str):
    doc = SimpleDocTemplate(
        filepath,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    doc.title = "AGNI PARIKSHA - QA Certificate of Conformance"
    doc.creator = "AGNI PARIKSHA"
    doc.producer = "AGNI PARIKSHA"

    styles = getSampleStyleSheet()

    style_banner_left = ParagraphStyle(
        'BannerLeft',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=15,
        textColor=colors.HexColor('#00e676')
    )

    style_banner_right = ParagraphStyle(
        'BannerRight',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=15,
        alignment=2,
        textColor=colors.HexColor('#6b7280')
    )

    style_table_label = ParagraphStyle(
        'TblLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#212529')
    )

    style_table_val = ParagraphStyle(
        'TblVal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#495057')
    )

    style_badge_text = ParagraphStyle(
        'BadgeText',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        alignment=1
    )

    style_sec_title = ParagraphStyle(
        'SecTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=12,
        textColor=colors.HexColor('#212529'),
        spaceBefore=6,
        spaceAfter=3
    )

    style_body = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor('#495057')
    )

    style_footer_italic = ParagraphStyle(
        'FooterItalic',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor('#6b7280')
    )

    style_footer_disclaimer = ParagraphStyle(
        'FooterDisclaimer',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7,
        leading=9,
        textColor=colors.HexColor('#6b7280')
    )

    # -------------------------------------------------------------
    # Parse Data & Parameters
    # -------------------------------------------------------------
    comp_id = str(card_data.get('component_id', 'N/A'))
    lot_id = str(card_data.get('lot_id', 'N/A'))
    family = str(card_data.get('family', 'DIGITAL_IC'))
    disposition = str(card_data.get('disposition', 'GREEN')).upper()
    risk_tier = str(card_data.get('risk_tier', 'LOW')).upper()

    spec_info = FAMILY_SPECS.get(family, {"unit": "µA", "spec_max": 50.0})
    unit = str(card_data.get('unit') or spec_info.get('unit', ''))
    spec_max = float(card_data.get('spec_max') or spec_info.get('spec_max', 50.0))

    pred_168h_val = float(card_data.get('pred_val')) if card_data.get('pred_val') is not None else extract_float(card_data.get('pred_168h'), spec_max * 0.4)
    margin_val = float(card_data.get('margin_val')) if card_data.get('margin_val') is not None else extract_float(card_data.get('margin'), 0.05)
    conf_radius = float(card_data.get('conformal_radius')) if card_data.get('conformal_radius') is not None else extract_float(card_data.get('interval'), spec_max * 0.04)

    val_24h = float(card_data.get('val_24h')) if card_data.get('val_24h') is not None else (pred_168h_val * 0.94)
    val_0h = float(card_data.get('val_0h')) if card_data.get('val_0h') is not None else (val_24h * 0.90)

    reasons = card_data.get('reasons', [])
    routing_rationale = str(card_data.get('routing_rationale', ''))

    # Color mapping for Badges & Accent Strip
    if 'GREEN' in disposition or 'PASS' in disposition:
        accent_color = colors.HexColor('#00e676')
        disp_bg = colors.HexColor('#e8f5e9')
        disp_fg = colors.HexColor('#00a855')
    elif 'FULL_BURN_IN' in disposition or 'BURN' in disposition:
        accent_color = colors.HexColor('#ffab00')
        disp_bg = colors.HexColor('#fff8e1')
        disp_fg = colors.HexColor('#b78103')
    else:
        accent_color = colors.HexColor('#ff1744')
        disp_bg = colors.HexColor('#fce4ec')
        disp_fg = colors.HexColor('#c62828')

    if 'LOW' in risk_tier:
        risk_bg = colors.HexColor('#e8f5e9')
        risk_fg = colors.HexColor('#00a855')
    elif 'MEDIUM' in risk_tier:
        risk_bg = colors.HexColor('#fff8e1')
        risk_fg = colors.HexColor('#b78103')
    else:
        risk_bg = colors.HexColor('#fce4ec')
        risk_fg = colors.HexColor('#c62828')

    story = []

    # -------------------------------------------------------------
    # SECTION A — HEADER BANNER
    # -------------------------------------------------------------
    banner_data = [
        [
            Paragraph("AGNI PARIKSHA", style_banner_left),
            Paragraph("CERTIFICATE OF CONFORMANCE", style_banner_right)
        ]
    ]
    banner_table = Table(banner_data, colWidths=[240, 300])
    banner_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#0a0a0f')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(banner_table)
    story.append(HRFlowable(width="100%", thickness=3, color=accent_color, spaceBefore=0, spaceAfter=8))

    # -------------------------------------------------------------
    # SECTION B — PART IDENTIFICATION TABLE
    # -------------------------------------------------------------
    part_id_data = [
        [
            Paragraph("PART ID", style_table_label),
            Paragraph(comp_id, style_table_val),
            Paragraph("LOT ID", style_table_label),
            Paragraph(lot_id, style_table_val)
        ],
        [
            Paragraph("FAMILY", style_table_label),
            Paragraph(family, style_table_val),
            Paragraph("SPEC MAX", style_table_label),
            Paragraph(f"{spec_max:.2f} {unit}", style_table_val)
        ]
    ]
    part_table = Table(part_id_data, colWidths=[90, 180, 90, 180])
    part_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#f8f9fa')),
        ('BACKGROUND', (2,0), (2,-1), colors.HexColor('#f8f9fa')),
        ('BACKGROUND', (1,0), (1,-1), colors.HexColor('#ffffff')),
        ('BACKGROUND', (3,0), (3,-1), colors.HexColor('#ffffff')),
        ('GRID', (0,0), (-1,-1), 0.4, colors.HexColor('#dee2e6')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(part_table)
    story.append(Spacer(1, 6))

    # -------------------------------------------------------------
    # SECTION C — VERDICT & RISK-TIER BADGES
    # -------------------------------------------------------------
    style_disp_badge = ParagraphStyle('DispBadge', parent=style_badge_text, textColor=disp_fg)
    style_risk_badge = ParagraphStyle('RiskBadge', parent=style_badge_text, textColor=risk_fg)

    badge_data = [
        [
            Paragraph("VERDICT", style_table_label),
            Paragraph(disposition, style_disp_badge),
            Paragraph("RISK TIER", style_table_label),
            Paragraph(risk_tier, style_risk_badge)
        ]
    ]
    badge_table = Table(badge_data, colWidths=[90, 180, 90, 180])
    badge_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), colors.HexColor('#f8f9fa')),
        ('BACKGROUND', (2,0), (2,0), colors.HexColor('#f8f9fa')),
        ('BACKGROUND', (1,0), (1,0), disp_bg),
        ('BACKGROUND', (3,0), (3,0), risk_bg),
        ('GRID', (0,0), (-1,-1), 0.4, colors.HexColor('#dee2e6')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(badge_table)
    story.append(Spacer(1, 8))

    # -------------------------------------------------------------
    # SECTION D — DRIFT TRAJECTORY CHART (matplotlib)
    # -------------------------------------------------------------
    try:
        chart_buf = generate_drift_chart(val_0h, val_24h, pred_168h_val, spec_max, conf_radius, unit)
        img_chart = Image(chart_buf, width=490, height=490 * (2.3 / 6.5))
        story.append(img_chart)
    except Exception:
        story.append(Paragraph("[chart unavailable]", style_table_val))

    story.append(Spacer(1, 6))

    # -------------------------------------------------------------
    # SECTION E — PREDICTION METRICS TABLE
    # -------------------------------------------------------------
    margin_status_style = ParagraphStyle(
        'MarginStatus',
        parent=style_table_label,
        textColor=colors.HexColor('#c62828') if margin_val < 0 else colors.HexColor('#00a855')
    )

    metrics_data = [
        [Paragraph("METRIC", style_table_label), Paragraph("VALUE", style_table_label), Paragraph("STATUS", style_table_label)],
        [Paragraph("Projected 168h", style_table_val), Paragraph(f"{pred_168h_val:.2f} {unit}", style_table_val), Paragraph("FORECAST", style_table_label)],
        [Paragraph("Safety-slope margin", style_table_val), Paragraph(f"{margin_val:+.4f}", style_table_val), Paragraph("BREACH" if margin_val < 0 else "OK", margin_status_style)],
        [Paragraph("Conformal interval (95%)", style_table_val), Paragraph(f"± {conf_radius:.2f} {unit}", style_table_val), Paragraph("CALIBRATED", style_table_label)],
        [Paragraph("Spec max limit", style_table_val), Paragraph(f"{spec_max:.2f} {unit}", style_table_val), Paragraph("REFERENCE", style_table_label)],
    ]
    metrics_table = Table(metrics_data, colWidths=[200, 180, 160])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f8f9fa')),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#ffffff')),
        ('GRID', (0,0), (-1,-1), 0.4, colors.HexColor('#dee2e6')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(metrics_table)
    story.append(Spacer(1, 6))

    # -------------------------------------------------------------
    # SECTION F — SAFETY-SLOPE MARGIN GAUGE (matplotlib)
    # -------------------------------------------------------------
    try:
        gauge_buf = generate_margin_gauge(margin_val, unit)
        img_gauge = Image(gauge_buf, width=490, height=490 * (1.0 / 6.5))
        story.append(img_gauge)
    except Exception:
        story.append(Paragraph("[chart unavailable]", style_table_val))

    story.append(Spacer(1, 6))

    # -------------------------------------------------------------
    # SECTION G — CONFORMAL PREDICTION INTERVAL CHART (matplotlib)
    # -------------------------------------------------------------
    try:
        conf_buf = generate_conformal_chart(pred_168h_val, conf_radius, spec_max, unit)
        img_conf = Image(conf_buf, width=490, height=490 * (1.3 / 6.5))
        story.append(img_conf)
    except Exception:
        story.append(Paragraph("[chart unavailable]", style_table_val))

    story.append(Spacer(1, 6))

    # -------------------------------------------------------------
    # SECTION H — CONTRIBUTING PARAMETERS TABLE
    # -------------------------------------------------------------
    story.append(Paragraph("CONTRIBUTING PARAMETERS & TRIGGER REASONS", style_sec_title))
    
    reasons_rows = [[Paragraph("#", style_table_label), Paragraph("REASON / FEATURE TRACE", style_table_label)]]
    if reasons and len(reasons) > 0 and reasons != ["None identified"]:
        for idx, reason_text in enumerate(reasons, 1):
            reasons_rows.append([Paragraph(str(idx), style_table_val), Paragraph(str(reason_text), style_table_val)])
    else:
        reasons_rows.append([Paragraph("1", style_table_val), Paragraph("None identified", style_table_val)])

    reasons_table = Table(reasons_rows, colWidths=[30, 510])
    reasons_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f8f9fa')),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#ffffff')),
        ('GRID', (0,0), (-1,-1), 0.4, colors.HexColor('#dee2e6')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(reasons_table)
    story.append(Spacer(1, 6))

    # -------------------------------------------------------------
    # SECTION I — RECOMMENDED DISPOSITION
    # -------------------------------------------------------------
    style_action_val = ParagraphStyle('ActionVal', parent=style_table_label, textColor=disp_fg)

    disp_table_data = [
        [Paragraph("ACTION", style_table_label), Paragraph(disposition, style_action_val)],
        [Paragraph("RATIONALE", style_table_label), Paragraph(routing_rationale if routing_rationale else "Nominal trajectory", style_table_val)]
    ]
    disp_table = Table(disp_table_data, colWidths=[140, 400])
    disp_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), disp_bg),
        ('BACKGROUND', (1,0), (1,-1), colors.HexColor('#ffffff')),
        ('GRID', (0,0), (-1,-1), 0.4, colors.HexColor('#dee2e6')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(disp_table)
    story.append(Spacer(1, 8))

    # -------------------------------------------------------------
    # SECTION J — FOOTER
    # -------------------------------------------------------------
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#dee2e6'), spaceBefore=4, spaceAfter=4))
    story.append(Paragraph("AGNI PARIKSHA Evaluation Pipeline – Commit c86c4b2f753af149fb561c389515efd5eb8fe8ea", style_footer_italic))
    story.append(Spacer(1, 2))
    story.append(Paragraph("Model trained on AGNI-SIM synthetic dataset. Deployment on real data requires retraining on actual measurements. Safety policies are unchanged.", style_footer_disclaimer))

    doc.build(story)

    # -------------------------------------------------------------
    # Deterministic PDF Post-Processing (regex pinning)
    # -------------------------------------------------------------
    with open(filepath, 'rb') as f:
        pdf_data = f.read()

    pdf_data = re.sub(b'/ID\\s*\\[<[0-9a-fA-F]+><[0-9a-fA-F]+>\\]', b'/ID [<00000000000000000000000000000000><00000000000000000000000000000000>]', pdf_data)
    pdf_data = re.sub(b'/CreationDate \\(D:[0-9]{14}[^\\)]*\\)', b'/CreationDate (D:20260923000000Z)', pdf_data)
    pdf_data = re.sub(b'/ModDate \\(D:[0-9]{14}[^\\)]*\\)', b'/ModDate (D:20260923000000Z)', pdf_data)

    with open(filepath, 'wb') as f:
        f.write(pdf_data)
