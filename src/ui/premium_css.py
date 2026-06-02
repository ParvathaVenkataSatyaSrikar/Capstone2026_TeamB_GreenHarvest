"""Premium GreenHarvest stylesheet — imported by components.apply_global_styles."""
from src.ui.brand import css_root_variables


def build_premium_css() -> str:
    return f"""
<style>
    :root {{
{css_root_variables()}
        --gh-font: system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
        --gh-font-display: Georgia, 'Times New Roman', serif;
        --gh-radius-sm: 10px;
        --gh-radius-lg: 22px;
        --gh-radius-xl: 28px;
        --gh-shadow-sm: 0 2px 8px rgba(15, 23, 42, 0.06);
        --gh-shadow-md: 0 8px 30px rgba(15, 23, 42, 0.08);
        --gh-shadow-lg: 0 20px 50px rgba(15, 23, 42, 0.12);
        --gh-shadow-glow: 0 0 0 1px rgba(255,255,255,0.08), 0 12px 40px rgba(34, 197, 94, 0.15);
    }}

    html, body, [class*="css"] {{
        font-family: var(--gh-font) !important;
        color: var(--gh-text);
        font-size: 15px;
        line-height: 1.6;
        -webkit-font-smoothing: antialiased;
    }}

    .block-container {{
        padding-top: 1.25rem !important;
        padding-bottom: 3rem !important;
        max-width: 1180px !important;
    }}

    /* App canvas — soft mesh, not flat green */
    .stApp {{
        background:
            radial-gradient(ellipse 80% 50% at 100% -10%, rgba(34, 197, 94, 0.12), transparent 50%),
            radial-gradient(ellipse 60% 40% at 0% 100%, rgba(14, 165, 233, 0.08), transparent 45%),
            linear-gradient(180deg, #f8fafc 0%, #f1f5f9 40%, #fafaf9 100%) !important;
    }}

    h1, h2, h3, .gh-display {{
        font-family: var(--gh-font-display) !important;
        letter-spacing: -0.02em;
    }}

    #MainMenu, footer {{ visibility: hidden; height: 0; }}
    header[data-testid="stHeader"] {{
        visibility: visible !important;
        background: transparent !important;
    }}
    [data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="collapsedControl"],
    button[kind="header"],
    button[kind="headerNoPadding"] {{
        visibility: visible !important;
        opacity: 1 !important;
        z-index: 999999 !important;
    }}

    /* —— Sidebar: dark premium nav —— */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #0c1812 0%, #13261c 55%, #0f1f17 100%) !important;
        border-right: 1px solid rgba(255,255,255,0.06) !important;
        box-shadow: 8px 0 40px rgba(0,0,0,0.15) !important;
    }}
    section[data-testid="stSidebar"] > div:first-child {{
        background: transparent !important;
    }}
    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] .stCaption {{
        color: rgba(255,255,255,0.88) !important;
    }}
    section[data-testid="stSidebar"] h5 {{
        color: rgba(255,255,255,0.45) !important;
        font-size: 0.7rem !important;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        font-weight: 700 !important;
    }}
    section[data-testid="stSidebar"] hr {{
        border-color: rgba(255,255,255,0.08) !important;
    }}
    section[data-testid="stSidebar"] .stSelectbox label {{
        color: rgba(255,255,255,0.7) !important;
        font-size: 0.8rem !important;
    }}
    section[data-testid="stSidebar"] [data-baseweb="select"] > div {{
        background: rgba(255,255,255,0.08) !important;
        border-color: rgba(255,255,255,0.12) !important;
        color: white !important;
    }}
    section[data-testid="stSidebar"] .stButton > button {{
        border-radius: 12px !important;
        font-weight: 600 !important;
    }}

    /* —— Buttons —— */
    .stButton > button[kind="primary"] {{
        background: linear-gradient(135deg, #15803d 0%, #22c55e 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.55rem 1.25rem !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 14px rgba(34, 197, 94, 0.35) !important;
        transition: transform 0.15s ease, box-shadow 0.15s ease !important;
    }}
    .stButton > button[kind="primary"]:hover {{
        transform: translateY(-1px);
        box-shadow: 0 8px 22px rgba(34, 197, 94, 0.4) !important;
    }}
    .stButton > button[kind="secondary"] {{
        background: white !important;
        color: var(--gh-crop-primary) !important;
        border: 1.5px solid #e2e8f0 !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
    }}
    .stButton > button[kind="secondary"]:hover {{
        border-color: var(--gh-crop-accent) !important;
        background: #f0fdf4 !important;
    }}

    /* —— Hero —— */
    .portal-hero-img {{
        position: relative;
        border-radius: var(--gh-radius-xl);
        overflow: hidden;
        margin-bottom: 1.5rem;
        min-height: 168px;
        box-shadow: var(--gh-shadow-lg);
    }}
    .portal-hero-img .bg {{
        position: absolute; inset: 0;
        background-size: cover;
        background-position: center;
        filter: brightness(0.45) saturate(1.1);
        transform: scale(1.02);
    }}
    .portal-hero-img .overlay {{
        position: relative; z-index: 1;
        background: linear-gradient(115deg,
            rgba(12, 24, 18, 0.92) 0%,
            rgba(15, 118, 110, 0.75) 50%,
            rgba(21, 128, 61, 0.55) 100%);
        padding: 2rem 2.25rem;
        color: white;
    }}
    .portal-hero-img h1 {{
        font-family: var(--gh-font-display) !important;
        color: white !important;
        margin: 0;
        font-size: 2.1rem;
        font-weight: 400;
        line-height: 1.15;
    }}
    .portal-hero-img p {{
        color: rgba(255,255,255,0.82) !important;
        margin: 0.65rem 0 0;
        font-size: 1.02rem;
        max-width: 38rem;
        font-weight: 400;
    }}

    .portal-hero {{
        background: linear-gradient(135deg, #0c1812, #166534, #0f766e);
        padding: 2rem 2.25rem;
        border-radius: var(--gh-radius-xl);
        color: white;
        margin-bottom: 1.5rem;
        box-shadow: var(--gh-shadow-lg);
    }}
    .portal-hero h1 {{
        font-family: var(--gh-font-display) !important;
        color: white !important;
        margin: 0;
        font-size: 2rem;
    }}

    .role-pill {{
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        padding: 0.4rem 1rem;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        background: rgba(255,255,255,0.15);
        border: 1px solid rgba(255,255,255,0.25);
        margin-bottom: 0.75rem;
    }}

    /* —— Sidebar brand —— */
    .gh-sidebar-brand {{
        text-align: left;
        padding: 1.25rem 1.1rem;
        border-radius: var(--gh-radius-lg);
        margin-bottom: 1.25rem;
        background: linear-gradient(145deg, rgba(255,255,255,0.12), rgba(255,255,255,0.04));
        border: 1px solid rgba(255,255,255,0.12);
        box-shadow: var(--gh-shadow-glow);
    }}
    .gh-sidebar-brand .brand-mark {{
        font-size: 1.75rem;
        line-height: 1;
        margin-bottom: 0.35rem;
    }}
    .gh-sidebar-brand .brand-title {{
        font-family: var(--gh-font-display);
        font-size: 1.35rem;
        font-weight: 400;
        color: white;
        letter-spacing: -0.02em;
    }}
    .gh-sidebar-brand .brand-sub {{
        font-size: 0.8rem;
        opacity: 0.85;
        margin-top: 0.2rem;
        color: rgba(255,255,255,0.9);
    }}
    .gh-sidebar-brand .brand-user {{
        font-size: 0.72rem;
        margin-top: 0.65rem;
        padding-top: 0.65rem;
        border-top: 1px solid rgba(255,255,255,0.1);
        color: rgba(255,255,255,0.65);
    }}

    .gh-status-bar {{
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: var(--gh-radius-sm);
        padding: 0.6rem 0.85rem;
        font-size: 0.72rem;
        color: #86efac;
        font-weight: 600;
    }}

    /* —— Section titles —— */
    .gh-section-head {{
        margin: 1.75rem 0 1rem;
    }}
    .gh-section-head h2 {{
        font-family: var(--gh-font-display) !important;
        font-size: 1.55rem;
        color: var(--gh-crop-primary);
        margin: 0;
        font-weight: 400;
    }}
    .gh-section-head p {{
        color: var(--gh-muted);
        margin: 0.35rem 0 0;
        font-size: 0.92rem;
    }}

    /* —— Profile strip —— */
    .gh-profile-strip {{
        display: flex;
        flex-wrap: wrap;
        gap: 0.65rem 1.25rem;
        align-items: center;
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: var(--gh-radius-lg);
        padding: 1rem 1.35rem;
        margin-bottom: 1.25rem;
        box-shadow: var(--gh-shadow-sm);
    }}
    .gh-profile-strip .pill {{
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.45rem 0.9rem;
        border-radius: 999px;
        font-size: 0.82rem;
        font-weight: 600;
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        color: var(--gh-text);
    }}
    .gh-profile-strip .pill.accent {{
        background: linear-gradient(135deg, #ecfdf5, #f0fdfa);
        border-color: #a7f3d0;
        color: var(--gh-crop-primary);
    }}

    /* —— Cards —— */
    .gh-card {{
        background: white;
        border: 1px solid #e8ecf1;
        border-radius: var(--gh-radius-lg);
        padding: 1.35rem 1.5rem;
        margin-bottom: 1rem;
        box-shadow: var(--gh-shadow-sm);
        transition: box-shadow 0.2s ease, border-color 0.2s ease;
    }}
    .gh-card:hover {{
        box-shadow: var(--gh-shadow-md);
        border-color: #d1fae5;
    }}
    .gh-card h4 {{
        margin: 0 0 0.75rem;
        color: var(--gh-text);
        font-size: 1.05rem;
        font-weight: 700;
        font-family: var(--gh-font) !important;
    }}

    /* —— Stat tiles —— */
    .stat-tile {{
        background: white;
        border-radius: var(--gh-radius-lg);
        padding: 1.35rem 1rem;
        text-align: left;
        border: 1px solid #e8ecf1;
        box-shadow: var(--gh-shadow-sm);
        height: 100%;
        position: relative;
        overflow: hidden;
    }}
    .stat-tile::before {{
        content: '';
        position: absolute;
        left: 0; top: 0; bottom: 0;
        width: 4px;
        background: linear-gradient(180deg, var(--gh-crop-accent), var(--gh-ai-mid));
        border-radius: 4px 0 0 4px;
    }}
    .stat-tile.highlight::before {{
        background: linear-gradient(180deg, #f59e0b, #eab308);
    }}
    .stat-tile.highlight {{
        background: linear-gradient(135deg, #fffbeb, white);
        border-color: #fde68a;
    }}
    .stat-tile .num {{
        font-size: 2rem;
        font-weight: 800;
        color: var(--gh-crop-primary);
        letter-spacing: -0.03em;
        line-height: 1.1;
    }}
    .stat-tile .lbl {{
        font-size: 0.78rem;
        color: var(--gh-muted);
        margin-top: 0.35rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }}

    /* —— Action tiles —— */
    .gh-action-card {{
        border-radius: var(--gh-radius-lg);
        padding: 1.5rem 1.4rem;
        margin-bottom: 0.5rem;
        color: white;
        min-height: 148px;
        position: relative;
        overflow: hidden;
        box-shadow: var(--gh-shadow-md);
    }}
    .gh-action-card::after {{
        content: '';
        position: absolute;
        width: 180px; height: 180px;
        right: -40px; top: -40px;
        background: rgba(255,255,255,0.12);
        border-radius: 50%;
    }}
    .gh-action-card.green {{ background: linear-gradient(145deg, #14532d, #22c55e); }}
    .gh-action-card.teal {{ background: linear-gradient(145deg, #0f766e, #2dd4bf); }}
    .gh-action-card.gold {{ background: linear-gradient(145deg, #92400e, #eab308); }}
    .gh-action-card.earth {{ background: linear-gradient(145deg, #78350f, #d97706); }}
    .gh-action-card.blue {{ background: linear-gradient(145deg, #1e3a5f, #3b82f6); }}
    .gh-action-card .emoji {{
        font-size: 2.75rem;
        position: absolute;
        right: 1rem;
        top: 1rem;
        opacity: 0.25;
    }}
    .gh-action-card h3 {{
        margin: 0;
        font-size: 1.2rem;
        font-weight: 700;
        color: white !important;
        font-family: var(--gh-font) !important;
        position: relative;
        z-index: 1;
    }}
    .gh-action-card p {{
        margin: 0.5rem 0 0;
        font-size: 0.88rem;
        opacity: 0.92;
        color: rgba(255,255,255,0.9) !important;
        line-height: 1.45;
        max-width: 85%;
        position: relative;
        z-index: 1;
    }}
    .gh-action-card .cta {{
        display: inline-block;
        margin-top: 0.85rem;
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        opacity: 0.9;
    }}

    .gh-feature-tile {{
        background: white;
        border-radius: var(--gh-radius-lg);
        border: 1px solid #e8ecf1;
        overflow: hidden;
        box-shadow: var(--gh-shadow-sm);
        height: 100%;
    }}
    .gh-feature-tile .img {{
        height: 120px;
        background-size: cover;
        background-position: center;
    }}
    .gh-feature-tile .body {{
        padding: 1rem 1.15rem;
    }}
    .gh-feature-tile .body strong {{
        color: var(--gh-crop-primary);
        font-size: 0.95rem;
    }}

    /* —— Chat —— */
    .gh-chat-panel {{
        background: #fafbfc;
        border: 1px solid #e2e8f0;
        border-radius: var(--gh-radius-xl);
        padding: 1.25rem 1.35rem;
        margin: 0.25rem 0 1rem;
        box-shadow: inset 0 1px 0 white, var(--gh-shadow-sm);
        min-height: 280px;
    }}

    .gh-chat-toolbar {{
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
        margin-bottom: 0.75rem;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid #e8ecf1;
    }}

    .gh-empty-chat {{
        text-align: center;
        padding: 3rem 1.5rem;
        border-radius: var(--gh-radius-lg);
        background: white;
        border: 2px dashed #cbd5e1;
        margin: 1rem 0;
    }}
    .gh-empty-chat .icon {{ font-size: 3.5rem; margin-bottom: 0.75rem; opacity: 0.9; }}
    .gh-empty-chat .title {{
        font-family: var(--gh-font-display);
        font-size: 1.35rem;
        color: var(--gh-crop-primary);
        margin: 0 0 0.35rem;
    }}
    .gh-empty-chat p {{ color: var(--gh-muted); margin: 0.2rem 0; font-size: 0.92rem; }}

    .chat-row {{ display: flex; gap: 0.75rem; margin: 1rem 0; align-items: flex-start; }}
    .chat-row.user {{ flex-direction: row-reverse; }}
    .chat-avatar {{
        width: 42px; height: 42px;
        border-radius: 14px;
        flex-shrink: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.25rem;
        box-shadow: var(--gh-shadow-sm);
    }}
    .chat-row.user .chat-avatar {{
        background: linear-gradient(135deg, #166534, #22c55e);
        border: none;
    }}
    .chat-row.bot .chat-avatar {{
        background: linear-gradient(135deg, #0f766e, #14b8a6);
        border: none;
    }}

    .farmer-query-bubble {{
        background: linear-gradient(135deg, #166534, #15803d);
        color: white !important;
        padding: 1rem 1.2rem;
        border-radius: 20px 20px 6px 20px;
        max-width: 78%;
        box-shadow: 0 4px 16px rgba(22, 101, 52, 0.25);
        line-height: 1.55;
        font-size: 0.94rem;
    }}
    .farmer-query-bubble strong {{ color: #bbf7d0 !important; }}

    .ai-answer-bubble {{
        background: white;
        border: 1px solid #e2e8f0;
        border-left: 4px solid var(--gh-ai-mid);
        padding: 1rem 1.2rem;
        border-radius: 20px 20px 20px 6px;
        max-width: 82%;
        box-shadow: var(--gh-shadow-sm);
        line-height: 1.6;
        font-size: 0.94rem;
    }}
    .ai-answer-bubble.pending {{
        border-left-color: #f59e0b;
        background: linear-gradient(135deg, #fffbeb, white);
    }}
    .ai-answer-bubble strong {{ color: var(--gh-crop-primary); font-weight: 700; }}
    .ai-answer-bubble em {{ color: var(--gh-muted); font-size: 0.85rem; }}
    .ai-answer-bubble ul, .gh-response ul {{ margin: 0.35rem 0 0.5rem 1.15rem; padding: 0; }}
    .ai-answer-bubble li, .gh-response li {{ margin-bottom: 0.3rem; }}
    .ai-answer-bubble p, .gh-response p {{ margin: 0.35rem 0; }}

    .gh-quick-label {{
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: var(--gh-muted);
        margin: 0.5rem 0 0.65rem;
    }}

    /* —— Badges & alerts —— */
    .gh-badge {{
        display: inline-block;
        padding: 0.3rem 0.75rem;
        border-radius: 999px;
        font-size: 0.7rem;
        font-weight: 700;
        margin-top: 0.4rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }}
    .badge-green {{ background: #dcfce7; color: #166534; }}
    .badge-amber {{ background: #ffedd5; color: #c2410c; }}
    .badge-red {{ background: #fee2e2; color: #b91c1c; }}
    .badge-blue {{ background: #dbeafe; color: #1d4ed8; }}

    .gh-response {{
        background: white;
        border: 1px solid #e2e8f0;
        border-left: 4px solid var(--gh-ai);
        padding: 1.25rem 1.35rem;
        border-radius: var(--gh-radius-lg);
        line-height: 1.65;
        box-shadow: var(--gh-shadow-sm);
    }}
    .gh-pending {{
        background: #fffbeb;
        border-left: 4px solid #f59e0b;
        padding: 1.25rem 1.35rem;
        border-radius: var(--gh-radius-lg);
    }}

    .gh-chip {{
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 999px;
        padding: 0.45rem 1rem;
        font-size: 0.8rem;
        font-weight: 600;
        color: var(--gh-text-soft);
        box-shadow: var(--gh-shadow-sm);
    }}

    .gh-nav-hint {{
        font-size: 0.8rem;
        color: var(--gh-muted);
        margin-bottom: 0.75rem;
        padding: 0.65rem 1rem;
        background: white;
        border-radius: var(--gh-radius-sm);
        border: 1px solid #e8ecf1;
    }}

    /* —— Tabs —— */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 6px;
        background: #f1f5f9;
        padding: 6px;
        border-radius: 14px;
        border: none;
    }}
    .stTabs [data-baseweb="tab"] {{
        background: transparent !important;
        border-radius: 10px !important;
        border: none !important;
        padding: 0.6rem 1.15rem !important;
        font-weight: 600 !important;
        color: var(--gh-muted) !important;
    }}
    .stTabs [aria-selected="true"] {{
        background: white !important;
        color: var(--gh-crop-primary) !important;
        box-shadow: var(--gh-shadow-sm) !important;
    }}

    [data-testid="stFileUploader"] {{
        border: 2px dashed #cbd5e1 !important;
        border-radius: var(--gh-radius-lg) !important;
        background: white !important;
        padding: 0.5rem !important;
    }}
    [data-testid="stFileUploader"]:hover {{
        border-color: var(--gh-crop-accent) !important;
        background: #f0fdf4 !important;
    }}

    [data-testid="stChatInput"] textarea {{
        border-radius: 16px !important;
        border: 1.5px solid #e2e8f0 !important;
        font-size: 0.95rem !important;
    }}
    [data-testid="stChatInput"]:focus-within {{
        border-color: var(--gh-crop-accent) !important;
        box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.15) !important;
    }}

    .stExpander {{
        border: 1px solid #e8ecf1 !important;
        border-radius: var(--gh-radius-lg) !important;
        background: white !important;
        box-shadow: var(--gh-shadow-sm) !important;
    }}

    div[data-testid="stMetric"] {{
        background: white;
        padding: 0.75rem;
        border-radius: var(--gh-radius-sm);
        border: 1px solid #e8ecf1;
    }}

    .auth-split {{
        display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem;
        align-items: stretch; margin-bottom: 1rem;
    }}
    @media (max-width: 900px) {{ .auth-split {{ grid-template-columns: 1fr; }} }}
    .auth-photo {{
        border-radius: var(--gh-radius-xl); min-height: 320px;
        background-size: cover; background-position: center;
        box-shadow: var(--gh-shadow-lg); position: relative; overflow: hidden;
    }}
    .auth-photo .caption {{
        position: absolute; bottom: 0; left: 0; right: 0;
        background: linear-gradient(transparent, rgba(12, 24, 18, 0.92));
        color: white; padding: 1.25rem; font-size: 0.9rem;
    }}
    .auth-shell {{
        background: linear-gradient(160deg, #0c1812, #166534);
        border-radius: var(--gh-radius-xl);
        padding: 2.5rem 2rem;
        text-align: center;
        color: white;
        box-shadow: var(--gh-shadow-lg);
    }}
    .auth-shell .logo {{ font-size: 2.75rem; line-height: 1; }}
    .auth-shell h1 {{ font-family: var(--gh-font-display) !important; color: white !important; }}
    .auth-shell p {{ color: rgba(255,255,255,0.85) !important; }}

    .gh-info-banner {{
        background: linear-gradient(90deg, #ecfdf5, #f0fdfa);
        border: 1px solid #a7f3d0;
        border-radius: var(--gh-radius-lg);
        padding: 1rem 1.25rem;
        margin: 1rem 0;
        font-size: 0.9rem;
        color: var(--gh-text-soft);
        line-height: 1.5;
    }}

    @media (max-width: 768px) {{
        .portal-hero-img h1 {{ font-size: 1.5rem; }}
        .stat-tile .num {{ font-size: 1.5rem; }}
        .block-container {{ padding-left: 1rem !important; padding-right: 1rem !important; }}
    }}
</style>
"""
