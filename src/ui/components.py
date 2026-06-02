"""Enterprise UI — GreenHarvest branding, vivid layout, imagery."""
from __future__ import annotations

import html
import re

import streamlit as st
from src.ui.roles import ROLES, AI_MODULES
from src.ui.brand import GH
from src.ui.assets import AVATARS, image_url_for_css, image_exists
from src.ui.premium_css import build_premium_css

ENTERPRISE_CSS = build_premium_css()


def apply_global_styles():
    st.markdown(ENTERPRISE_CSS, unsafe_allow_html=True)


def auth_hero(title: str = "GreenHarvest", subtitle: str = ""):
    st.markdown(
        f'<div class="auth-shell"><div class="logo">🌾</div>'
        f'<h1>{title}</h1><p>{subtitle}</p></div>',
        unsafe_allow_html=True,
    )


def auth_with_image(title: str, subtitle: str, image_key: str = "login_farm"):
    url = image_url_for_css(image_key)
    photo_style = f"background-image:url({url});" if url else (
        f"background:linear-gradient(145deg,{GH['crop_primary']},{GH['ai']});"
    )
    st.markdown(
        f'<div class="auth-split">'
        f'<div class="auth-photo" style="{photo_style}">'
        f'<div class="caption">🌾 Real support for real farms — advice, experts, and schemes in one place.</div></div>'
        f'<div class="auth-shell" style="display:flex;flex-direction:column;justify-content:center;">'
        f'<div class="logo">🌾</div><h1>{title}</h1><p>{subtitle}</p></div></div>',
        unsafe_allow_html=True,
    )


def sidebar_brand(role_color: str, role_icon: str, role_label: str, display_name: str):
    st.sidebar.markdown(
        f'<div class="gh-sidebar-brand">'
        f'<div class="brand-mark">🌾</div>'
        f'<div class="brand-title">GreenHarvest</div>'
        f'<div class="brand-sub">{role_icon} {role_label}</div>'
        f'<div class="brand-user">Signed in as {display_name}</div></div>',
        unsafe_allow_html=True,
    )


def section_title(title: str, subtitle: str = "") -> None:
    sub = f"<p>{subtitle}</p>" if subtitle else ""
    st.markdown(
        f'<div class="gh-section-head"><h2>{title}</h2>{sub}</div>',
        unsafe_allow_html=True,
    )


def profile_strip(name: str, crop: str, district: str, language: str) -> None:
    st.markdown(
        f'<div class="gh-profile-strip">'
        f'<span class="pill accent">🧑‍🌾 {name}</span>'
        f'<span class="pill">🌱 {crop.title()}</span>'
        f'<span class="pill">📍 {district}</span>'
        f'<span class="pill">🗣️ {language}</span>'
        f"</div>",
        unsafe_allow_html=True,
    )


def info_banner(text: str) -> None:
    st.markdown(f'<div class="gh-info-banner">{text}</div>', unsafe_allow_html=True)


def feature_tile(caption: str, image_key: str | None = None, emoji: str = "🌾") -> None:
    img = ""
    if image_key and image_exists(image_key):
        url = image_url_for_css(image_key)
        img = f'<div class="img" style="background-image:url({url});"></div>'
    else:
        img = (
            f'<div class="img" style="background:linear-gradient(135deg,#ecfdf5,#f0fdfa);'
            f'display:flex;align-items:center;justify-content:center;font-size:2.5rem;">{emoji}</div>'
        )
    st.markdown(
        f'<div class="gh-feature-tile">{img}<div class="body"><strong>{caption}</strong></div></div>',
        unsafe_allow_html=True,
    )


def feature_chips(items: list[tuple[str, str]]):
    chips = "".join(f'<span class="gh-chip">{icon} {label}</span>' for icon, label in items)
    st.markdown(f'<div class="gh-feature-row">{chips}</div>', unsafe_allow_html=True)


def status_bar(text: str, sidebar: bool = False):
    fn = st.sidebar.markdown if sidebar else st.markdown
    fn(f'<div class="gh-status-bar">{text}</div>', unsafe_allow_html=True)


def page_header(title: str, subtitle: str, role: str = "", image_key: str | None = "hero_fields"):
    if role:
        from src.ui.portal import render_main_nav_bar
        render_main_nav_bar(role)

    role_html = ""
    if role and role in ROLES:
        r = ROLES[role]
        role_html = (
            f'<span class="role-pill" style="background:rgba(255,255,255,0.25);">'
            f'{r["icon"]} {r["label"]}</span> '
        )
    if image_key and image_exists(image_key):
        url = image_url_for_css(image_key)
        st.markdown(
            f'<div class="portal-hero-img"><div class="bg" style="background-image:url({url});"></div>'
            f'<div class="overlay">{role_html}<h1>{title}</h1><p>{subtitle}</p></div></div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="portal-hero">{role_html}<h1>{title}</h1><p>{subtitle}</p></div>',
            unsafe_allow_html=True,
        )


def metric_row(metrics: list[tuple[str, str]], highlight_index: int | None = None):
    cols = st.columns(len(metrics))
    for i, (col, (label, value)) in enumerate(zip(cols, metrics)):
        extra = " highlight" if highlight_index == i else ""
        with col:
            st.markdown(
                f'<div class="stat-tile{extra}"><div class="num">{value}</div><div class="lbl">{label}</div></div>',
                unsafe_allow_html=True,
            )


def action_card(title: str, description: str, variant: str = "green", emoji: str = "🌾"):
    st.markdown(
        f'<div class="gh-action-card {variant}"><span class="emoji">{emoji}</span>'
        f'<h3>{title}</h3><p>{description}</p>'
        f'<span class="cta">Open →</span></div>',
        unsafe_allow_html=True,
    )


def confidence_badge(score: float) -> str:
    if score >= 0.75:
        css, label = "badge-green", "High confidence"
    elif score >= 0.55:
        css, label = "badge-amber", "Medium confidence"
    else:
        css, label = "badge-red", "Low confidence"
    return f'<span class="gh-badge {css}">{label}</span>'


def review_status_badge(status: str) -> str:
    mapping = {
        "auto_approved": ("badge-green", "Instant answer"),
        "pending_human": ("badge-amber", "With expert"),
        "approved": ("badge-green", "Expert approved"),
        "rejected": ("badge-red", "Officer follow-up"),
    }
    css, label = mapping.get(status, ("badge-blue", status))
    return f'<span class="gh-badge {css}">{label}</span>'


def format_message_html(text: str, *, markdown: bool = True) -> str:
    """Escape HTML, then render simple markdown (bold, italic, bullet lists)."""
    if not text:
        return ""
    s = html.escape(text)
    if not markdown:
        return s.replace("\n", "<br>")

    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\*)\*([^*\n]+?)\*(?!\*)", r"<em>\1</em>", s)

    blocks: list[str] = []
    in_list = False
    for line in s.split("\n"):
        stripped = line.strip()
        bullet = re.match(r"^[-•]\s+(.+)$", stripped)
        if bullet:
            if not in_list:
                blocks.append('<ul class="chat-md-list">')
                in_list = True
            blocks.append(f"<li>{bullet.group(1)}</li>")
            continue
        if in_list:
            blocks.append("</ul>")
            in_list = False
        if not stripped:
            blocks.append("<br>")
        else:
            blocks.append(f"<p>{line}</p>")
    if in_list:
        blocks.append("</ul>")
    return "".join(blocks)


def render_response_box(text: str, pending: bool = False):
    css_class = "gh-pending" if pending else "gh-response"
    body = format_message_html(text)
    st.markdown(f'<div class="{css_class}">{body}</div>', unsafe_allow_html=True)


def render_ai_pipeline():
    section_title("How your answer is built", "Seven smart steps — from your question to trusted advice")
    cols = st.columns(4)
    icons = ["📥", "🎯", "📚", "🌦️", "💡", "📋", "🚨"]
    for i, (name, desc) in enumerate(AI_MODULES):
        with cols[i % 4]:
            st.markdown(
                f'<div class="gh-card" style="min-height:5rem;">'
                f'<div style="font-size:1.35rem;margin-bottom:0.35rem;">{icons[i]}</div>'
                f'<strong style="color:var(--gh-crop-primary);">{name}</strong><br>'
                f'<span style="color:var(--gh-muted);font-size:0.8rem;">{desc}</span></div>',
                unsafe_allow_html=True,
            )


def chat_panel_start():
    st.markdown('<div class="gh-chat-panel">', unsafe_allow_html=True)


def chat_panel_end():
    st.markdown("</div>", unsafe_allow_html=True)


def section_card(title: str, image_key: str | None = None):
    img = ""
    if image_key and image_exists(image_key):
        url = image_url_for_css(image_key)
        img = f'<div class="tip-card-img" style="background-image:url({url});"></div>'
    st.markdown(f'<div class="gh-card">{img}<h4>{title}</h4>', unsafe_allow_html=True)


def end_card():
    st.markdown("</div>", unsafe_allow_html=True)


def render_chat_message(text: str, is_user: bool = False, review_status: str | None = None):
    body = format_message_html(text, markdown=not is_user)
    avatar = AVATARS["farmer"] if is_user else AVATARS["advisor"]
    row_class = "user" if is_user else "bot"
    bubble_class = "farmer-query-bubble" if is_user else "ai-answer-bubble"
    if not is_user and review_status == "pending_human":
        bubble_class += " pending"
    badge = ""
    if not is_user and review_status:
        badge = review_status_badge(review_status)
    st.markdown(
        f'<div class="chat-row {row_class}">'
        f'<div class="chat-avatar">{avatar}</div>'
        f'<div><div class="{bubble_class}">{body}</div>{badge}</div></div>',
        unsafe_allow_html=True,
    )


