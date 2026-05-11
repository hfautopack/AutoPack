"""
Home Fragrance AutoPack — Streamlit Web App v4
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
See secrets_template.toml for required credentials.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import uuid, re, requests

# ─────────────────────────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Home Fragrance AutoPack",
    page_icon="🕯️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────
#  STYLES
# ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Hide Streamlit chrome ───────────────────────────────── */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* ── Full window width ───────────────────────────────────── */
.stApp { background: #F4F4F6; }
.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}
section[data-testid="stMainBlockContainer"] {
    padding: 0 !important;
    max-width: 100% !important;
}

/* ── Tab bar ─────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: white;
    border-bottom: 1px solid #DEDEDE;
    padding: 8px 24px 0;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 20px;
    padding: 8px 18px;
    font-size: 13px;
    font-weight: 500;
    color: #1A1A1A;
    background: transparent;
    border: none;
}
.stTabs [aria-selected="true"] {
    background: #111111 !important;
    color: #FFFFFF !important;
    border-radius: 20px;
}
.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] { display: none; }
div[data-testid="stTabs"] > div:first-child { margin-bottom: 0 !important; }

/* ── Page titles ─────────────────────────────────────────── */
.page-title {
    font-size: 26px;
    font-weight: 900;
    color: #1A1A1A;
    letter-spacing: -0.5px;
    padding: 20px 24px 0;
}

/* ── Card grid area — margins + top gap from title ───────── */
.padded {
    padding: 16px 24px 24px;
}

/* ── ALL CAPS on text inputs / textareas ─────────────────── */
input[type="text"], textarea {
    text-transform: uppercase !important;
    text-align: center !important;
    font-size: 11px !important;
    letter-spacing: 0.3px !important;
}

/* ── Remove labels ───────────────────────────────────────── */
div.stTextInput > label { display: none !important; }
div.stTextArea  > label { display: none !important; }

/* ── Compact input rows inside upcoming cards ────────────── */
div.stTextInput > div {
    border: none !important;
    border-bottom: 1px solid #DEDEDE !important;
    border-radius: 0 !important;
    background: white;
    box-shadow: none !important;
}
div.stTextInput > div > div { border: none !important; }
div.stTextInput > div > div > input {
    border: none !important;
    border-radius: 0 !important;
    padding: 8px 8px !important;
    background: white !important;
    box-shadow: none !important;
}
div.stTextInput > div:focus-within {
    border-bottom: 1px solid #888 !important;
    box-shadow: none !important;
}

/* ── Upcoming card container: zero gap between widgets ───── */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: white !important;
    border: 1px solid #DEDEDE !important;
    border-radius: 6px !important;
    overflow: hidden !important;
    padding: 0 !important;
}
div[data-testid="stVerticalBlockBorderWrapper"] > div {
    padding: 0 !important;
    gap: 0 !important;
}
div[data-testid="stVerticalBlock"] { gap: 0 !important; }
div[data-testid="stVerticalBlock"] > div[data-testid="element-container"] {
    margin: 0 !important;
    padding: 0 !important;
}
div[data-testid="stVerticalBlockBorderWrapper"]
    div[data-testid="stVerticalBlock"] > * {
    margin-bottom: 0 !important;
    margin-top: 0 !important;
}

/* ── Read-only text rows ─────────────────────────────────── */
.ro-field {
    background: white;
    border-bottom: 1px solid #DEDEDE;
    padding: 7px 8px;
    font-size: 11px;
    text-align: center;
    text-transform: uppercase;
    color: #1A1A1A;
    letter-spacing: 0.3px;
    min-height: 32px;
    box-sizing: border-box;
}
.ro-field.placeholder { color: #C7C7CC; }

/* ── Clickable cards (CW + Reshoot) ──────────────────────── */
.ap-card {
    background: white;
    border: 1px solid #DEDEDE;
    border-radius: 6px;
    overflow: hidden;
    margin-bottom: 8px;
    cursor: pointer;
    user-select: none;
    transition: box-shadow 0.15s;
}
.ap-card:hover { box-shadow: 0 2px 10px rgba(0,0,0,0.10); }
.ap-card.selected {
    border: 2px solid #1A73E8 !important;
    box-shadow: 0 0 0 2px rgba(26,115,232,0.15);
}

/* ── Image area (3:4 ratio) ──────────────────────────────── */
.img-area {
    position: relative;
    width: 100%;
    aspect-ratio: 3 / 4;
    overflow: hidden;
    background: #EBEBEB;
}
.img-area img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
}
.img-placeholder {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: #C7C7CC;
    font-size: 11px;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    cursor: pointer;
    gap: 8px;
}
.img-placeholder svg { opacity: 0.4; }

/* ── Hover overlay (action buttons on image) ─────────────── */
.img-overlay {
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    opacity: 0;
    transition: opacity 0.18s;
    pointer-events: none;
}
.img-area:hover .img-overlay {
    opacity: 1;
    pointer-events: auto;
}
/* Colored circle buttons */
.hbtn {
    position: absolute;
    width: 38px;
    height: 38px;
    border-radius: 50%;
    border: none;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 17px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.25);
    transition: transform 0.1s, filter 0.1s;
}
.hbtn:hover { transform: scale(1.08); filter: brightness(1.1); }
.hbtn-tl  { top: 10px; left: 10px;  background: #111111; color: white; }
.hbtn-tr  { top: 10px; right: 10px; background: #E63946; color: white; }
.hbtn-tr2 { top: 10px; right: 56px; background: #1A73E8; color: white; }

/* ── Catalog card ────────────────────────────────────────── */
.cat-card {
    background: white;
    border: 1px solid #DEDEDE;
    border-radius: 6px;
    overflow: hidden;
    margin-bottom: 4px;
}
.cat-card-info {
    padding: 8px;
    text-align: center;
    font-size: 11px;
    text-transform: uppercase;
    color: #1A1A1A;
    border-bottom: 1px solid #DEDEDE;
    line-height: 1.9;
}

/* ── URL paste input (image field) ───────────────────────── */
.url-row div.stTextInput > div {
    border: none !important;
    border-top: 1px solid #DEDEDE !important;
    border-radius: 0 !important;
    background: #FAFAFA !important;
}
.url-row div.stTextInput > div > div > input {
    font-size: 10px !important;
    text-transform: none !important;
    text-align: left !important;
    color: #9A9A9F !important;
    padding: 6px 8px !important;
}

/* ── Delete confirmation ─────────────────────────────────── */
.del-bar {
    background: #FFF5F5;
    border-top: 1px solid #FECACA;
    padding: 7px 8px;
    text-align: center;
    font-size: 11px;
    font-weight: 600;
    color: #E63946;
    text-transform: uppercase;
    letter-spacing: 0.3px;
}

/* ── Buttons ─────────────────────────────────────────────── */
div.stButton > button {
    border-radius: 4px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.4px;
    border: none !important;
    padding: 4px 10px !important;
}
div.stButton > button[kind="primary"]   { background: #111111 !important; color: white !important; }
div.stButton > button[kind="secondary"] { background: #E8E8E8 !important; color: #111111 !important; }

/* ── Action bar ──────────────────────────────────────────── */
.action-bar { padding: 0 24px 12px; display: flex; gap: 12px; }

/* ── Column gap ──────────────────────────────────────────── */
div[data-testid="stHorizontalBlock"] { gap: 10px !important; }

/* ── Streamlit image ─────────────────────────────────────── */
div[data-testid="stImage"] img { border-top: 1px solid #DEDEDE; border-bottom: 1px solid #DEDEDE; }
div[data-testid="stImage"] { margin: 0 !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
#  INLINE JS HELPER  (onclick attributes — React allows these)
# ─────────────────────────────────────────────────────────────────
def _js(action: str, iid: str, stop_prop: bool = False) -> str:
    """Return inline JS that sets query params and navigates.
    React strips <script> tags but onclick attributes execute normally."""
    sp = "event.stopPropagation();" if stop_prop else ""
    return (
        f"{sp}"
        f"var u=new URL(window.location.href);"
        f"u.searchParams.set('ap_action','{action}');"
        f"u.searchParams.set('ap_id','{iid}');"
        f"window.location.href=u.toString();"
    )


# ─────────────────────────────────────────────────────────────────
#  GOOGLE SERVICES
# ─────────────────────────────────────────────────────────────────
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SHEET_HEADERS = [
    "id", "brand", "candle_name", "season", "pvr",
    "scent_notes", "ops_notes", "image_url", "status",
    "created_at", "updated_at",
]


@st.cache_resource
def _get_gc():
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=SCOPES
    )
    return gspread.authorize(creds)


def _sheet():
    ws = _get_gc().open_by_key(st.secrets["sheet_id"]).sheet1
    if not ws.get_all_values():
        ws.append_row(SHEET_HEADERS)
    elif ws.row_values(1) != SHEET_HEADERS:
        ws.update("A1", [SHEET_HEADERS])
    return ws


@st.cache_data(ttl=3)
def load_items() -> list[dict]:
    try:
        return _sheet().get_all_records()
    except Exception as e:
        st.error(f"Could not load data: {e}")
        return []


def _clear():
    load_items.clear()


# ─────────────────────────────────────────────────────────────────
#  DATA HELPERS
# ─────────────────────────────────────────────────────────────────
def add_item() -> str:
    new_id = str(uuid.uuid4())
    now    = datetime.now().strftime("%Y-%m-%d %H:%M")
    _sheet().append_row([new_id, "", "", "", "", "", "", "", "upcoming", now, now])
    _clear()
    return new_id


def save_field(item_id: str, field: str, raw_value: str):
    value = raw_value.strip() if field == "image_url" else raw_value.upper().strip()
    ws    = _sheet()
    recs  = ws.get_all_records()
    col   = SHEET_HEADERS.index(field) + 1
    for i, r in enumerate(recs):
        if str(r["id"]) == str(item_id):
            ws.update_cell(i + 2, col, value)
            ws.update_cell(i + 2, SHEET_HEADERS.index("updated_at") + 1,
                           datetime.now().strftime("%Y-%m-%d %H:%M"))
            break
    _clear()


def set_status(item_id: str, status: str):
    ws   = _sheet()
    recs = ws.get_all_records()
    for i, r in enumerate(recs):
        if str(r["id"]) == str(item_id):
            ws.update_cell(i + 2, SHEET_HEADERS.index("status") + 1, status)
            ws.update_cell(i + 2, SHEET_HEADERS.index("updated_at") + 1,
                           datetime.now().strftime("%Y-%m-%d %H:%M"))
            break
    _clear()


def set_status_many(ids: list[str], status: str):
    ws     = _sheet()
    recs   = ws.get_all_records()
    id_set = set(str(i) for i in ids)
    now    = datetime.now().strftime("%Y-%m-%d %H:%M")
    for i, r in enumerate(recs):
        if str(r["id"]) in id_set:
            ws.update_cell(i + 2, SHEET_HEADERS.index("status") + 1, status)
            ws.update_cell(i + 2, SHEET_HEADERS.index("updated_at") + 1, now)
    _clear()


def copy_to_reshoot(item: dict):
    now    = datetime.now().strftime("%Y-%m-%d %H:%M")
    new_id = str(uuid.uuid4())
    _sheet().append_row([
        new_id, item.get("brand",""), item.get("candle_name",""),
        item.get("season",""), item.get("pvr",""), item.get("scent_notes",""),
        item.get("ops_notes",""), item.get("image_url",""),
        "reshoot", now, now,
    ])
    _clear()
    return new_id


def delete_item(item_id: str):
    ws   = _sheet()
    recs = ws.get_all_records()
    for i, r in enumerate(recs):
        if str(r["id"]) == str(item_id):
            ws.delete_rows(i + 2)
            break
    _clear()


def remove_last_empty():
    items    = load_items()
    upcoming = [i for i in items if i.get("status") == "upcoming"]
    for item in reversed(upcoming):
        if not any(item.get(f,"").strip()
                   for f in ["brand","candle_name","season","pvr",
                              "scent_notes","ops_notes","image_url"]):
            delete_item(item["id"])
            return


def send_slack(message: str):
    try:
        webhook = st.secrets.get("slack_webhook_url", "")
        if webhook:
            requests.post(webhook, json={"text": message}, timeout=5)
    except Exception:
        pass


# ─────────────────────────────────────────────────────────────────
#  SESSION STATE + ACTION HANDLER
# ─────────────────────────────────────────────────────────────────
def _init():
    defaults = {
        "sel_cw":            set(),
        "sel_reshoot":       set(),
        "confirm_delete_id": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def _handle_actions():
    action = st.query_params.get("ap_action", "")
    ap_id  = st.query_params.get("ap_id", "")
    if not action:
        return
    st.query_params.clear()

    if action == "cw_sel":
        if ap_id in st.session_state.sel_cw:
            st.session_state.sel_cw.discard(ap_id)
        else:
            st.session_state.sel_cw.add(ap_id)
        st.rerun()

    elif action == "cw_back":
        st.session_state.sel_cw.discard(ap_id)
        set_status(ap_id, "upcoming")
        st.rerun()

    elif action == "cat_reshoot":
        items = load_items()
        item  = next((i for i in items if str(i["id"]) == ap_id), None)
        if item:
            copy_to_reshoot(item)
            send_slack(
                f"🔁 *Reshoot requested*\n"
                f"*{_fval(item,'candle_name') or 'Unnamed'}*"
                f" — {_fval(item,'brand') or ''}"
            )
        st.rerun()

    elif action == "cat_delete_ask":
        st.session_state.confirm_delete_id = ap_id
        st.rerun()

    elif action == "re_sel":
        if ap_id in st.session_state.sel_reshoot:
            st.session_state.sel_reshoot.discard(ap_id)
        else:
            st.session_state.sel_reshoot.add(ap_id)
        st.rerun()


# ─────────────────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────────────────
def _fval(item: dict, field: str) -> str:
    return str(item.get(field, "") or "").upper().strip()


def _img(item: dict) -> str:
    return item.get("image_url", "") or ""


def _ro_field(value: str, placeholder: str) -> str:
    cls = "ro-field" if value else "ro-field placeholder"
    return f'<div class="{cls}">{value or placeholder}</div>'


def _full_word_search(items: list[dict], query: str) -> list[dict]:
    if not query.strip():
        return items
    tokens     = query.strip().split()
    searchable = ["brand","candle_name","season","pvr","scent_notes","ops_notes"]
    results    = []
    for item in items:
        haystack = " ".join(str(item.get(f,"") or "") for f in searchable).upper()
        if all(re.search(r'\b' + re.escape(t.upper()) + r'\b', haystack) for t in tokens):
            results.append(item)
    return results


def _img_area_html(img_url: str, overlay_html: str = "") -> str:
    """3:4 image area with optional hover overlay."""
    if img_url:
        inner = f'<img src="{img_url}" alt="">'
    else:
        inner = (
            '<div class="img-placeholder">'
            '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" '
            'stroke="#C7C7CC" stroke-width="1.5">'
            '<rect x="3" y="3" width="18" height="18" rx="2"/>'
            '<circle cx="8.5" cy="8.5" r="1.5"/>'
            '<path d="M21 15l-5-5L5 21"/>'
            '</svg>'
            '<span>No image</span>'
            '</div>'
        )
    overlay = (f'<div class="img-overlay">{overlay_html}</div>'
               if overlay_html else "")
    return f'<div class="img-area">{inner}{overlay}</div>'


# ─────────────────────────────────────────────────────────────────
#  PAGE: UPCOMING IN STUDIO
# ─────────────────────────────────────────────────────────────────
def page_upcoming():
    st.markdown('<div class="page-title">⏱ UPCOMING IN STUDIO</div>',
                unsafe_allow_html=True)

    items    = load_items()
    upcoming = [i for i in items if i.get("status") == "upcoming"]

    st.markdown('<div class="padded">', unsafe_allow_html=True)

    COLS        = 6
    total_slots = len(upcoming) + 1
    n_rows      = max(1, -(-total_slots // COLS))

    slot = 0
    for row in range(n_rows):
        cols = st.columns(COLS, gap="small")
        for col_idx in range(COLS):
            if slot < len(upcoming):
                with cols[col_idx]:
                    _upcoming_card(upcoming[slot])
                slot += 1
            elif slot == len(upcoming):
                with cols[col_idx]:
                    st.markdown("<div style='padding-top:4px'>", unsafe_allow_html=True)
                    if st.button("＋", key="add_card", type="primary",
                                 help="Add new product slot"):
                        add_item()
                        st.rerun()
                    st.markdown('<div style="margin-top:8px">', unsafe_allow_html=True)
                    if st.button("－", key="rem_card",
                                 help="Remove last empty slot"):
                        remove_last_empty()
                        st.rerun()
                    st.markdown("</div></div>", unsafe_allow_html=True)
                slot += 1
        if slot > len(upcoming):
            break

    st.markdown('</div>', unsafe_allow_html=True)


def _upcoming_card(item: dict):
    iid = str(item["id"])

    with st.container(border=True):
        for field, ph in [
            ("brand",       "BRAND/COLLECTION"),
            ("candle_name", "CANDLE NAME"),
            ("season",      "SEASON"),
            ("pvr",         "PVR"),
        ]:
            key = f"up_{iid}_{field}"
            val = _fval(item, field)
            def _save(f=field, k=key, i=iid, v0=val):
                v = st.session_state.get(k, "")
                if v.upper().strip() != v0:
                    save_field(i, f, v)
            st.text_input(ph, value=val, key=key, on_change=_save,
                          placeholder=ph, label_visibility="collapsed")

        # Image area
        img_url = _img(item)
        st.markdown(_img_area_html(img_url), unsafe_allow_html=True)

        # URL paste field
        key_url = f"up_url_{iid}"
        st.markdown('<div class="url-row">', unsafe_allow_html=True)
        new_url = st.text_input(
            "url", value=img_url, placeholder="PASTE IMAGE URL",
            key=key_url, label_visibility="collapsed"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        if new_url.strip() != img_url and new_url.strip():
            save_field(iid, "image_url", new_url.strip())
            st.rerun()

        for field, ph in [
            ("scent_notes", "SCENT NOTES"),
            ("ops_notes",   "OPS NOTES"),
        ]:
            key = f"up_{iid}_{field}"
            val = _fval(item, field)
            def _save2(f=field, k=key, i=iid, v0=val):
                v = st.session_state.get(k, "")
                if v.upper().strip() != v0:
                    save_field(i, f, v)
            st.text_input(ph, value=val, key=key, on_change=_save2,
                          placeholder=ph, label_visibility="collapsed")

        st.markdown(
            '<div style="border-top:1px solid #DEDEDE;background:white;padding:6px 8px;">',
            unsafe_allow_html=True
        )
        c1, c2 = st.columns([4, 1])
        with c1:
            if st.button("→ CURRENT WEEK", key=f"up_adv_{iid}",
                         type="primary", use_container_width=True):
                for f in ["brand","candle_name","season","pvr","scent_notes","ops_notes"]:
                    k = f"up_{iid}_{f}"
                    if k in st.session_state:
                        save_field(iid, f, st.session_state[k])
                set_status(iid, "current_week")
                st.rerun()
        with c2:
            if st.button("🗑", key=f"up_del_{iid}", type="secondary",
                         use_container_width=True, help="Delete"):
                delete_item(iid)
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
#  PAGE: CURRENT WEEK
# ─────────────────────────────────────────────────────────────────
def page_current_week():
    items = load_items()
    cw    = [i for i in items if i.get("status") == "current_week"]

    st.markdown('<div class="page-title">☐ CURRENT WEEK</div>',
                unsafe_allow_html=True)

    sel: set = st.session_state.sel_cw

    if sel:
        st.markdown('<div class="action-bar">', unsafe_allow_html=True)
        c1, _ = st.columns([2, 8])
        with c1:
            if st.button(f"MOVE TO CATALOG  ({len(sel)})",
                         type="primary", use_container_width=True):
                set_status_many(list(sel), "catalog")
                st.session_state.sel_cw = set()
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    if not cw:
        st.markdown(
            '<div style="text-align:center;color:#9A9A9F;font-size:14px;'
            'padding:80px 20px;">No items yet — add from Upcoming in Studio.</div>',
            unsafe_allow_html=True)
        return

    st.markdown('<div class="padded">', unsafe_allow_html=True)
    cols = st.columns(6, gap="small")
    for idx, item in enumerate(cw):
        with cols[idx % 6]:
            _cw_card(item)
    st.markdown('</div>', unsafe_allow_html=True)


def _cw_card(item: dict):
    iid      = str(item["id"])
    selected = iid in st.session_state.sel_cw
    sel_cls  = "selected" if selected else ""

    fields_html = "".join(
        _ro_field(_fval(item, f), ph)
        for f, ph in [
            ("brand","BRAND/COLLECTION"), ("candle_name","CANDLE NAME"),
            ("season","SEASON"), ("pvr","PVR"),
        ]
    )
    bottom_html = "".join(
        _ro_field(_fval(item, f), ph)
        for f, ph in [("scent_notes","SCENT NOTES"), ("ops_notes","OPS NOTES")]
    )

    # Back-arrow button in top-left of image on hover
    arrow = (
        f'<button class="hbtn hbtn-tl" '
        f'onclick="{_js("cw_back", iid, stop_prop=True)}" title="Return to Upcoming">'
        f'←</button>'
    )
    img_html = _img_area_html(_img(item), arrow)

    # Entire card clickable → toggle selection
    st.markdown(
        f'<div class="ap-card {sel_cls}" onclick="{_js("cw_sel", iid)}">'
        f'{fields_html}{img_html}{bottom_html}'
        f'</div>',
        unsafe_allow_html=True
    )


# ─────────────────────────────────────────────────────────────────
#  PAGE: HOME FRAGRANCE CATALOG
# ─────────────────────────────────────────────────────────────────
def page_catalog():
    items   = load_items()
    catalog = [i for i in items if i.get("status") == "catalog"]
    catalog.sort(key=lambda x: x.get("updated_at",""), reverse=True)

    st.markdown('<div class="page-title">≡ HOME FRAGRANCE CATALOG</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="padded">', unsafe_allow_html=True)

    query    = st.text_input("Search", placeholder="🔍  Search library…",
                             key="cat_search", label_visibility="collapsed")
    filtered = _full_word_search(catalog, query)

    if not filtered:
        msg = (f'No results for "{query}".' if query
               else "No archived items yet. Items moved from Current Week will appear here.")
        st.markdown(
            f'<div style="text-align:center;color:#9A9A9F;font-size:14px;padding:60px 0;">'
            f'{msg}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        return

    cols = st.columns(6, gap="small")
    for idx, item in enumerate(filtered):
        with cols[idx % 6]:
            _catalog_card(item)

    st.markdown('</div>', unsafe_allow_html=True)


def _catalog_card(item: dict):
    iid     = str(item["id"])
    confirm = st.session_state.get("confirm_delete_id") == iid

    info_lines = [
        (_fval(item, f) or ph, bool(_fval(item, f)))
        for f, ph in [
            ("brand","BRAND/COLLECTION"), ("candle_name","CANDLE NAME"),
            ("season","SEASON"), ("pvr","PVR"),
        ]
    ]
    info_html = "<br>".join(
        f'<span style="color:{"#1A1A1A" if has_val else "#C7C7CC"}">{text}</span>'
        for text, has_val in info_lines
    )

    # ♻ (blue) and 🗑 (red) appear on hover in top-right of image
    icons = (
        f'<button class="hbtn hbtn-tr2" '
        f'onclick="{_js("cat_reshoot", iid, stop_prop=True)}" title="Request Reshoot">♻</button>'
        f'<button class="hbtn hbtn-tr" '
        f'onclick="{_js("cat_delete_ask", iid, stop_prop=True)}" title="Delete">🗑</button>'
    )
    img_html = _img_area_html(_img(item), icons)

    st.markdown(
        f'<div class="cat-card">'
        f'<div class="cat-card-info">{info_html}</div>'
        f'{img_html}</div>',
        unsafe_allow_html=True
    )

    # URL paste field
    key_url = f"cat_url_{iid}"
    st.markdown('<div class="url-row">', unsafe_allow_html=True)
    new_url = st.text_input(
        "url", value=_img(item), placeholder="PASTE IMAGE URL FROM DAM",
        key=key_url, label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    if new_url.strip() != _img(item) and new_url.strip():
        save_field(iid, "image_url", new_url.strip())
        st.rerun()

    # Delete confirmation
    if confirm:
        st.markdown('<div class="del-bar">Are you sure?</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("YES, DELETE", key=f"cat_conf_{iid}",
                         type="primary", use_container_width=True):
                delete_item(iid)
                st.session_state.confirm_delete_id = None
                st.rerun()
        with c2:
            if st.button("CANCEL", key=f"cat_canc_{iid}",
                         type="secondary", use_container_width=True):
                st.session_state.confirm_delete_id = None
                st.rerun()


# ─────────────────────────────────────────────────────────────────
#  PAGE: RESHOOT REQUESTS
# ─────────────────────────────────────────────────────────────────
def page_reshoot():
    items   = load_items()
    reshoot = [i for i in items if i.get("status") == "reshoot"]

    st.markdown('<div class="page-title">↺ RESHOOT REQUESTS</div>',
                unsafe_allow_html=True)

    sel: set = st.session_state.sel_reshoot

    if sel:
        st.markdown('<div class="action-bar">', unsafe_allow_html=True)
        c1, c2, _ = st.columns([2, 2, 6])
        with c1:
            if st.button(f"MOVE TO UPCOMING  ({len(sel)})",
                         type="primary", use_container_width=True):
                sel_items = [i for i in reshoot if str(i["id"]) in sel]
                set_status_many(list(sel), "upcoming")
                for item in sel_items:
                    send_slack(
                        f"✅ *Reshoot accepted → Upcoming*\n"
                        f"*{_fval(item,'candle_name') or 'Unnamed'}*"
                        f" — {_fval(item,'brand') or ''}"
                    )
                st.session_state.sel_reshoot = set()
                st.rerun()
        with c2:
            if st.button(f"DECLINE  ({len(sel)})",
                         type="secondary", use_container_width=True):
                sel_items = [i for i in reshoot if str(i["id"]) in sel]
                for item in sel_items:
                    delete_item(str(item["id"]))
                    send_slack(
                        f"❌ *Reshoot declined*\n"
                        f"*{_fval(item,'candle_name') or 'Unnamed'}*"
                        f" — {_fval(item,'brand') or ''}"
                    )
                st.session_state.sel_reshoot = set()
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    if not reshoot:
        st.markdown("""
        <div style="background:white;border:1px solid #DEDEDE;border-radius:8px;
                    margin:0 24px;padding:70px;text-align:center;">
            <div style="font-size:36px;color:#C7C7CC;margin-bottom:12px;">↺</div>
            <div style="font-size:15px;color:#9A9A9F;">No reshoot requests yet</div>
        </div>""", unsafe_allow_html=True)
        return

    st.markdown('<div class="padded">', unsafe_allow_html=True)
    cols = st.columns(6, gap="small")
    for idx, item in enumerate(reshoot):
        with cols[idx % 6]:
            _reshoot_card(item)
    st.markdown('</div>', unsafe_allow_html=True)


def _reshoot_card(item: dict):
    iid      = str(item["id"])
    selected = iid in st.session_state.sel_reshoot
    sel_cls  = "selected" if selected else ""

    fields_html = "".join(
        _ro_field(_fval(item, f), ph)
        for f, ph in [
            ("brand","BRAND/COLLECTION"), ("candle_name","CANDLE NAME"),
            ("season","SEASON"), ("pvr","PVR"),
        ]
    )
    img_html   = _img_area_html(_img(item))
    scent_html = _ro_field(_fval(item, "scent_notes"), "SCENT NOTES")

    # Entire card clickable → toggle selection
    st.markdown(
        f'<div class="ap-card {sel_cls}" onclick="{_js("re_sel", iid)}">'
        f'{fields_html}{img_html}{scent_html}'
        f'</div>',
        unsafe_allow_html=True
    )

    # Editable ops notes — flush below card
    key_ops = f"re_ops_{iid}"
    def _save_ops(k=key_ops, i=iid):
        save_field(i, "ops_notes", st.session_state.get(k, ""))

    st.markdown(
        '<div style="background:white;border:1px solid #DEDEDE;border-top:none;'
        'border-radius:0 0 6px 6px;overflow:hidden;margin-top:-8px;margin-bottom:8px;">',
        unsafe_allow_html=True
    )
    st.text_input("OPS NOTES", value=_fval(item, "ops_notes"),
                  key=key_ops, on_change=_save_ops, placeholder="OPS NOTES",
                  label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────────────────
def main():
    _init()
    _handle_actions()

    tab1, tab2, tab3, tab4 = st.tabs([
        "⏱  Upcoming in Studio",
        "☐  Current Week",
        "≡  Home Fragrance Catalog",
        "↺  Reshoot Requests",
    ])
    with tab1: page_upcoming()
    with tab2: page_current_week()
    with tab3: page_catalog()
    with tab4: page_reshoot()


if __name__ == "__main__":
    main()
