import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def generate_financial_pdf_report(user, report_type, incomes, expenses, budgets, investments, goals, health_score_data, output_path):
    """
    Generates a professional downloadable PDF financial statement using ReportLab.
    """
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom Color Palette
    NAVY = colors.HexColor('#0F172A')
    SLATE = colors.HexColor('#1E293B')
    EMERALD = colors.HexColor('#10B981')
    BLUE = colors.HexColor('#3B82F6')
    RED = colors.HexColor('#EF4444')
    LIGHT_BG = colors.HexColor('#F8FAFC')
    BORDER_COLOR = colors.HexColor('#E2E8F0')

    # Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=22,
        leading=26,
        textColor=NAVY,
        fontName='Helvetica-Bold'
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#64748B'),
        fontName='Helvetica'
    )

    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=14,
        leading=18,
        textColor=SLATE,
        fontName='Helvetica-Bold',
        spaceBefore=12,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=SLATE,
        fontName='Helvetica'
    )

    bold_body = ParagraphStyle(
        'BodyBold',
        parent=body_style,
        fontName='Helvetica-Bold'
    )

    story = []

    # 1. Header Banner
    header_data = [
        [
            Paragraph("<b>PFM FINTECH FINANCIAL STATEMENT</b>", title_style),
            Paragraph(f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}<br/><b>Type:</b> {report_type}", subtitle_style)
        ]
    ]
    header_table = Table(header_data, colWidths=[3.5 * inch, 3.5 * inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (1,0), (1,0), 'RIGHT'),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=2, color=EMERALD, spaceAfter=15))

    # 2. User & Financial Profile Summary Card
    user_info = [
        [Paragraph(f"<b>User Name:</b> {user.full_name}", body_style), Paragraph(f"<b>Email:</b> {user.email}", body_style)],
        [Paragraph(f"<b>Currency:</b> {user.currency}", body_style), Paragraph(f"<b>Risk Profile:</b> {user.risk_tolerance}", body_style)],
        [Paragraph(f"<b>Financial Health Score:</b> <font color='{EMERALD}'><b>{health_score_data['score']}/100 ({health_score_data['grade']})</b></font>", body_style),
         Paragraph(f"<b>Target Monthly Savings:</b> ₹{user.monthly_target_savings:,.2f}", body_style)]
    ]
    user_table = Table(user_info, colWidths=[3.5 * inch, 3.5 * inch])
    user_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), LIGHT_BG),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('PADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(user_table)
    story.append(Spacer(1, 15))

    # 3. High Level Financial Key Metrics Table
    total_inc = sum(i.amount for i in incomes)
    total_exp = sum(e.amount for e in expenses)
    net_sav = total_inc - total_exp
    sav_rate = (net_sav / total_inc * 100) if total_inc > 0 else 0.0
    total_inv = sum(inv.current_value for inv in investments)

    metrics_data = [
        [
            Paragraph("<b>Total Income</b>", bold_body),
            Paragraph("<b>Total Expenses</b>", bold_body),
            Paragraph("<b>Net Savings</b>", bold_body),
            Paragraph("<b>Savings Rate</b>", bold_body),
            Paragraph("<b>Investments</b>", bold_body)
        ],
        [
            Paragraph(f"<font color='green'>₹{total_inc:,.2f}</font>", body_style),
            Paragraph(f"<font color='red'>₹{total_exp:,.2f}</font>", body_style),
            Paragraph(f"<font color='blue'>₹{net_sav:,.2f}</font>", body_style),
            Paragraph(f"{sav_rate:.1f}%", body_style),
            Paragraph(f"₹{total_inv:,.2f}", body_style)
        ]
    ]
    metrics_table = Table(metrics_data, colWidths=[1.4 * inch] * 5)
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#E2E8F0')),
        ('GRID', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(Paragraph("Financial Performance Overview", section_heading))
    story.append(metrics_table)
    story.append(Spacer(1, 15))

    # 4. Expense Breakdown Table
    story.append(Paragraph("Category Spending Analysis", section_heading))
    cat_summary = {}
    for e in expenses:
        cat_summary[e.category] = cat_summary.get(e.category, 0.0) + e.amount

    exp_table_data = [[Paragraph("<b>Category</b>", bold_body), Paragraph("<b>Spent (INR)</b>", bold_body), Paragraph("<b>% of Total</b>", bold_body)]]
    for cat, amt in sorted(cat_summary.items(), key=lambda x: x[1], reverse=True)[:8]:
        pct = (amt / total_exp * 100) if total_exp > 0 else 0
        exp_table_data.append([
            Paragraph(cat, body_style),
            Paragraph(f"₹{amt:,.2f}", body_style),
            Paragraph(f"{pct:.1f}%", body_style)
        ])

    exp_table = Table(exp_table_data, colWidths=[3.0 * inch, 2.0 * inch, 2.0 * inch])
    exp_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), LIGHT_BG),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(exp_table)
    story.append(Spacer(1, 15))

    # 5. Investment & Goal Summary
    story.append(Paragraph("Investments & Financial Goals", section_heading))
    inv_goal_data = [
        [Paragraph("<b>Active Investments</b>", bold_body), Paragraph("<b>Financial Goals</b>", bold_body)],
        [
            Paragraph(f"Total Invested: ₹{sum(i.amount_invested for i in investments):,.2f}<br/>Current Value: ₹{total_inv:,.2f}", body_style),
            Paragraph(f"Total Active Goals: {len(goals)}<br/>Avg Completion: {sum(g.completion_percentage for g in goals)/max(1, len(goals)):.1f}%", body_style)
        ]
    ]
    inv_goal_table = Table(inv_goal_data, colWidths=[3.5 * inch, 3.5 * inch])
    inv_goal_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(inv_goal_table)
    story.append(Spacer(1, 15))

    # 6. AI Insights & Recommendations
    story.append(Paragraph("AI Intelligent Financial Advice", section_heading))
    ai_msg = f"• {health_score_data['summary']}<br/>"
    if sav_rate < 20:
        ai_msg += "• Recommended: Cut top discretionary categories (Shopping/Travel) by 15% to reach a 20% savings rate.<br/>"
    if total_inv < total_inc * 0.1:
        ai_msg += "• Recommended: Build a systematic monthly SIP of ₹5,000 in Mutual Funds/PPF for wealth compounding."

    ai_p = Paragraph(ai_msg, body_style)
    ai_box = Table([[ai_p]], colWidths=[7.0 * inch])
    ai_box.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F0FDF4')),
        ('BOX', (0,0), (-1,-1), 1, EMERALD),
        ('PADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(ai_box)

    # Build Document
    doc.build(story)
    return output_path
