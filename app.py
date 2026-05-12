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
import uuid, re, requests, base64, io

# Optional Pillow — used for resize/compress so uploads fit Sheets cell limit.
try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


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
#  SVG ICONS (used in hover buttons + placeholder rectangle)
# ─────────────────────────────────────────────────────────────────
SVG_ARROW = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="white" '
    'stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M19 12H5"/><path d="m12 19-7-7 7-7"/></svg>'
)
SVG_RECYCLE = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="white" '
    'stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/>'
    '<path d="M21 3v5h-5"/>'
    '<path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/>'
    '<path d="M8 16H3v5"/></svg>'
)
SVG_TRASH = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="white" '
    'stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M3 6h18"/>'
    '<path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6"/>'
    '<path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>'
)
SVG_IMAGE = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" '
    'width="36" height="36">'
    '<rect width="18" height="18" x="3" y="3" rx="2" ry="2"/>'
    '<circle cx="9" cy="9" r="2"/>'
    '<path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/></svg>'
)

# ─────────────────────────────────────────────────────────────────
#  STYLES
# ─────────────────────────────────────────────────────────────────
BLUE       = "#2563EB"
BLUE_HOVER = "#1D4ED8"
RED        = "#EF4444"
RED_HOVER  = "#DC2626"
BORDER     = "#DEDEDE"
PAGE_BG    = "#F4F4F6"
SIDE_PAD   = "48px"
ROW_GAP    = "48px"  # vertical gap between rows of cards (matches SIDE_PAD)

st.markdown(f"""
<style>
/* ── Hide Streamlit chrome ───────────────────────────────── */
#MainMenu, footer, header {{ visibility: hidden; }}
.stDeployButton {{ display: none; }}

/* ── Full window width ───────────────────────────────────── */
.stApp {{ background: {PAGE_BG}; }}
.block-container {{
    padding: 0 !important;
    max-width: 100% !important;
}}
section[data-testid="stMainBlockContainer"] {{
    padding: 0 !important;
    max-width: 100% !important;
}}

/* ── Tab bar ─────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {{
    background: white;
    border-bottom: 1px solid {BORDER};
    padding: 8px {SIDE_PAD} 0;
    gap: 4px;
}}
.stTabs [data-baseweb="tab"] {{
    border-radius: 20px;
    padding: 8px 18px;
    font-size: 13px;
    font-weight: 500;
    color: #1A1A1A;
    background: transparent;
    border: none;
}}
.stTabs [aria-selected="true"] {{
    background: #111111 !important;
    color: #FFFFFF !important;
    border-radius: 20px;
}}
.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] {{ display: none; }}
div[data-testid="stTabs"] > div:first-child {{ margin-bottom: 0 !important; }}

/* ── Page title (buffer from tab bar) ───────────────────── */
.page-title {{
    font-size: 26px;
    font-weight: 900;
    color: #1A1A1A;
    letter-spacing: -0.5px;
    padding: 32px {SIDE_PAD} 24px;
}}

/* ── Content wrapper (side & bottom padding) ────────────── */
.padded {{ padding: 0 {SIDE_PAD} 32px; }}

/* ── Input typography (caps, centered) ──────────────────── */
input[type="text"], textarea {{
    text-transform: uppercase !important;
    text-align: center !important;
    font-size: 11px !important;
    letter-spacing: 0.3px !important;
}}
/* Allow URL paste field to be left-aligned, mixed-case */
.url-paste-wrap input[type="text"] {{
    text-transform: none !important;
    text-align: left !important;
}}

/* ── Hide widget labels ─────────────────────────────────── */
div.stTextInput  > label {{ display: none !important; }}
div.stTextArea   > label {{ display: none !important; }}

/* ── Text inputs: separately-bordered rounded rows ──────── */
div.stTextInput > div {{
    border: 1px solid {BORDER} !important;
    border-radius: 4px !important;
    background: white;
    box-shadow: none !important;
    margin-bottom: 4px;
}}
div.stTextInput > div > div {{ border: none !important; }}
div.stTextInput > div > div > input {{
    border: none !important;
    border-radius: 4px !important;
    padding: 9px 8px !important;
    background: white !important;
    box-shadow: none !important;
}}
div.stTextInput > div:focus-within {{
    border-color: #888 !important;
}}

/* ── Read-only field row (bordered rectangle) ───────────── */
.ro-field {{
    display: block;
    background: white;
    border: 1px solid {BORDER};
    border-radius: 4px;
    padding: 9px 8px;
    font-size: 11px;
    text-align: center;
    text-transform: uppercase;
    color: #1A1A1A;
    letter-spacing: 0.3px;
    margin-bottom: 4px;
    min-height: 32px;
    text-decoration: none;
}}
.ro-field.placeholder {{ color: #C7C7CC; }}
a.ro-field {{ color: #1A1A1A; }}
a.ro-field.placeholder {{ color: #C7C7CC; }}
a.ro-field:hover {{ background: #FAFAFA; }}

/* ── Container reset for upcoming card ──────────────────── */
div[data-testid="stVerticalBlockBorderWrapper"] {{
    background: transparent !important;
    border: none !important;
    border-radius: 0 !important;
    padding: 0 !important;
}}
div[data-testid="stVerticalBlockBorderWrapper"] > div {{
    padding: 0 !important;
    gap: 0 !important;
}}
div[data-testid="stVerticalBlock"] {{ gap: 0 !important; }}

/* ── Card container (current week / catalog / reshoot) ──── */
.ap-card {{
    position: relative;
    background: transparent;
    border: 2px solid transparent;
    border-radius: 6px;
    padding: 2px;
    margin-bottom: {ROW_GAP};
    cursor: pointer;
    transition: border-color 0.15s;
    user-select: none;
}}
.ap-card:hover {{ border-color: #ABABAB; }}
.ap-card.selected {{
    border: 3px solid {BLUE} !important;
    padding: 1px;
}}
.ap-card.selected:hover {{ border-color: {BLUE}; }}

/* ── Image rectangle (3:4 aspect) ───────────────────────── */
.img-rect {{
    position: relative;
    aspect-ratio: 3 / 4;
    background: white;
    border: 1px solid {BORDER};
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 4px;
}}
.img-rect img {{
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
}}
.img-rect .empty {{
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: #C7C7CC;
    gap: 8px;
    font-size: 13px;
    text-transform: none;
}}
.img-rect .empty svg {{ width: 36px; height: 36px; }}

/* Click-link overlay (covers the image for card selection) */
.img-click-link {{
    position: absolute;
    inset: 0;
    z-index: 1;
    text-decoration: none;
}}

/* Hover overlay (holds the round icon buttons) */
.img-rect .hover-overlay {{
    position: absolute;
    inset: 0;
    opacity: 0;
    transition: opacity 0.2s;
    pointer-events: none;
    z-index: 2;
}}
.img-rect:hover .hover-overlay {{ opacity: 1; }}
/* Buttons inside the overlay capture their own clicks */
.img-rect .hover-overlay .hover-btn {{
    pointer-events: auto;
    z-index: 3;
}}

/* ── Hover icon buttons (colored circles) ───────────────── */
.hover-btn {{
    position: absolute;
    cursor: pointer;
    border: none;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    text-decoration: none;
    color: white;
    box-shadow: 0 2px 6px rgba(0,0,0,0.18);
    transition: transform 0.1s, background 0.15s;
}}
.hover-btn svg {{ width: 20px; height: 20px; }}
.hover-btn:hover {{ transform: scale(1.06); }}
.hover-btn-blue {{ background: {BLUE}; }}
.hover-btn-blue:hover {{ background: {BLUE_HOVER}; }}
.hover-btn-red {{ background: {RED}; }}
.hover-btn-red:hover {{ background: {RED_HOVER}; }}
.hover-btn-tl  {{ top: 8px; left: 8px; }}
.hover-btn-tr  {{ top: 8px; right: 8px; }}
.hover-btn-tr2 {{ top: 8px; right: 56px; }}

/* ── Catalog: dense text-info section above image ───────── */
.cat-card-info {{
    background: white;
    border: 1px solid {BORDER};
    border-radius: 4px;
    padding: 8px;
    text-align: center;
    font-size: 11px;
    text-transform: uppercase;
    color: #1A1A1A;
    line-height: 1.9;
    margin-bottom: 4px;
}}

/* ── URL paste field (mixed-case, small) ────────────────── */
.url-paste-wrap div.stTextInput > div > div > input {{
    font-size: 10px !important;
    text-transform: none !important;
    text-align: left !important;
    color: #6A6A6F !important;
}}

/* ── File uploader styled as 3:4 placeholder rectangle ──── */
div[data-testid="stFileUploader"] {{
    margin-bottom: 4px;
}}
div[data-testid="stFileUploader"] section[data-testid="stFileUploaderDropzone"] {{
    aspect-ratio: 3 / 4;
    background: white;
    border: 1px dashed {BORDER};
    border-radius: 4px;
    cursor: pointer;
    padding: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: border-color 0.15s, background 0.15s;
}}
div[data-testid="stFileUploader"] section[data-testid="stFileUploaderDropzone"]:hover {{
    border-color: #888;
    background: #FAFAFA;
}}
div[data-testid="stFileUploader"] [data-testid="stFileUploaderDropzoneInstructions"] {{
    color: #C7C7CC !important;
    text-align: center;
    padding: 0 !important;
}}
div[data-testid="stFileUploader"] [data-testid="stFileUploaderDropzoneInstructions"] > div {{
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    gap: 8px !important;
}}
div[data-testid="stFileUploader"] [data-testid="stFileUploaderDropzoneInstructions"] svg {{
    width: 36px !important;
    height: 36px !important;
    color: #C7C7CC !important;
    fill: none !important;
    stroke: #C7C7CC !important;
}}
/* Replace default "Drag and drop" text with our copy */
div[data-testid="stFileUploader"] [data-testid="stFileUploaderDropzoneInstructions"] span {{
    font-size: 0 !important;
    color: transparent !important;
}}
div[data-testid="stFileUploader"] [data-testid="stFileUploaderDropzoneInstructions"] span::after {{
    content: "Click or paste image";
    font-size: 13px;
    color: #C7C7CC;
    display: block;
}}
div[data-testid="stFileUploader"] [data-testid="stFileUploaderDropzoneInstructions"] small {{
    display: none !important;
}}
div[data-testid="stFileUploader"] section[data-testid="stFileUploaderDropzone"] button {{
    display: none !important;
}}

/* ── Delete-confirm strip (catalog) ─────────────────────── */
.del-confirm-bar {{
    background: #FFF5F5;
    border: 1px solid #FECACA;
    border-radius: 4px;
    padding: 7px 8px;
    text-align: center;
    font-size: 11px;
    font-weight: 600;
    color: #E63946;
    text-transform: uppercase;
    letter-spacing: 0.3px;
    margin-bottom: 4px;
}}

/* ── Streamlit buttons (default styling) ────────────────── */
div.stButton > button {{
    border-radius: 4px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.4px;
    border: none !important;
    padding: 6px 12px !important;
}}
div.stButton > button[kind="primary"] {{
    background: #111111 !important;
    color: white !important;
}}
div.stButton > button[kind="secondary"] {{
    background: #E8E8E8 !important;
    color: #111111 !important;
}}

/* ── +/- circular control buttons (Upcoming tab sidebar) ─ */
.ap-controls {{
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
    padding-top: 4px;
}}
.ap-control-btn {{
    width: 44px;
    height: 44px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 26px;
    font-weight: 400;
    text-decoration: none;
    box-shadow: 0 2px 6px rgba(0,0,0,0.18);
    line-height: 1;
    transition: transform 0.1s;
}}
.ap-control-btn:hover {{ transform: scale(1.06); }}
.ap-control-add {{ background: #111111; }}
.ap-control-rem {{ background: {RED}; }}

/* ── Action bar (multi-select MOVE / DECLINE) ───────────── */
.action-bar {{
    background: transparent;
    padding: 12px {SIDE_PAD};
    display: flex;
    gap: 12px;
    align-items: center;
}}

/* ── Misc: column gap, image margins ────────────────────── */
div[data-testid="stHorizontalBlock"] {{
    gap: 16px !important;
    margin-bottom: {ROW_GAP};
}}
div[data-testid="stImage"] {{ margin: 0 !important; }}
div[data-testid="stImage"] img {{ border-radius: 4px; }}

/* ── Force white text + no underline on all anchor controls ── */
/* (Streamlit forces target="_blank" on <a> in user markdown, and
   its default link styling can override our color/decoration.) */
a.ro-field,
a.hover-btn,
a.ap-control-btn,
a.img-click-link,
.ap-card a,
.ap-controls a {{
    text-decoration: none !important;
    text-underline-offset: 0 !important;
}}
a.ap-control-btn,
a.ap-control-btn:link,
a.ap-control-btn:visited,
a.ap-control-btn:hover,
a.ap-control-btn:active {{
    color: white !important;
}}
a.hover-btn,
a.hover-btn:link,
a.hover-btn:visited,
a.hover-btn:hover,
a.hover-btn:active {{
    color: white !important;
}}
a.ro-field {{ color: #1A1A1A !important; }}
a.ro-field.placeholder {{ color: #C7C7CC !important; }}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
#  GOOGLE SERVICES
# ─────────────────────────────────────────────────────────────────
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
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
    gc = gspread.authorize(creds)
    return gc


def _sheet():
    gc = _get_services()
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
    # Don't force-uppercase URLs / data URLs
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
    s_col  = SHEET_HEADERS.index("status") + 1
    u_col  = SHEET_HEADERS.index("updated_at") + 1
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
    items    = load_items()
    upcoming = [i for i in items if i.get("status") == "upcoming"]
    for item in reversed(upcoming):
        fields = ["brand","candle_name","season","pvr","scent_notes","ops_notes","image_url"]
        if not any(item.get(f,"").strip() for f in fields):
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
#  IMAGE UPLOAD PROCESSING
# ─────────────────────────────────────────────────────────────────
# Google Sheets caps a single cell at ~50,000 chars. Base64 inflates
# bytes by ~33%, so we resize to a thumbnail before encoding. When DAM
# access lands, swap _process_upload to push the file to DAM and return
# the canonical DAM URL instead.
MAX_CELL_CHARS = 45000

def _process_upload(uploaded_file) -> str | None:
    """Read an UploadedFile, resize if Pillow is available, return a
    data: URL (or None if the result would exceed the cell limit)."""
    bytes_data = uploaded_file.read()
    mime = uploaded_file.type or "image/jpeg"

    if HAS_PIL:
        try:
            img = Image.open(io.BytesIO(bytes_data))
            # Flatten transparency onto white so we can save as JPEG.
            if img.mode in ("RGBA", "LA", "P"):
                rgba = img.convert("RGBA")
                bg = Image.new("RGB", rgba.size, (255, 255, 255))
                bg.paste(rgba, mask=rgba.split()[-1])
                img = bg
            elif img.mode != "RGB":
                img = img.convert("RGB")
            img.thumbnail((600, 800), Image.LANCZOS)
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=78, optimize=True)
            bytes_data = buf.getvalue()
            mime = "image/jpeg"
        except Exception:
            pass  # fall back to raw bytes

    b64 = base64.b64encode(bytes_data).decode("ascii")
    data_url = f"data:{mime};base64,{b64}"
    if len(data_url) > MAX_CELL_CHARS:
        return None
    return data_url


# ─────────────────────────────────────────────────────────────────
#  SESSION STATE + ACTION HANDLER
# ─────────────────────────────────────────────────────────────────
def _init():
    defaults = {
        "sel_cw":             set(),
        "sel_reshoot":        set(),
        "confirm_delete_id":  None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def _handle_actions():
    """Process anchor-href driven query-param actions before rendering."""
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
                f" ({_fval(item,'season') or ''})"
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

    elif action == "add_card":
        add_item()
        st.rerun()

    elif action == "rem_card":
        remove_last_empty()
        st.rerun()


# ─────────────────────────────────────────────────────────────────
#  RENDER HELPERS
# ─────────────────────────────────────────────────────────────────
def _fval(item: dict, field: str) -> str:
    return str(item.get(field, "") or "").upper().strip()


def _img(item: dict) -> str:
    return item.get("image_url", "") or ""


def _ro_field(value: str, placeholder: str, href: str = "") -> str:
    has_val = bool(value)
    cls     = "ro-field" if has_val else "ro-field placeholder"
    text    = value if has_val else placeholder
    if href:
        return f'<a class="{cls}" href="{href}" target="_self">{text}</a>'
    return f'<div class="{cls}">{text}</div>'


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


def _img_wrap_html(img_url: str, overlay_html: str = "",
                   click_href: str = "") -> str:
    """3:4 image rectangle with optional click-through link + hover overlay."""
    if img_url:
        inner = f'<img src="{img_url}">'
    else:
        inner = f'<div class="empty">{SVG_IMAGE}<span>No image</span></div>'
    click_link = (
        f'<a class="img-click-link" href="{click_href}" target="_self"></a>'
        if click_href else ''
    )
    overlay = (
        f'<div class="hover-overlay">{overlay_html}</div>' if overlay_html else ''
    )
    return (
        f'<div class="img-rect">'
        f'{inner}'
        f'{click_link}'
        f'{overlay}'
        f'</div>'
    )


def _handle_upload(uploaded, iid: str):
    """Dedupe-aware: only save once per uploaded file."""
    if uploaded is None:
        return
    file_id  = getattr(uploaded, "file_id", None) or f"{uploaded.name}_{uploaded.size}"
    last_key = f"_last_upload_{iid}"
    if st.session_state.get(last_key) == file_id:
        return
    data_url = _process_upload(uploaded)
    if data_url is None:
        st.error("Image too large after compression — try a smaller file or paste a URL instead.")
        st.session_state[last_key] = file_id  # don't retry every rerun
        return
    save_field(iid, "image_url", data_url)
    st.session_state[last_key] = file_id
    st.rerun()


# ─────────────────────────────────────────────────────────────────
#  PAGE: UPCOMING IN STUDIO
# ─────────────────────────────────────────────────────────────────
def page_upcoming():
    st.markdown('<div class="page-title">⏱ UPCOMING IN STUDIO</div>',
                unsafe_allow_html=True)

    items    = load_items()
    upcoming = [i for i in items if i.get("status") == "upcoming"]

    st.markdown('<div class="padded">', unsafe_allow_html=True)

    COLS = 6

    # ─── First row: 6 card columns + 1 narrow column for +/- controls ────
    first_row_count = min(len(upcoming), COLS)
    cols = st.columns([1, 1, 1, 1, 1, 1, 0.35], gap="small")
    for i in range(first_row_count):
        with cols[i]:
            _upcoming_card(upcoming[i])
    # Empty card cells beyond the first_row_count remain blank
    with cols[COLS]:
        st.markdown(
            f'<div class="ap-controls">'
            f'<a class="ap-control-btn ap-control-add" target="_self" '
            f'href="?ap_action=add_card&ap_id=_" title="Add new product slot">+</a>'
            f'<a class="ap-control-btn ap-control-rem" target="_self" '
            f'href="?ap_action=rem_card&ap_id=_" title="Remove last empty slot">−</a>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # ─── Subsequent rows: 6 columns of cards only ────────────────────────
    slot = first_row_count
    while slot < len(upcoming):
        cols_row = st.columns(COLS, gap="small")
        for col_idx in range(COLS):
            if slot < len(upcoming):
                with cols_row[col_idx]:
                    _upcoming_card(upcoming[slot])
                slot += 1

    st.markdown('</div>', unsafe_allow_html=True)


def _upcoming_card(item: dict):
    iid = str(item["id"])

    with st.container():
        # ── Top text fields (editable, save on change) ───────
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
            st.text_input(ph, value=val, key=key,
                          on_change=_save, placeholder=ph,
                          label_visibility="collapsed")

        # ── Image area (3:4) ─────────────────────────────────
        img_url = _img(item)
        if img_url:
            # Display existing image inside the 3:4 rect
            st.markdown(
                f'<div class="img-rect"><img src="{img_url}"></div>',
                unsafe_allow_html=True,
            )
        else:
            # File uploader is styled globally as the 3:4 placeholder
            uploaded = st.file_uploader(
                "Click or paste image",
                type=["png", "jpg", "jpeg", "webp"],
                key=f"upload_{iid}",
                label_visibility="collapsed",
            )
            _handle_upload(uploaded, iid)

        # ── URL paste field (always present) ─────────────────
        key_url     = f"up_url_{iid}"
        display_url = "" if img_url.startswith("data:") else img_url
        placeholder = "PASTE NEW URL TO REPLACE" if img_url else "OR PASTE IMAGE URL"
        st.markdown('<div class="url-paste-wrap">', unsafe_allow_html=True)
        new_url = st.text_input(
            "Image URL", value=display_url,
            placeholder=placeholder,
            key=key_url, label_visibility="collapsed",
        )
        st.markdown('</div>', unsafe_allow_html=True)
        if new_url.strip() and new_url.strip() != img_url:
            save_field(iid, "image_url", new_url.strip())
            st.rerun()

        # ── Bottom text fields ───────────────────────────────
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
            st.text_input(ph, value=val, key=key,
                          on_change=_save2, placeholder=ph,
                          label_visibility="collapsed")

        # ── Action row (→ CURRENT WEEK | delete) ─────────────
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
            if st.button("🗑", key=f"up_del_{iid}",
                         type="secondary", use_container_width=True,
                         help="Delete this item"):
                delete_item(iid)
                st.rerun()


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
            '<div class="padded" style="text-align:center;color:#9A9A9F;'
            'font-size:14px;padding-top:80px;padding-bottom:80px;">'
            'No items yet. Add items from the "Upcoming in Studio" tab.</div>',
            unsafe_allow_html=True
        )
        return

    st.markdown('<div class="padded">', unsafe_allow_html=True)
    COLS = 6
    cols = st.columns(COLS, gap="small")
    for idx, item in enumerate(cw):
        with cols[idx % COLS]:
            _cw_card(item)
    st.markdown('</div>', unsafe_allow_html=True)


def _cw_card(item: dict):
    iid      = str(item["id"])
    selected = iid in st.session_state.sel_cw
    sel_cls  = "selected" if selected else ""
    sel_href = f"?ap_action=cw_sel&ap_id={iid}"

    # All text rows are click-through anchors → toggle selection.
    fields_html = "".join(
        _ro_field(_fval(item, f), ph, href=sel_href)
        for f, ph in [
            ("brand",       "BRAND/COLLECTION"),
            ("candle_name", "CANDLE NAME"),
            ("season",      "SEASON"),
            ("pvr",         "PVR"),
        ]
    )

    # Top-left blue back-arrow → returns card to Upcoming.
    arrow_overlay = (
        f'<a class="hover-btn hover-btn-blue hover-btn-tl" target="_self" '
        f'href="?ap_action=cw_back&ap_id={iid}" title="Return to Upcoming">'
        f'{SVG_ARROW}</a>'
    )
    img_html = _img_wrap_html(_img(item), arrow_overlay, click_href=sel_href)

    bottom_html = "".join(
        _ro_field(_fval(item, f), ph, href=sel_href)
        for f, ph in [
            ("scent_notes", "SCENT NOTES"),
            ("ops_notes",   "OPS NOTES"),
        ]
    )

    st.markdown(
        f'<div class="ap-card {sel_cls}">'
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
    catalog.sort(key=lambda x: x.get("updated_at", ""), reverse=True)

    st.markdown('<div class="page-title">≡ HOME FRAGRANCE CATALOG</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="padded">', unsafe_allow_html=True)

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

    COLS = 6
    cols = st.columns(COLS, gap="small")
    for idx, item in enumerate(filtered):
        with cols[idx % COLS]:
            _catalog_card(item)

    st.markdown('</div>', unsafe_allow_html=True)


def _catalog_card(item: dict):
    iid     = str(item["id"])
    confirm = st.session_state.get("confirm_delete_id") == iid

    info_lines = [
        (_fval(item, f) or ph, bool(_fval(item, f)))
        for f, ph in [
            ("brand",       "BRAND/COLLECTION"),
            ("candle_name", "CANDLE NAME"),
            ("season",      "SEASON"),
            ("pvr",         "PVR"),
        ]
    ]
    info_html = "<br>".join(
        f'<span style="color:{"#1A1A1A" if has_val else "#C7C7CC"}">{text}</span>'
        for text, has_val in info_lines
    )

    # Top-right hover buttons: blue recycle (reshoot) + red trash (delete).
    cat_overlay = (
        f'<a class="hover-btn hover-btn-blue hover-btn-tr2" target="_self" '
        f'href="?ap_action=cat_reshoot&ap_id={iid}" title="Request Reshoot">'
        f'{SVG_RECYCLE}</a>'
        f'<a class="hover-btn hover-btn-red hover-btn-tr" target="_self" '
        f'href="?ap_action=cat_delete_ask&ap_id={iid}" title="Delete">'
        f'{SVG_TRASH}</a>'
    )
    img_html = _img_wrap_html(_img(item), cat_overlay)

    st.markdown(
        f'<div class="ap-card">'
        f'<div class="cat-card-info">{info_html}</div>'
        f'{img_html}'
        f'</div>',
        unsafe_allow_html=True
    )

    # URL paste field
    img_url    = _img(item)
    key_url    = f"cat_url_{iid}"
    display_url = "" if img_url.startswith("data:") else img_url
    st.markdown('<div class="url-paste-wrap">', unsafe_allow_html=True)
    new_url = st.text_input(
        "Image URL", value=display_url,
        placeholder="PASTE IMAGE URL FROM DAM",
        key=key_url, label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    if new_url.strip() and new_url.strip() != img_url:
        save_field(iid, "image_url", new_url.strip())
        st.rerun()

    # Delete confirmation
    if confirm:
        st.markdown(
            '<div class="del-confirm-bar">Are you sure you want to delete this?</div>',
            unsafe_allow_html=True
        )
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
                    margin:0 32px;padding:70px;text-align:center;">
            <div style="font-size:36px;color:#C7C7CC;margin-bottom:12px;">↺</div>
            <div style="font-size:15px;color:#9A9A9F;">No items marked for reshoots</div>
            <div style="font-size:13px;color:#C7C7CC;margin-top:4px;">
                Items recycled from the catalog will appear here</div>
        </div>""", unsafe_allow_html=True)
        return

    st.markdown('<div class="padded">', unsafe_allow_html=True)
    COLS = 6
    cols = st.columns(COLS, gap="small")
    for idx, item in enumerate(reshoot):
        with cols[idx % COLS]:
            _reshoot_card(item)
    st.markdown('</div>', unsafe_allow_html=True)


def _reshoot_card(item: dict):
    iid      = str(item["id"])
    selected = iid in st.session_state.sel_reshoot
    sel_cls  = "selected" if selected else ""
    sel_href = f"?ap_action=re_sel&ap_id={iid}"

    fields_html = "".join(
        _ro_field(_fval(item, f), ph, href=sel_href)
        for f, ph in [
            ("brand",       "BRAND/COLLECTION"),
            ("candle_name", "CANDLE NAME"),
            ("season",      "SEASON"),
            ("pvr",         "PVR"),
        ]
    )
    img_html   = _img_wrap_html(_img(item), "", click_href=sel_href)
    scent_html = _ro_field(_fval(item, "scent_notes"), "SCENT NOTES", href=sel_href)

    st.markdown(
        f'<div class="ap-card {sel_cls}">'
        f'{fields_html}{img_html}{scent_html}'
        f'</div>',
        unsafe_allow_html=True
    )

    # Editable ops_notes lives outside the clickable card.
    key_ops = f"re_ops_{iid}"
    def _save_ops(k=key_ops, i=iid):
        v = st.session_state.get(k, "")
        save_field(i, "ops_notes", v)
    st.text_input(
        "OPS NOTES",
        value=_fval(item, "ops_notes"),
        key=key_ops,
        on_change=_save_ops,
        placeholder="OPS NOTES",
        label_visibility="collapsed"
    )


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
