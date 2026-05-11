"""
Home Fragrance AutoPack — Streamlit Web App
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Data is stored in Google Sheets. Images are stored in Google Drive.
See README_SETUP.txt for full setup instructions.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from datetime import datetime
import uuid
import io

# ─────────────────────────────────────────────────────────────────
#  PAGE CONFIG  (must be the very first Streamlit call)
# ─────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Home Fragrance AutoPack",
    page_icon="🕯️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────
#  GLOBAL STYLES
# ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Hide Streamlit chrome ───────────────────────────────────── */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* ── Page background ─────────────────────────────────────────── */
.stApp { background-color: #F4F4F6; }
.block-container {
    padding-top: 1rem;
    padding-bottom: 2rem;
    max-width: 1300px;
}

/* ── Tab bar  ────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background-color: #FFFFFF;
    border-bottom: 1px solid #DEDEDE;
    padding: 0 8px;
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
    background-color: #111111 !important;
    color: #FFFFFF !important;
    border-radius: 20px;
}
.stTabs [data-baseweb="tab-highlight"] { display: none; }
.stTabs [data-baseweb="tab-border"]    { display: none; }

/* ── Page title ──────────────────────────────────────────────── */
.page-title {
    font-size: 26px;
    font-weight: 900;
    color: #1A1A1A;
    letter-spacing: -0.5px;
    margin-bottom: 16px;
    margin-top: 8px;
}

/* ── Item card ───────────────────────────────────────────────── */
.item-card {
    background: #FFFFFF;
    border: 1px solid #DEDEDE;
    border-radius: 6px;
    overflow: hidden;
    margin-bottom: 4px;
}
.card-thumb-placeholder {
    height: 155px;
    background: #EBEBEB;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #C7C7CC;
    font-size: 13px;
}
.card-thumb img {
    width: 100%;
    height: 155px;
    object-fit: cover;
}
.card-body { padding: 10px 12px 6px; }
.card-brand {
    font-size: 10px;
    font-weight: 600;
    color: #9A9A9F;
    text-transform: uppercase;
    letter-spacing: 0.6px;
}
.card-name {
    font-size: 14px;
    font-weight: 700;
    color: #1A1A1A;
    margin: 3px 0 4px;
    line-height: 1.3;
}
.card-meta  { font-size: 11px; color: #9A9A9F; margin-bottom: 2px; }
.card-notes { font-size: 11px; color: #9A9A9F; margin-top: 4px; }

/* ── Upcoming field card ─────────────────────────────────────── */
.upcoming-card {
    background: #FFFFFF;
    border: 1px solid #DEDEDE;
    border-radius: 6px;
    overflow: hidden;
    margin-bottom: 4px;
}
.upcoming-field {
    padding: 7px 10px;
    border-bottom: 1px solid #DEDEDE;
    font-size: 11px;
    color: #9A9A9F;
    text-align: center;
    background: #FFFFFF;
}
.upcoming-field.has-value { color: #1A1A1A; }
.upcoming-field.image-area {
    height: 150px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    gap: 6px;
    color: #C7C7CC;
    font-size: 12px;
}
.upcoming-field img {
    width: 100%;
    height: 150px;
    object-fit: cover;
}

/* ── Empty state ─────────────────────────────────────────────── */
.empty-card {
    background: #FFFFFF;
    border: 1px solid #DEDEDE;
    border-radius: 8px;
    padding: 70px 40px;
    text-align: center;
}
.empty-icon  { font-size: 42px; color: #C7C7CC; margin-bottom: 12px; }
.empty-title { font-size: 15px; color: #9A9A9F; font-weight: 500; margin-bottom: 4px; }
.empty-sub   { font-size: 13px; color: #C7C7CC; }

/* Current Week empty (no card — just centered text on gray bg) */
.empty-plain { text-align: center; color: #9A9A9F; font-size: 14px; padding: 80px 20px; }

/* ── Primary button override ─────────────────────────────────── */
div.stButton > button[kind="primary"] {
    background-color: #111111;
    color: #FFFFFF;
    border: none;
    border-radius: 4px;
    font-size: 12px;
}
div.stButton > button[kind="secondary"] {
    background-color: #E8E8E8;
    color: #1A1A1A;
    border: none;
    border-radius: 4px;
    font-size: 12px;
}
div.stButton > button[kind="primary"]:hover  { background-color: #333333; }
div.stButton > button[kind="secondary"]:hover { background-color: #D5D5D5; }

/* ── Add-item button ─────────────────────────────────────────── */
.add-btn-row { margin: 12px 0 20px; }

/* ── Form styling ────────────────────────────────────────────── */
div[data-testid="stForm"] {
    background: #FFFFFF;
    border: 1px solid #DEDEDE;
    border-radius: 8px;
    padding: 20px;
}
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
    sh = gc.open_by_key(st.secrets["sheet_id"])
    ws = sh.sheet1
    # Auto-create header row if the sheet is brand new
    if ws.row_count == 0 or ws.acell("A1").value != "id":
        ws.insert_row(SHEET_HEADERS, 1)
    return ws


# ─── Data access (cached for 4 seconds to avoid hammering the API)
@st.cache_data(ttl=4)
def load_items() -> list[dict]:
    try:
        return _sheet().get_all_records()
    except Exception as e:
        st.error(f"⚠️ Could not load data from Google Sheets: {e}")
        return []


def _clear_cache():
    load_items.clear()


# ─── Write helpers
def add_item(brand, candle_name, season, pvr, scent_notes, ops_notes, image_url=""):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    _sheet().append_row([
        str(uuid.uuid4()), brand, candle_name, season, pvr,
        scent_notes, ops_notes, image_url, "upcoming", now, now,
    ])
    _clear_cache()


def set_status(item_id: str, new_status: str):
    ws      = _sheet()
    records = ws.get_all_records()
    for i, rec in enumerate(records):
        if str(rec["id"]) == str(item_id):
            row = i + 2   # +1 for header, +1 for 1-indexing
            ws.update_cell(row, 9,  new_status)
            ws.update_cell(row, 11, datetime.now().strftime("%Y-%m-%d %H:%M"))
            break
    _clear_cache()


def update_item(item_id: str, **fields):
    ws      = _sheet()
    records = ws.get_all_records()
    col_map = {h: i + 1 for i, h in enumerate(SHEET_HEADERS)}
    for i, rec in enumerate(records):
        if str(rec["id"]) == str(item_id):
            row = i + 2
            for field, value in fields.items():
                if field in col_map:
                    ws.update_cell(row, col_map[field], value)
            ws.update_cell(row, col_map["updated_at"],
                           datetime.now().strftime("%Y-%m-%d %H:%M"))
            break
    _clear_cache()


def delete_item(item_id: str):
    ws      = _sheet()
    records = ws.get_all_records()
    for i, rec in enumerate(records):
        if str(rec["id"]) == str(item_id):
            ws.delete_rows(i + 2)
            break
    _clear_cache()


def upload_image(file_bytes: bytes, filename: str, mime_type: str) -> str:
    """Upload to Google Drive and return a publicly viewable URL."""
    _, drive = _get_services()
    folder_id = st.secrets["drive_folder_id"]

    media = MediaIoBaseUpload(io.BytesIO(file_bytes), mimetype=mime_type)
    f = drive.files().create(
        body={"name": filename, "parents": [folder_id]},
        media_body=media,
        fields="id",
    ).execute()

    fid = f["id"]
    drive.permissions().create(
        fileId=fid, body={"type": "anyone", "role": "reader"}
    ).execute()

    return f"https://drive.google.com/uc?export=view&id={fid}"


# ─────────────────────────────────────────────────────────────────
#  SESSION STATE DEFAULTS
# ─────────────────────────────────────────────────────────────────
def _init_state():
    defaults = {
        "show_add_form":    False,
        "editing_item_id":  None,
        "confirm_delete_id": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_state()


# ─────────────────────────────────────────────────────────────────
#  REUSABLE COMPONENTS
# ─────────────────────────────────────────────────────────────────
def _thumb_html(image_url: str, height: int = 155) -> str:
    if image_url:
        return f'<img src="{image_url}" style="width:100%;height:{height}px;object-fit:cover;">'
    return (f'<div style="height:{height}px;background:#EBEBEB;display:flex;'
            f'align-items:center;justify-content:center;color:#C7C7CC;font-size:13px;">'
            f'No image</div>')


def _upcoming_card_html(item: dict) -> str:
    def row(label, field, is_image=False):
        val = item.get(field, "")
        if is_image:
            if val:
                return (f'<div style="border-bottom:1px solid #DEDEDE;">'
                        f'<img src="{val}" style="width:100%;height:150px;object-fit:cover;display:block;"></div>')
            return ('<div style="height:150px;border-bottom:1px solid #DEDEDE;'
                    'display:flex;align-items:center;justify-content:center;'
                    'flex-direction:column;gap:4px;color:#C7C7CC;font-size:12px;">'
                    '🖼<br>No image yet</div>')
        color = "#1A1A1A" if val else "#C7C7CC"
        display = val if val else label
        return (f'<div style="padding:7px 10px;border-bottom:1px solid #DEDEDE;'
                f'font-size:11px;color:{color};text-align:center;">{display}</div>')

    return (
        '<div style="background:#FFF;border:1px solid #DEDEDE;border-radius:6px;overflow:hidden;">'
        + row("BRAND/COLLECTION", "brand")
        + row("CANDLE NAME",       "candle_name")
        + row("SEASON",            "season")
        + row("PVR",               "pvr")
        + row("",                  "image_url", is_image=True)
        + row("SCENT NOTES",       "scent_notes")
        + row("OPS NOTES",         "ops_notes")
        + '</div>'
    )


def _display_card_html(item: dict) -> str:
    brand = item.get("brand", "")
    name  = item.get("candle_name", "")
    meta  = "  ·  ".join(v for v in [item.get("season",""), item.get("pvr","")] if v)
    scent = item.get("scent_notes", "")
    ops   = item.get("ops_notes", "")

    body = ""
    if brand: body += f'<div class="card-brand">{brand}</div>'
    if name:  body += f'<div class="card-name">{name}</div>'
    if meta:  body += f'<div class="card-meta">{meta}</div>'
    if scent: body += f'<div class="card-notes">🌸 {scent}</div>'
    if ops:   body += f'<div class="card-notes">📋 {ops}</div>'

    return (
        '<div class="item-card">'
        + _thumb_html(item.get("image_url", ""))
        + f'<div class="card-body">{body}</div>'
        + '</div>'
    )


# ─────────────────────────────────────────────────────────────────
#  ADD / EDIT FORM
# ─────────────────────────────────────────────────────────────────
def _item_form(title: str, defaults: dict = None, form_key: str = "item_form"):
    """
    Renders an add/edit form.
    Returns (submitted, cancelled, form_data_dict).
    """
    d = defaults or {}
    submitted = cancelled = False
    data = {}

    with st.form(form_key, clear_on_submit=True):
        st.markdown(f"**{title}**")
        c1, c2 = st.columns(2)
        with c1:
            data["brand"]       = st.text_input("Brand / Collection", value=d.get("brand",""))
            data["season"]      = st.text_input("Season",             value=d.get("season",""))
            data["scent_notes"] = st.text_input("Scent Notes",        value=d.get("scent_notes",""))
        with c2:
            data["candle_name"] = st.text_input("Candle Name",        value=d.get("candle_name",""))
            data["pvr"]         = st.text_input("PVR",                value=d.get("pvr",""))
            data["ops_notes"]   = st.text_input("Ops Notes",          value=d.get("ops_notes",""))

        img_file = st.file_uploader(
            "Product image (optional)",
            type=["png","jpg","jpeg","webp","gif"],
            key=f"{form_key}_img",
        )
        data["_img_file"] = img_file

        cols = st.columns([1, 1, 4])
        with cols[0]:
            submitted = st.form_submit_button("Save", type="primary")
        with cols[1]:
            cancelled = st.form_submit_button("Cancel", type="secondary")

    return submitted, cancelled, data


# ─────────────────────────────────────────────────────────────────
#  PAGE: UPCOMING IN STUDIO
# ─────────────────────────────────────────────────────────────────
def page_upcoming(items: list[dict]):
    st.markdown('<div class="page-title">UPCOMING IN STUDIO</div>',
                unsafe_allow_html=True)

    upcoming = [i for i in items if i.get("status") == "upcoming"]

    # ── Add form ──────────────────────────────────────────────────
    if st.session_state.show_add_form:
        submitted, cancelled, data = _item_form("New Item", form_key="add_form")

        if cancelled:
            st.session_state.show_add_form = False
            st.rerun()

        if submitted:
            image_url = ""
            if data["_img_file"]:
                with st.spinner("Uploading image…"):
                    image_url = upload_image(
                        data["_img_file"].read(),
                        data["_img_file"].name,
                        data["_img_file"].type,
                    )
            add_item(
                data["brand"], data["candle_name"], data["season"],
                data["pvr"], data["scent_notes"], data["ops_notes"],
                image_url,
            )
            st.session_state.show_add_form = False
            st.rerun()

    # ── Edit form ─────────────────────────────────────────────────
    elif st.session_state.editing_item_id:
        edit_item = next(
            (i for i in upcoming
             if str(i["id"]) == str(st.session_state.editing_item_id)),
            None,
        )
        if edit_item:
            submitted, cancelled, data = _item_form(
                "Edit Item", defaults=edit_item, form_key="edit_form"
            )
            if cancelled:
                st.session_state.editing_item_id = None
                st.rerun()
            if submitted:
                fields = {k: v for k, v in data.items() if k != "_img_file"}
                if data["_img_file"]:
                    with st.spinner("Uploading image…"):
                        fields["image_url"] = upload_image(
                            data["_img_file"].read(),
                            data["_img_file"].name,
                            data["_img_file"].type,
                        )
                update_item(edit_item["id"], **fields)
                st.session_state.editing_item_id = None
                st.rerun()

    # ── Card grid + add button ────────────────────────────────────
    else:
        btn_col, _ = st.columns([1, 5])
        with btn_col:
            if st.button("＋  Add New Item", type="primary", use_container_width=True):
                st.session_state.show_add_form = True
                st.rerun()

        if not upcoming:
            st.markdown(
                '<div class="empty-plain">No upcoming items yet. '
                'Click <strong>+ Add New Item</strong> to get started.</div>',
                unsafe_allow_html=True,
            )
            return

        cols = st.columns(4)
        for idx, item in enumerate(upcoming):
            with cols[idx % 4]:
                st.markdown(_upcoming_card_html(item), unsafe_allow_html=True)

                # Action buttons
                b1, b2, b3 = st.columns([3, 2, 1])
                with b1:
                    if st.button("→ Current Week",
                                 key=f"up_cw_{item['id']}", type="primary",
                                 use_container_width=True):
                        set_status(item["id"], "current_week")
                        st.rerun()
                with b2:
                    if st.button("✏ Edit",
                                 key=f"up_ed_{item['id']}", type="secondary",
                                 use_container_width=True):
                        st.session_state.editing_item_id = item["id"]
                        st.rerun()
                with b3:
                    if st.button("✕",
                                 key=f"up_del_{item['id']}", type="secondary",
                                 use_container_width=True):
                        st.session_state.confirm_delete_id = item["id"]
                        st.rerun()

        # ── Delete confirmation
        if st.session_state.confirm_delete_id:
            st.warning("Are you sure you want to delete this item?")
            y, n, _ = st.columns([1, 1, 4])
            with y:
                if st.button("Yes, delete", type="primary"):
                    delete_item(st.session_state.confirm_delete_id)
                    st.session_state.confirm_delete_id = None
                    st.rerun()
            with n:
                if st.button("Cancel", type="secondary"):
                    st.session_state.confirm_delete_id = None
                    st.rerun()


# ─────────────────────────────────────────────────────────────────
#  GENERIC GRID PAGE  (Current Week / Catalog / Reshoot)
# ─────────────────────────────────────────────────────────────────
def page_grid(
    items:       list[dict],
    status:      str,
    title:       str,
    empty_icon:  str,
    empty_title: str,
    empty_sub:   str,
    actions:     list[tuple],   # (label, new_status, is_primary)
    plain_empty: bool = False,
):
    st.markdown(f'<div class="page-title">{title}</div>', unsafe_allow_html=True)

    filtered = [i for i in items if i.get("status") == status]

    if not filtered:
        if plain_empty:
            st.markdown(
                f'<div class="empty-plain">{empty_title}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(f"""
            <div class="empty-card">
                <div class="empty-icon">{empty_icon}</div>
                <div class="empty-title">{empty_title}</div>
                <div class="empty-sub">{empty_sub}</div>
            </div>""", unsafe_allow_html=True)
        return

    cols = st.columns(4)
    for idx, item in enumerate(filtered):
        with cols[idx % 4]:
            st.markdown(_display_card_html(item), unsafe_allow_html=True)

            btn_cols = st.columns(len(actions))
            for ci, (label, new_status, is_primary) in enumerate(actions):
                with btn_cols[ci]:
                    btn_type = "primary" if is_primary else "secondary"
                    if st.button(label,
                                 key=f"{status}_{new_status}_{item['id']}",
                                 type=btn_type,
                                 use_container_width=True):
                        set_status(item["id"], new_status)
                        st.rerun()


# ─────────────────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────────────────
def main():
    items = load_items()

    tab1, tab2, tab3, tab4 = st.tabs([
        "⏱  Upcoming in Studio",
        "☐  Current Week",
        "≡  Home Fragrance Catalog",
        "↺  Reshoot Requests",
    ])

    with tab1:
        page_upcoming(items)

    with tab2:
        page_grid(
            items,
            status      = "current_week",
            title       = "CURRENT WEEK",
            empty_icon  = "",
            empty_title = 'No items yet. Add items from the "Upcoming in Studio" tab.',
            empty_sub   = "",
            actions     = [
                ("→ Archive to Catalog", "catalog",  True),
                ("← Back to Upcoming",  "upcoming", False),
            ],
            plain_empty = True,
        )

    with tab3:
        page_grid(
            items,
            status      = "catalog",
            title       = "HOME FRAGRANCE CATALOG",
            empty_icon  = "≡",
            empty_title = "No archived items yet",
            empty_sub   = "Items moved from Current Week will appear here",
            actions     = [
                ("↺ Mark for Reshoot",  "reshoot",      True),
                ("← Back to Current",   "current_week", False),
            ],
        )

    with tab4:
        page_grid(
            items,
            status      = "reshoot",
            title       = "RESHOOT REQUESTS",
            empty_icon  = "↺",
            empty_title = "No items marked for reshoots",
            empty_sub   = "Items recycled from the catalog will appear here",
            actions     = [
                ("→ Back to Upcoming", "upcoming", True),
                ("→ Re-archive",       "catalog",  False),
            ],
        )


if __name__ == "__main__":
    main()
