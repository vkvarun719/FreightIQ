"""
build_pdf.py - Generates an institutional-grade PDF documentation document for
the Baltic Dry Index (BDI) Freight Intelligence & Chartering Optimization Desk (FreightIQ).
"""

import os
import sys
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

PDF_OUTPUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "FreightIQ_Platform_Architecture_and_Guide.pdf")

# Custom Canvas for Professional Header & Footer with Page Numbers
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))

        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 750, "FREIGHTIQ: BALTIC DRY INDEX FREIGHT INTELLIGENCE & CHARTERING OPTIMIZATION")
            self.drawRightString(612 - 54, 750, "TECHNICAL & OPERATIONAL MANUAL")
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.5)
            self.line(54, 742, 612 - 54, 742)

        # Footer (all pages)
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(54, 45, 612 - 54, 45)
        self.drawString(54, 32, "CONFIDENTIAL & PROPRIETARY — INSTITUTIONAL MARITIME DESK USE ONLY")
        self.drawRightString(612 - 54, 32, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()

def generate_pdf():
    doc = SimpleDocTemplate(
        PDF_OUTPUT_PATH,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    # Custom Palette
    c_primary = colors.HexColor("#0f172a")     # Deep Navy
    c_secondary = colors.HexColor("#1e3a8a")   # Marine Blue
    c_accent = colors.HexColor("#0284c7")      # Ocean Cyan
    c_dark = colors.HexColor("#1e293b")        # Slate Text
    c_light = colors.HexColor("#f8fafc")       # Card Background
    c_border = colors.HexColor("#e2e8f0")      # Border Grey
    c_emerald = colors.HexColor("#059669")     # Success Green
    c_amber = colors.HexColor("#d97706")       # Warning Amber

    # Paragraph Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=c_primary,
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=c_secondary,
        spaceAfter=15
    )

    h1_style = ParagraphStyle(
        'Heading1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=c_primary,
        spaceBefore=12,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=c_secondary,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=c_dark,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'BulletText',
        parent=body_style,
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=4
    )

    code_style = ParagraphStyle(
        'CodeBlock',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#0f172a"),
        backColor=colors.HexColor("#f1f5f9"),
        borderPadding=6,
        spaceBefore=4,
        spaceAfter=6
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=c_dark
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=11,
        textColor=colors.white
    )

    story = []

    # -------------------------------------------------------------
    # 1. TITLE & EXECUTIVE BANNER
    # -------------------------------------------------------------
    story.append(Paragraph("FREIGHTIQ: BALTIC DRY INDEX INTELLIGENCE NETWORK", title_style))
    story.append(Paragraph("Institutional Maritime Analytics, Ensemble Forecasting & Live Data Auto-Update Operational Guide", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_accent, spaceBefore=0, spaceAfter=10))

    # Metadata Box
    meta_data = [
        [
            Paragraph("<b>Target Audience:</b> Dry Bulk Charterers, Vessel Operators, Traders", table_cell_style),
            Paragraph(f"<b>System Baseline:</b> September 2026 (3,164 Sessions)", table_cell_style)
        ],
        [
            Paragraph("<b>Coverage:</b> 2014–2026 Historical Baltic Settlements (10+ Yrs)", table_cell_style),
            Paragraph("<b>Architecture:</b> Super Learner Meta-Ensemble + FastAPI Desk", table_cell_style)
        ]
    ]
    meta_table = Table(meta_data, colWidths=[270, 234])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), c_light),
        ('BOX', (0, 0), (-1, -1), 0.5, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))

    # -------------------------------------------------------------
    # 2. SECTION 1: WHAT IS THIS WEBSITE ABOUT?
    # -------------------------------------------------------------
    story.append(Paragraph("1. Executive Overview: What is FreightIQ?", h1_style))
    story.append(Paragraph(
        "<b>FreightIQ</b> is an institutional-grade commercial freight intelligence and decision-support platform designed for dry bulk charterers, vessel operators, commodity trading desks (coking coal, thermal coal, iron ore, bauxite, grain), and maritime supply chain directors. It bridges high-frequency quantitative market forecasting with operational terminal navigation constraints.",
        body_style
    ))
    story.append(Paragraph("The platform addresses four fundamental commercial chartering pillars:", body_style))
    story.append(Paragraph("• <b>Optimal Market Entry & Fixture Timing:</b> Identifies cyclical rate troughs across Capesize, Panamax, Supramax, and Handysize segments. Recommends prompt vs. deferred strategic entry windows with quantified dollar savings per cargo.", bullet_style))
    story.append(Paragraph("• <b>Port Infrastructure & Vessel Matching (India East Coast):</b> Enforces physical draft and LOA constraints across all major East Coast Indian bulk terminals (Dhamra, Gangavaram, Krishnapatnam, Visakhapatnam, Paradip, Ennore, Chennai, Haldia) to eliminate draft exceedance risks.", bullet_style))
    story.append(Paragraph("• <b>Voyage Economics & Cost Optimization:</b> Calculates net freight cost per metric ton ($/MT), sea transit days, port turnaround stay (TPD), VLSFO bunker consumption (@ $615/MT), port dues, and demurrage exposure.", bullet_style))
    story.append(Paragraph("• <b>Idle Fleet & Backhaul Triangulation:</b> Formulates coastal backhaul routes post-discharge to eliminate empty deadhead ballasting (e.g. coastal coal cabotage to Ennore, agricultural export from Kakinada).", bullet_style))
    story.append(Paragraph("• <b>Early Warning & Meteorological Risk Matrix:</b> Tracks market variance spikes, South-West Monsoon swell, North-East post-monsoon cyclone windows (Oct–Dec), and berth queues to enforce protective WIBON/WIPON charter terms.", bullet_style))
    story.append(Spacer(1, 8))

    # -------------------------------------------------------------
    # 3. SECTION 2: HOW TO RUN THE PLATFORM
    # -------------------------------------------------------------
    story.append(Paragraph("2. Operational Runbook: How to Run FreightIQ", h1_style))
    story.append(Paragraph("The system is engineered as a lightweight, high-performance stack with zero heavy dependencies.", body_style))

    story.append(Paragraph("A. Launching the Interactive Web Workstation (Browser UI)", h2_style))
    story.append(Paragraph("Execute the FastAPI workstation server from the project directory:", body_style))
    story.append(Paragraph("cd freightrates<br/>python app.py", code_style))
    story.append(Paragraph("Open your web browser and navigate to <b>http://127.0.0.1:8000</b>. The interactive terminal features real-time dynamic forecasts, interactive horizon toggles (30d, 60d, 90d, 180d), voyage simulators, terminal draft validation, and live CSV export.", body_style))

    story.append(Paragraph("B. Running via Command-Line Interface (CLI)", h2_style))
    story.append(Paragraph("To generate fixture recommendations directly from the terminal:", body_style))
    story.append(Paragraph('python predict.py --commodity "Coking Coal" --volume 75000 --origin "Hay Point / Dalrymple, Australia" --dest "Visakhapatnam" --days 30', code_style))

    story.append(Paragraph("C. Automated Walk-Forward Training & Validation Benchmark", h2_style))
    story.append(Paragraph("To retrain all four models on the full 10-year Baltic dataset and evaluate out-of-sample metrics:", body_style))
    story.append(Paragraph("python train.py", code_style))
    story.append(Paragraph("Detailed validation metrics and 30-day forecast series are written to <code>models/model_report.json</code>.", body_style))

    story.append(Paragraph("D. Automated Daily Background Scheduling", h2_style))
    story.append(Paragraph("• <b>Windows Task Scheduler:</b> Double-click <code>setup_windows_task.bat</code> to register a silent Windows Scheduled Task that executes daily at 18:30 (post-London settlement). Logs are written to <code>logs/scraper.log</code>.<br/>• <b>Python Daemon:</b> Run <code>python bdi_live_scraper.py --schedule 18:30</code> for continuous background execution.", body_style))
    story.append(Spacer(1, 8))

    # -------------------------------------------------------------
    # 4. SECTION 3: QUANTITATIVE FORECASTING MODELS
    # -------------------------------------------------------------
    story.append(Paragraph("3. Quantitative Forecasting Models & 10-Year Benchmark", h1_style))
    story.append(Paragraph(
        "FreightIQ utilizes a <b>Super Learner Stacking Meta-Ensemble</b> trained and validated via walk-forward out-of-sample testing across full market cycles (the 2016 commodity slump, 2020–2022 pandemic disruption, Red Sea canal diversions, and 2024–2026 recovery).",
        body_style
    ))

    # Model Performance Table
    perf_data = [
        [
            Paragraph("<b>Model Architecture</b>", table_header_style),
            Paragraph("<b>Out-of-Sample MAE</b>", table_header_style),
            Paragraph("<b>RMSE</b>", table_header_style),
            Paragraph("<b>MAPE (%)</b>", table_header_style),
            Paragraph("<b>Directional Acc.</b>", table_header_style),
            Paragraph("<b>R² Score</b>", table_header_style)
        ],
        [
            Paragraph("<b>Gradient Boosted Trees (GBDT)</b>", table_cell_style),
            Paragraph("$34.78", table_cell_style),
            Paragraph("$47.56", table_cell_style),
            Paragraph("1.83%", table_cell_style),
            Paragraph("70.85%", table_cell_style),
            Paragraph("<b>0.9930</b>", table_cell_style)
        ],
        [
            Paragraph("<b>Deep Neural Network (MLP-ResNet)</b>", table_cell_style),
            Paragraph("$36.31", table_cell_style),
            Paragraph("$49.53", table_cell_style),
            Paragraph("1.90%", table_cell_style),
            Paragraph("71.18%", table_cell_style),
            Paragraph("0.9925", table_cell_style)
        ],
        [
            Paragraph("<b>Ridge Autoregressive AR(60)</b>", table_cell_style),
            Paragraph("$35.50", table_cell_style),
            Paragraph("$48.87", table_cell_style),
            Paragraph("1.86%", table_cell_style),
            Paragraph("69.89%", table_cell_style),
            Paragraph("0.9927", table_cell_style)
        ],
        [
            Paragraph("<b>Super Learner Meta-Ensemble</b>", table_cell_style),
            Paragraph("<b>$36.82</b>", table_cell_style),
            Paragraph("<b>$50.59</b>", table_cell_style),
            Paragraph("<b>1.91%</b>", table_cell_style),
            Paragraph("<b>69.40%</b>", table_cell_style),
            Paragraph("<b>0.9921</b>", table_cell_style)
        ]
    ]

    perf_table = Table(perf_data, colWidths=[150, 70, 60, 64, 80, 80])
    perf_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_secondary),
        ('BOX', (0, 0), (-1, -1), 0.5, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, c_light]),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#e0e7ff")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
    ]))
    story.append(perf_table)
    story.append(Spacer(1, 8))

    story.append(Paragraph("34-Dimensional Technical & Maritime Feature Matrix:", h2_style))
    story.append(Paragraph("• <b>Trend & Moving Averages:</b> SMA 5, 10, 20, 50, 100, 200, Golden/Death Cross indicator, EMA 12, 26, MACD, Signal, Histogram.<br/>• <b>Momentum & Mean Reversion:</b> RSI-14, Momentum Rate of Change (ROC 5, 20, 60).<br/>• <b>Multi-Scale Volatility:</b> Rolling Std (5, 20, 60d), Parkinson High-Low Volatility, Bollinger Bands (%B and Bandwidth).<br/>• <b>Cyclical Harmonics:</b> Multi-frequency Fourier sine/cosine series (Annual 365.25d, Semi-Annual 182.6d, Quarterly 91.3d).<br/>• <b>Autoregressive Lags:</b> Historical Return Lags 1, 2, 3, 5, 10, 20, 30, and 60 trading sessions.", body_style))
    story.append(Spacer(1, 8))

    # -------------------------------------------------------------
    # 5. SECTION 4: HOW WE TAKE LIVE BDI DATA
    # -------------------------------------------------------------
    story.append(Paragraph("4. Live BDI Data Auto-Update Engine (Web Scraping)", h1_style))
    story.append(Paragraph(
        "To ensure models never go stale, FreightIQ features an institutional scraping and automated model retraining pipeline (<code>bdi_live_scraper.py</code>).",
        body_style
    ))

    story.append(Paragraph("A. Multi-Source Scraping Hierarchy & Failover", h2_style))
    story.append(Paragraph("• <b>Primary (TradingEconomics):</b> Direct JSON script extraction via <code>TEChartsMeta</code> (immune to HTML DOM table column shifting), plus dynamic <code>&lt;th&gt;</code> column header mapping.<br/>• <b>Secondary (Seaandjob News Wire):</b> Scrapes official daily Baltic Exchange market settlement reports (e.g. <i>'The Baltic dry index fell 1.8% to 3445 on Monday'</i>).<br/>• <b>Tertiary (Hellenic Shipping News):</b> Parses daily fixture indices across Capesize, Panamax, and Supramax.<br/>• <b>Quaternary (Investing.com):</b> Browser session emulation with realistic user headers.", body_style))

    story.append(Paragraph("B. Institutional Validation Gate (Circuit-Breakers)", h2_style))
    story.append(Paragraph("Candidate settlements must pass 5 strict validation checks before writing to CSV:", body_style))
    story.append(Paragraph("1. <b>Reasonable Range:</b> Index price must be bounded between $200 and $25,000.<br/>2. <b>Weekend Circuit-Breaker:</b> Rejects Saturday or Sunday prints (Mon–Fri trading sessions only).<br/>3. <b>15% Daily Movement Circuit-Breaker:</b> Rejects prints moving > 15% from prior close to prevent misparsed column anomalies.<br/>4. <b>Chronology Check:</b> Reject backdated or stale prints (candidate date &ge; latest recorded CSV date).<br/>5. <b>Internal Consistency:</b> Verified that <code>Price - Prior Close == Reported Point Change</code> within &plusmn;5 points.", body_style))

    story.append(Paragraph("C. Canonical CSV Sync & Automated Model Retraining", h2_style))
    story.append(Paragraph("• <b>Deterministic Path Resolution:</b> The canonical CSV in <code>freightrates/</code> is updated directly, and root CSV synchronized.<br/>• <b>Ordered Deduplication:</b> Checks if date exists. If new, inserts in descending chronological order.<br/>• <b>Automatic Retraining:</b> Retrains GBDT, MLP-ResNet, Ridge, and Meta-Ensemble, writing updated weights and forecasts to <code>models/model_report.json</code> in ~15 seconds.<br/>• <b>In-App Web 1-Click Sync:</b> Clicking <b>[LIVE AUTO-SYNC]</b> on the web dashboard scrapes fresh data, retrains models, and hot-reloads data in memory with cache-busting so the browser immediately reflects the fresh settlement.", body_style))
    story.append(Spacer(1, 8))

    # -------------------------------------------------------------
    # 6. SECTION 5: HOW IT ALL WORKS (END-TO-END WORKFLOW)
    # -------------------------------------------------------------
    story.append(Paragraph("5. End-to-End System Architecture: How It All Works", h1_style))
    
    arch_data = [
        [
            Paragraph("<b>Stage</b>", table_header_style),
            Paragraph("<b>Component / File</b>", table_header_style),
            Paragraph("<b>Key Operation & Output</b>", table_header_style)
        ],
        [
            Paragraph("<b>1. Live Ingestion</b>", table_cell_style),
            Paragraph("<code>bdi_live_scraper.py</code>", table_cell_style),
            Paragraph("Scrapes live BDI settlement, runs validation gate, appends to CSV with deduplication.", table_cell_style)
        ],
        [
            Paragraph("<b>2. Feature Eng.</b>", table_cell_style),
            Paragraph("<code>baltic_data.py</code>", table_cell_style),
            Paragraph("Constructs 34-dim technical matrix (SMAs, MACD, RSI, volatility, Fourier harmonics, lags).", table_cell_style)
        ],
        [
            Paragraph("<b>3. Model Training</b>", table_cell_style),
            Paragraph("<code>forecasting_models.py</code><br/><code>train.py</code>", table_cell_style),
            Paragraph("Walk-forward cross validation across GBDT, MLP, Ridge. Fits Meta-Ensemble and saves report.", table_cell_style)
        ],
        [
            Paragraph("<b>4. Freight Engine</b>", table_cell_style),
            Paragraph("<code>freight_engine.py</code><br/><code>maritime_data.py</code>", table_cell_style),
            Paragraph("Evaluates voyage economics, terminal draft limits, bunker costs, demurrage, and laycan timing.", table_cell_style)
        ],
        [
            Paragraph("<b>5. User Interface</b>", table_cell_style),
            Paragraph("<code>app.py</code><br/>(FastAPI + Web UI)", table_cell_style),
            Paragraph("Serves interactive workstation at port 8000. Real-time forecasting, simulation, and 1-click sync.", table_cell_style)
        ]
    ]

    arch_table = Table(arch_data, colWidths=[90, 130, 284])
    arch_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_primary),
        ('BOX', (0, 0), (-1, -1), 0.5, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_light]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(arch_table)
    story.append(Spacer(1, 12))

    # Final summary callout
    callout_data = [[
        Paragraph(
            "<b>Summary & Next Steps:</b> FreightIQ is fully configured, validated on 3,164 daily market settlements, and synced to GitHub (<code>himamshu07-dot/FREIGHTIQ</code>). You can launch the server using <code>python app.py</code> or run daily updates via <code>setup_windows_task.bat</code>.",
            table_cell_style
        )
    ]]
    callout_table = Table(callout_data, colWidths=[504])
    callout_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#ecfdf5")),
        ('BOX', (0, 0), (-1, -1), 1, c_emerald),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(callout_table)

    # Build Document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF Successfully generated at: {PDF_OUTPUT_PATH}")

if __name__ == '__main__':
    generate_pdf()
