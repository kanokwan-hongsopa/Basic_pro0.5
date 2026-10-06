"""
Styling constants, dark slate safety theme palette, and Plotly templates
for Thailand Road Accident Analytics Dashboard.
"""

# Color Palette (Dark Slate Theme with Safety Indicators)
COLOR_BG_DARK = "#0F172A"       # Main application background
COLOR_CARD_BG = "#1E293B"       # Card / Container background
COLOR_CARD_BORDER = "#334155"   # Card subtle border
COLOR_TEXT_PRIMARY = "#F8FAFC"  # High-contrast text
COLOR_TEXT_MUTED = "#94A3B8"    # Subtitles, labels, legends
COLOR_TEXT_SECONDARY = "#CBD5E1"# Secondary body text

# Safety Status Indicators (from BRD)
COLOR_CRITICAL_RED = "#FF4136"  # High Risk / Level 3 / Critical Blackspot
COLOR_WARNING_AMBER = "#FFDC00" # Moderate Risk / Level 2 / Warning
COLOR_SAFE_GREEN = "#2ECC40"    # Low Risk / Level 1 / Baseline

# Accent & Data Palette
COLOR_CYAN_ACCENT = "#38BDF8"   # Secondary metric
COLOR_PURPLE_ACCENT = "#A855F7" # Secondary category
COLOR_ORANGE_ACCENT = "#FB923C" # Auxiliary metric

RISK_COLOR_MAP = {
    "Level 3: Critical Blackspot (Red Zone)": COLOR_CRITICAL_RED,
    "Level 2: Moderate Risk (Surveillance Zone)": COLOR_WARNING_AMBER,
    "Level 1: Low Risk (Baseline Zone)": COLOR_SAFE_GREEN,
}

VEHICLE_COLOR_MAP = {
    "Motorcycle": "#F43F5E",
    "Private Car": "#38BDF8",
    "Commercial Truck": "#F59E0B",
    "Public Bus/Van": "#10B981",
}

# Standard Plotly Layout Config
def apply_dark_theme(fig, title="", height=400):
    fig.update_layout(
        title={
            "text": f"<b>{title}</b>" if title else "",
            "x": 0.03,
            "y": 0.94,
            "xanchor": "left",
            "yanchor": "top",
            "font": {"size": 15, "color": COLOR_TEXT_PRIMARY, "family": "Inter, Prompt, Segoe UI, sans-serif"}
        },
        height=height,
        paper_bgcolor=COLOR_CARD_BG,
        plot_bgcolor="rgba(15, 23, 42, 0.4)",
        font={"color": COLOR_TEXT_MUTED, "family": "Inter, Prompt, Segoe UI, sans-serif", "size": 12},
        margin=dict(l=40, r=30, t=50, b=40),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font={"size": 11, "color": COLOR_TEXT_SECONDARY},
            bgcolor="rgba(0,0,0,0)"
        ),
        xaxis=dict(
            gridcolor="#334155",
            zerolinecolor="#475569",
            tickfont={"color": COLOR_TEXT_MUTED, "size": 11},
            title_font={"color": COLOR_TEXT_SECONDARY, "size": 12}
        ),
        yaxis=dict(
            gridcolor="#334155",
            zerolinecolor="#475569",
            tickfont={"color": COLOR_TEXT_MUTED, "size": 11},
            title_font={"color": COLOR_TEXT_SECONDARY, "size": 12}
        ),
        hoverlabel=dict(
            bgcolor="#0F172A",
            font_size=12,
            font_family="Inter, Prompt, Segoe UI, sans-serif",
            font_color="#FFFFFF"
        )
    )
    return fig
