"""
Home Fragrance AutoPack — Streamlit Web App v2
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
See secrets_template.toml for required credentials.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from datetime import datetime
import uuid, io, re, requests

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
div[data-testid="stTabs"] > div:first-child {
    margin-bottom: 0 !important;
}

/* ── Page titles ─────────────────────────────────────────── */
.page-title {
    font-size: 26px;
    font-weight: 900;
    color: #1A1A1A;
    letter-spacing: -0.5px;
    padding: 20px 24px 4px;
}
.page-title-icon { margin-right: 10px; }

/* ── ALL CAPS on every text input & textarea ─────────────── */
input[type="text"], textarea {
    text-transform: uppercase !important;
    text-align: center !important;
    font-size: 11px !important;
    letter-spacing: 0.3px !important;
}
/* Exception: search bar stays normal */
input.search-input {
    text-transform: none !important;
    text-align: left !important;
    font-size: 14px !important;
}

/* ── Remove labels from inputs ───────────────────────────── */
div.stTextInput  > label { display: none !important; }
div.stTextArea   > label { display: none !important; }

/* ── Input field styling (bordered rows in cards) ────────── */
div.stTextInput > div {
    border: none !important;
    border-bottom: 1px solid #DEDEDE !important;
    border-radius: 0 !important;
    background: white;
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

/* Ops-notes textarea */
div.stTextArea > div { border: none !important; border-top: 1px solid #DEDEDE !important; border-radius: 0 !important; }
div.stTextArea > div > div > textarea {
    border: none !important;
    border-radius: 0 !important;
    background: white !important;
    min-height: 60px !important;
    font-size: 11px !important;
    text-align: center !important;
    text-transform: uppercase !important;
    box-shadow: none !important;
}

/* ── File uploader (image area) ──────────────────────────── */
div[data-testid="stFileUploaderDropzone"] {
    background: white !important;
    border: none !important;
    border-radius: 0 !important;
    padding: 18px 8px !important;
    min-height: 180px;
    display: flex;
    align-items: center;
    justify-content: center;
}
div[data-testid="stFileUploaderDropzoneInstructions"] > div > span {
    font-size: 11px !important;
    color: #C7C7CC !important;
}
div[data-testid="stFileUploaderDropzoneInstructions"] > div > small { display: none; }
div[data-testid="stFileUploader"] section > button { display: none; }

/* ── Upcoming card column borders ────────────────────────── */
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
/* Remove gap between stacked inputs */
div[data-testid="stVerticalBlock"] > div[data-testid="element-container"] {
    margin: 0 !important;
}

/* ── Read-only field rows (CW / Reshoot) ─────────────────── */
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
}
.ro-field.placeholder { color: #C7C7CC; }
.ro-card {
    background: white;
    border: 1px solid #DEDEDE;
    border-radius: 6px;
    overflow: hidden;
    margin-bottom: 8px;
}
.ro-card.selected { border: 2px solid #1A73E8 !important; }
.ro-card-img { width: 100%; display: block; object-fit: cover; height: 200px; }
.ro-card-noimg {
    height: 200px;
    background: #EBEBEB;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #C7C7CC;
    font-size: 13px;
}

/* ── Catalog card ────────────────────────────────────────── */
.cat-card {
    background: white;
    border: 1px solid #DEDEDE;
    border-radius: 6px;
    overflow: hidden;
    margin-bottom: 8px;
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
.cat-card-img { width: 100%; height: 220px; object-fit: cover; display: block; }
.cat-card-noimg {
    height: 220px;
    background: #EBEBEB;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #C7C7CC;
    font-size: 13px;
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
div.stButton > button[kind="primary"] {
    background: #111111 !important;
    color: white !important;
}
div.stButton > button[kind="secondary"] {
    background: #E8E8E8 !important;
    color: #111111 !important;
}
/* Circle add/remove buttons */
button.circle-add, button.circle-remove {
    width: 44px; height: 44px;
    border-radius: 50%;
    font-size: 22px;
    font-weight: 700;
    border: none;
    cursor: pointer;
    box-shadow: 0 2px 10px rgba(0,0,0,0.2);
}

/* ── Action bar (shown when cards selected) ──────────────── */
.action-bar {
    background: transparent;
    padding: 12px 24px;
    display: flex;
    gap: 12px;
    align-items: center;
}
.action-bar-btn {
    padding: 12px 28px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 800;
    letter-spacing: 0.6px;
    border: none;
    cursor: pointer;
    box-shadow: 0 4px 16px rgba(0,0,0,0.2);
}
.action-bar-btn.black  { background: #111; color: white; }
.action-bar-btn.red    { background: #E63946; color: white; }
.action-bar-btn.blue   { background: #1A73E8; color: white; }

/* ── Search bar ──────────────────────────────────────────── */
div[data-testid="stTextInput"].search-wrapper > div {
    border: 1px solid #DEDEDE !important;
    border-radius: 24px !important;
    border-bottom: 1px solid #DEDEDE !important;
    background: white;
}
div[data-testid="stTextInput"].search-wrapper > div > div > input {
    text-transform: none !important;
    text-align: left !important;
    font-size: 14px !important;
    border-radius: 24px !important;
    padding-left: 14px !important;
}

/* ── Content padding ─────────────────────────────────────── */
.padded { padding: 0 24px; }

/* ── Column gap fix ──────────────────────────────────────── */
div[data-testid="stHorizontalBlock"] { gap: 10px !important; }

/* ── Streamlit image display ─────────────────────────────── */
div[data-testid="stImage"] img {
    border-top: 1px solid #DEDEDE;
    border-bottom: 1px solid #DEDEDE;
}
div[data-testid="stImage"] { margin: 0 !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
#  GOOGLE SERVICES
# ─────────────────────────────────────────────────────────────────
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
SHEET_HEADERS = [
    "id", "brand", "candle_name", "season", "pvr",
    "scent_notes", "ops_notes", "image_url", "status",
    "created_at", "updated_at",
]


@st.cache_resource
def _get_services():
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=SCOPES
    )
    gc    = gspread.authorize(creds)
    drive = build("drive", "v3", credentials=creds)
    return gc, drive


def _sheet():
    gc, _ = _get_services()
    ws = gc.open_by_key(st.secrets["sheet_id"]).sheet1
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
    value = raw_value.upper().strip()
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
    ws   = _sheet()
    recs = ws.get_all_records()
    id_set = set(str(i) for i in ids)
    now  = datetime.now().strftime("%Y-%m-%d %H:%M")
    s_col = SHEET_HEADERS.index("status") + 1
    u_col = SHEET_HEADERS.index("updated_at") + 1
    for i, r in enumerate(recs):
        if str(r["id"]) in id_set:
            ws.update_cell(i + 2, s_col, status)
            ws.update_cell(i + 2, u_col, now)
    _clear()


def copy_to_reshoot(item: dict):
    """Create an independent copy of a catalog item in the reshoot queue."""
    now    = datetime.now().strftime("%Y-%m-%d %H:%M")
    new_id = str(uuid.uuid4())
    _sheet().append_row([
        new_id,
        item.get("brand", ""),
        item.get("candle_name", ""),
        item.get("season", ""),
        item.get("pvr", ""),
        item.get("scent_notes", ""),
        item.get("ops_notes", ""),
        item.get("image_url", ""),
        "reshoot",
        now, now,
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
    """Remove the most recently added item that has no data filled in."""
    items = load_items()
    upcoming = [i for i in items if i.get("status") == "upcoming"]
    for item in reversed(upcoming):
        fields = ["brand","candle_name","season","pvr","scent_notes","ops_notes","image_url"]
        if not any(item.get(f,"").strip() for f in fields):
            delete_item(item["id"])
            return


def upload_image(file_bytes: bytes, filename: str, mime: str) -> str:
    _, drive = _get_services()
    folder   = st.secrets["drive_folder_id"]
    media    = MediaIoBaseUpload(io.BytesIO(file_bytes), mimetype=mime)
    f = drive.files().create(
        body={"name": filename, "parents": [folder]},
        media_body=media, fields="id"
    ).execute()
    fid = f["id"]
    drive.permissions().create(
        fileId=fid, body={"type": "anyone", "role": "reader"}
    ).execute()
    return f"https://drive.google.com/uc?export=view&id={fid}"


def send_slack(message: str):
    """Send a message to the configured Slack webhook (optional)."""
    try:
        webhook = st.secrets.get("slack_webhook_url", "")
        if webhook:
            requests.post(webhook, json={"text": message}, timeout=5)
    except Exception:
        pass  # Slack is optional — never block the app


# ─────────────────────────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────────────────────────
def _init():
    for k, v in {
        "sel_cw":      set(),
        "sel_reshoot": set(),
    }.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init()


# ─────────────────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────────────────
def _fval(item: dict, field: str) -> str:
    return str(item.get(field, "") or "").upper().strip()


def _img(item: dict) -> str:
    return item.get("image_url", "") or ""


def _ro_field(value: str, placeholder: str) -> str:
    """Return HTML for a read-only field row."""
    if value:
        return f'<div class="ro-field">{value}</div>'
    return f'<div class="ro-field placeholder">{placeholder}</div>'


def _full_word_search(items: list[dict], query: str) -> list[dict]:
    """Return items where ALL space-separated query tokens appear as full words
    in at least one of the item's text fields."""
    if not query.strip():
        return items
    tokens = query.strip().split()
    searchable = ["brand", "candle_name", "season", "pvr", "scent_notes", "ops_notes"]
    results = []
    for item in items:
        haystack = " ".join(str(item.get(f, "") or "") for f in searchable).upper()
        if all(re.search(r'\b' + re.escape(t.upper()) + r'\b', haystack) for t in tokens):
            results.append(item)
    return results


# ─────────────────────────────────────────────────────────────────
#  PAGE: UPCOMING IN STUDIO
# ─────────────────────────────────────────────────────────────────
def page_upcoming():
    st.markdown('<div class="page-title">⏱ UPCOMING IN STUDIO</div>',
                unsafe_allow_html=True)

    items    = load_items()
    upcoming = [i for i in items if i.get("status") == "upcoming"]

    st.markdown('<div class="padded">', unsafe_allow_html=True)

    COLS = 4
    # We'll render cards + the +/- buttons in the same row grid
    total_slots = len(upcoming) + 1  # +1 for the +/- control slot
    n_rows = max(1, -(-total_slots // COLS))  # ceiling division

    slot = 0
    for row in range(n_rows):
        cols = st.columns(COLS, gap="small")
        for col_idx in range(COLS):
            if slot < len(upcoming):
                item = upcoming[slot]
                with cols[col_idx]:
                    _upcoming_card(item)
                slot += 1
            elif slot == len(upcoming):
                # +/- buttons slot
                with cols[col_idx]:
                    st.markdown("<div style='padding-top:6px'>", unsafe_allow_html=True)
                    if st.button("＋", key="add_card", type="primary",
                                 help="Add new product slot"):
                        add_item()
                        st.rerun()
                    st.markdown(
                        '<div style="margin-top:8px">',
                        unsafe_allow_html=True
                    )
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
        # ── Text fields (auto-save on change) ───────────────
        for field, ph in [
            ("brand",       "BRAND/COLLECTION"),
            ("candle_name", "CANDLE NAME"),
            ("season",      "SEASON"),
            ("pvr",         "PVR"),
        ]:
            key = f"up_{iid}_{field}"
            val = _fval(item, field)
            def _save(f=field, k=key, i=iid):
                v = st.session_state.get(k, "")
                if v and v.upper() != _fval(item, f):
                    save_field(i, f, v)
            st.text_input(ph, value=val, key=key,
                          on_change=_save,
                          placeholder=ph,
                          label_visibility="collapsed")

        # ── Image ────────────────────────────────────────────
        img_url = _img(item)
        if img_url:
            st.image(img_url, use_container_width=True)
            # Replace image button
            new_img = st.file_uploader(
                "Replace image", type=["png","jpg","jpeg","webp","gif"],
                key=f"up_img_{iid}", label_visibility="collapsed"
            )
            if new_img:
                with st.spinner("Uploading…"):
                    url = upload_image(new_img.read(), new_img.name, new_img.type)
                    save_field(iid, "image_url", url)
                st.rerun()
        else:
            new_img = st.file_uploader(
                "Click or paste image", type=["png","jpg","jpeg","webp","gif"],
                key=f"up_img_{iid}", label_visibility="collapsed"
            )
            if new_img:
                with st.spinner("Uploading…"):
                    url = upload_image(new_img.read(), new_img.name, new_img.type)
                    save_field(iid, "image_url", url)
                st.rerun()

        # ── Bottom fields ────────────────────────────────────
        for field, ph in [
            ("scent_notes", "SCENT NOTES"),
            ("ops_notes",   "OPS NOTES"),
        ]:
            key = f"up_{iid}_{field}"
            val = _fval(item, field)
            def _save2(f=field, k=key, i=iid):
                v = st.session_state.get(k, "")
                if v and v.upper() != _fval(item, f):
                    save_field(i, f, v)
            st.text_input(ph, value=val, key=key,
                          on_change=_save2,
                          placeholder=ph,
                          label_visibility="collapsed")

        # ── Action buttons ───────────────────────────────────
        st.markdown(
            '<div style="border-top:1px solid #DEDEDE;background:white;padding:6px 8px;">',
            unsafe_allow_html=True
        )
        c1, c2 = st.columns([4, 1])
        with c1:
            if st.button("→ CURRENT WEEK", key=f"up_adv_{iid}",
                         type="primary", use_container_width=True):
                # Save any pending session_state changes first
                for f in ["brand","candle_name","season","pvr","scent_notes","ops_notes"]:
                    k = f"up_{iid}_{f}"
                    if k in st.session_state:
                        save_field(iid, f, st.session_state[k])
                set_status(iid, "current_week")
                st.rerun()
        with c2:
            if st.button("🗑", key=f"up_del_{iid}",
                         type="secondary", use_container_width=True,
                         help="Delete this item"):
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

    # ── Action bar (when items selected) ─────────────────────
    if sel:
        st.markdown('<div class="padded action-bar">', unsafe_allow_html=True)
        c1, c2, _ = st.columns([2, 2, 6])
        with c1:
            if st.button(f"MOVE TO CATALOG  ({len(sel)})",
                         type="primary", use_container_width=True):
                set_status_many(list(sel), "catalog")
                st.session_state.sel_cw = set()
                st.rerun()
        with c2:
            if st.button("CLEAR SELECTION", type="secondary",
                         use_container_width=True):
                st.session_state.sel_cw = set()
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    if not cw:
        st.markdown(
            '<div style="text-align:center;color:#9A9A9F;font-size:14px;'
            'padding:80px 20px;">No items yet. Add items from the '
            '"Upcoming in Studio" tab.</div>',
            unsafe_allow_html=True
        )
        return

    st.markdown('<div class="padded">', unsafe_allow_html=True)
    cols = st.columns(4, gap="small")
    for idx, item in enumerate(cw):
        with cols[idx % 4]:
            _cw_card(item)
    st.markdown('</div>', unsafe_allow_html=True)


def _cw_card(item: dict):
    iid      = str(item["id"])
    selected = iid in st.session_state.sel_cw
    border   = "2px solid #1A73E8" if selected else "1px solid #DEDEDE"

    # Top info + image + bottom info rendered as HTML
    fields_html = "".join(
        _ro_field(_fval(item, f), ph)
        for f, ph in [
            ("brand",       "BRAND/COLLECTION"),
            ("candle_name", "CANDLE NAME"),
            ("season",      "SEASON"),
            ("pvr",         "PVR"),
        ]
    )
    img_html = (
        f'<img class="ro-card-img" src="{_img(item)}">'
        if _img(item)
        else '<div class="ro-card-noimg">No image</div>'
    )
    bottom_html = "".join(
        _ro_field(_fval(item, f), ph)
        for f, ph in [
            ("scent_notes", "SCENT NOTES"),
            ("ops_notes",   "OPS NOTES"),
        ]
    )

    st.markdown(
        f'<div class="ro-card" style="border:{border};margin-bottom:4px;">'
        f'{fields_html}{img_html}{bottom_html}</div>',
        unsafe_allow_html=True
    )

    # ── Buttons ───────────────────────────────────────────────
    c1, c2 = st.columns([1, 1])
    with c1:
        label = "✓ SELECTED" if selected else "SELECT"
        btn_t = "primary" if selected else "secondary"
        if st.button(label, key=f"cw_sel_{iid}",
                     type=btn_t, use_container_width=True):
            if selected:
                st.session_state.sel_cw.discard(iid)
            else:
                st.session_state.sel_cw.add(iid)
            st.rerun()
    with c2:
        if st.button("← UPCOMING", key=f"cw_back_{iid}",
                     type="secondary", use_container_width=True):
            st.session_state.sel_cw.discard(iid)
            set_status(iid, "upcoming")
            st.rerun()


# ─────────────────────────────────────────────────────────────────
#  PAGE: HOME FRAGRANCE CATALOG
# ─────────────────────────────────────────────────────────────────
def page_catalog():
    items   = load_items()
    catalog = [i for i in items if i.get("status") == "catalog"]
    # Most recent first
    catalog.sort(key=lambda x: x.get("updated_at", ""), reverse=True)

    st.markdown('<div class="page-title">≡ HOME FRAGRANCE CATALOG</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="padded">', unsafe_allow_html=True)

    # ── Search bar ────────────────────────────────────────────
    query = st.text_input(
        "Search",
        placeholder="🔍  Search library…",
        key="cat_search",
        label_visibility="collapsed"
    )

    filtered = _full_word_search(catalog, query)

    if not filtered:
        if query:
            st.markdown(
                f'<div style="color:#9A9A9F;font-size:14px;padding:40px 0;">'
                f'No results for "{query}".</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown("""
            <div style="background:white;border:1px solid #DEDEDE;border-radius:8px;
                        padding:70px;text-align:center;">
                <div style="font-size:36px;color:#C7C7CC;margin-bottom:12px;">≡</div>
                <div style="font-size:15px;color:#9A9A9F;">No archived items yet</div>
                <div style="font-size:13px;color:#C7C7CC;margin-top:4px;">
                    Items moved from Current Week will appear here</div>
            </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        return

    cols = st.columns(4, gap="small")
    for idx, item in enumerate(filtered):
        with cols[idx % 4]:
            _catalog_card(item)

    st.markdown('</div>', unsafe_allow_html=True)


def _catalog_card(item: dict):
    iid = str(item["id"])

    # Info text (no bottom text in catalog)
    info_lines = [
        _fval(item, f) or ph
        for f, ph in [
            ("brand",       "BRAND/COLLECTION"),
            ("candle_name", "CANDLE NAME"),
            ("season",      "SEASON"),
            ("pvr",         "PVR"),
        ]
    ]
    info_html = "<br>".join(
        f'<span style="color:{"#1A1A1A" if _fval(item,f) else "#C7C7CC"}">{v}</span>'
        for v, (f, _) in zip(info_lines, [
            ("brand",""), ("candle_name",""), ("season",""), ("pvr","")
        ])
    )

    img_html = (
        f'<img class="cat-card-img" src="{_img(item)}">'
        if _img(item)
        else '<div class="cat-card-noimg">No image</div>'
    )

    st.markdown(
        f'<div class="cat-card">'
        f'<div class="cat-card-info">{info_html}</div>'
        f'{img_html}</div>',
        unsafe_allow_html=True
    )

    # ── Image upload (replace) ────────────────────────────────
    new_img = st.file_uploader(
        "Replace image",
        type=["png","jpg","jpeg","webp","gif"],
        key=f"cat_img_{iid}",
        label_visibility="collapsed"
    )
    if new_img:
        with st.spinner("Uploading…"):
            url = upload_image(new_img.read(), new_img.name, new_img.type)
            save_field(iid, "image_url", url)
        st.rerun()

    # ── Action buttons ────────────────────────────────────────
    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("♻ RESHOOT", key=f"cat_re_{iid}",
                     type="primary", use_container_width=True):
            new_id = copy_to_reshoot(item)
            send_slack(
                f"🔁 *Reshoot requested*\n"
                f"*{_fval(item,'candle_name') or 'Unnamed'}*"
                f" — {_fval(item,'brand') or ''}"
                f" ({_fval(item,'season') or ''})"
            )
            st.success("Copied to Reshoot Requests!")
            st.rerun()
    with c2:
        if st.button("🗑 DELETE", key=f"cat_del_{iid}",
                     type="secondary", use_container_width=True):
            delete_item(iid)
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

    # ── Action bar (when items selected) ─────────────────────
    if sel:
        st.markdown('<div class="padded action-bar">', unsafe_allow_html=True)
        c1, c2, c3, _ = st.columns([2, 2, 2, 4])
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
        with c3:
            if st.button("CLEAR SELECTION", type="secondary",
                         use_container_width=True):
                st.session_state.sel_reshoot = set()
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    if not reshoot:
        st.markdown("""
        <div style="background:white;border:1px solid #DEDEDE;border-radius:8px;
                    margin:0 24px;padding:70px;text-align:center;">
            <div style="font-size:36px;color:#C7C7CC;margin-bottom:12px;">↺</div>
            <div style="font-size:15px;color:#9A9A9F;">No items marked for reshoots</div>
            <div style="font-size:13px;color:#C7C7CC;margin-top:4px;">
                Items recycled from the catalog will appear here</div>
        </div>""", unsafe_allow_html=True)
        return

    st.markdown('<div class="padded">', unsafe_allow_html=True)
    cols = st.columns(4, gap="small")
    for idx, item in enumerate(reshoot):
        with cols[idx % 4]:
            _reshoot_card(item)
    st.markdown('</div>', unsafe_allow_html=True)


def _reshoot_card(item: dict):
    iid      = str(item["id"])
    selected = iid in st.session_state.sel_reshoot
    border   = "2px solid #1A73E8" if selected else "1px solid #DEDEDE"

    # Top fields (read-only)
    fields_html = "".join(
        _ro_field(_fval(item, f), ph)
        for f, ph in [
            ("brand",       "BRAND/COLLECTION"),
            ("candle_name", "CANDLE NAME"),
            ("season",      "SEASON"),
            ("pvr",         "PVR"),
        ]
    )
    # Image (not editable)
    img_html = (
        f'<img class="ro-card-img" src="{_img(item)}">'
        if _img(item)
        else '<div class="ro-card-noimg">No image</div>'
    )
    # Scent notes (read-only)
    scent_html = _ro_field(_fval(item, "scent_notes"), "SCENT NOTES")

    st.markdown(
        f'<div class="ro-card" style="border:{border};margin-bottom:4px;">'
        f'{fields_html}{img_html}{scent_html}</div>',
        unsafe_allow_html=True
    )

    # ── Ops Notes (EDITABLE) ──────────────────────────────────
    key_ops = f"re_ops_{iid}"
    def _save_ops(k=key_ops, i=iid):
        v = st.session_state.get(k, "")
        save_field(i, "ops_notes", v)

    with st.container(border=True):
        st.text_input(
            "OPS NOTES",
            value=_fval(item, "ops_notes"),
            key=key_ops,
            on_change=_save_ops,
            placeholder="OPS NOTES",
            label_visibility="collapsed"
        )

    # ── Select button ─────────────────────────────────────────
    label = "✓ SELECTED" if selected else "SELECT"
    btn_t = "primary" if selected else "secondary"
    if st.button(label, key=f"re_sel_{iid}",
                 type=btn_t, use_container_width=True):
        if selected:
            st.session_state.sel_reshoot.discard(iid)
        else:
            st.session_state.sel_reshoot.add(iid)
        st.rerun()


# ─────────────────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────────────────
def main():
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
