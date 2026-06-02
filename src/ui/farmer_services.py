"""Farmer portal — schemes, mock payments, dealer quote requests."""
from __future__ import annotations

import streamlit as st

from src.integrations.scheme_payment import get_mock_scheme_status
from src.integrations.dealer_locator import find_dealers, INPUT_TYPES
from src.db.repository import save_dealer_request, list_dealer_requests


def render_scheme_payment_tab(farmer_id: str, district: str) -> None:
    st.caption(
        "**Demo only** — simulated PM-KISAN / subsidy status. "
        "GreenHarvest does not access government payment systems or your bank."
    )
    for row in get_mock_scheme_status(farmer_id, district):
        with st.expander(f"📋 {row['scheme']} — {row['status']}", expanded=row["scheme"] == "PM-KISAN"):
            st.markdown(f"**Enrolled:** {'Yes' if row['enrolled'] else 'No'}")
            st.markdown(f"**Benefit:** {row['benefit']}")
            if row.get("installment") and row["installment"] != "—":
                st.markdown(f"**Installment:** {row['installment']}")
            if row.get("last_payment") and row["last_payment"] != "—":
                st.markdown(f"**Last payment (demo):** {row['last_payment']}")
            if row.get("next_expected") and row["next_expected"] != "—":
                st.markdown(f"**Next expected (demo):** {row['next_expected']}")
            st.markdown(f"**Status:** {row['status']}")
            st.caption(f"Reference: `{row['reference']}` · {row['note']}")


def render_dealer_tab(farmer_id: str, profile: dict) -> None:
    st.warning(
        "**Safety:** GreenHarvest does not sell pesticides or chemicals. "
        "We only show licensed dealer information and log a **demo callback request**. "
        "Always follow label doses and consult an agriculture officer for outbreaks."
    )
    district = profile.get("district", "")
    crop = profile.get("crop", "")

    col1, col2 = st.columns(2)
    with col1:
        input_type = st.selectbox("Input type", INPUT_TYPES, index=0)
    with col2:
        st.text_input("Your district", value=district, disabled=True)

    dealers = find_dealers(district, input_type)
    st.markdown("#### Licensed dealers near you (demo directory)")
    for d in dealers:
        lic = "✅ Licensed" if d.get("licensed") else "⚠️ Unverified"
        st.markdown(
            f"**{d['name']}** · {d['village']}, {d['district']} · ~{d['distance_km']} km · {lic}  \n"
            f"Phone (demo): `{d['phone']}` · Inputs: {', '.join(d.get('inputs', []))}"
        )
        if d.get("note"):
            st.caption(d["note"])

    st.markdown("---")
    st.markdown("#### Request a callback (demo — no purchase)")
    with st.form("dealer_quote_form"):
        product = st.text_input("Product or problem (e.g. pink bollworm spray)", placeholder="Optional")
        phone = st.text_input("Your phone", value=profile.get("phone", ""))
        submitted = st.form_submit_button("Log demo quote request", type="primary")
    if submitted:
        save_dealer_request(
            farmer_id=farmer_id,
            district=district,
            crop=crop,
            input_type=input_type,
            product_note=product,
            phone=phone,
        )
        st.success("Demo request logged. A dealer would call you in a real deployment — not processed here.")

    prior = list_dealer_requests(farmer_id, limit=5)
    if prior:
        st.markdown("**Your recent demo requests**")
        for r in prior:
            st.caption(
                f"{r['created_at'][:16]} · {r['input_type']} · {r.get('product_note') or '—'} · status: {r['status']}"
            )
