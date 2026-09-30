import html

import requests
import streamlit as st
import streamlit_shadcn_ui as ui

API_URL = "http://127.0.0.1:8000"
DEFAULT_AREAS = ["Wakad", "Hinjewadi", "Viman Nagar", "Kothrud", "Baner"]
PG_AMENITY_OPTIONS = ["WiFi", "Gym", "Washing Machine", "Power Backup", "Pool", "Library"]
ROOMMATE_AMENITY_OPTIONS = PG_AMENITY_OPTIONS + ["AC"]
HABIT_OPTIONS = ["studying_late", "gaming", "fitness", "reading", "cooking", "music", "yoga"]

BREAKDOWN_LABELS = [
    ("area_score", "Area"),
    ("budget_score", "Budget"),
    ("distance_score", "Distance"),
    ("amenities_score", "Amenities"),
    ("food_score", "Food"),
]

st.set_page_config(page_title="Smart PG Matcher", layout="wide")

# ---------------------------------------------------------
# Styling: one place for every colour, size and spacing
# ---------------------------------------------------------
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
    --ink: #0F172A;
    --muted: #64748B;
    --line: #E2E8F0;
    --soft: #F1F5F9;
    --card: #FFFFFF;
    --good: #15803D;
    --good-bg: #DCFCE7;
    --mid: #B45309;
    --mid-bg: #FEF3C7;
    --low: #B91C1C;
    --low-bg: #FEE2E2;
}

/* Font: applied to text elements only, so Streamlit's icon fonts keep working */
.stApp, .stApp p, .stApp label, .stApp li, .stApp input, .stApp textarea,
.stApp button, .stApp h1, .stApp h2, .stApp h3, .stApp h4 {
    font-family: 'Inter', -apple-system, 'Segoe UI', Roboto, sans-serif;
}

/* Hide the clutter but keep the header so the sidebar toggle still works */
#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"] { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }

.stApp { background: #F8FAFC; }
.block-container { padding-top: 2.2rem; max-width: 1180px; }

/* Page header */
.hero { padding: 0.25rem 0 1.25rem; }
.eyebrow { font-size: 0.75rem; letter-spacing: 0.12em; text-transform: uppercase; color: var(--muted); font-weight: 600; }
.stApp .hero h1 { font-size: 2.1rem; font-weight: 700; letter-spacing: -0.02em; margin: 0.3rem 0 0.4rem; padding: 0; color: var(--ink); }
.hero p { color: var(--muted); margin: 0; font-size: 1rem; }

/* Sidebar */
section[data-testid="stSidebar"] { border-right: 1px solid var(--line); }
.side-title { font-size: 1.05rem; font-weight: 600; color: var(--ink); letter-spacing: -0.01em; }
.side-label { font-size: 0.7rem; letter-spacing: 0.1em; text-transform: uppercase; color: var(--muted); font-weight: 600; margin: 1.2rem 0 0.4rem; }

/* Section headings inside tabs */
.section-title { font-size: 1.25rem; font-weight: 600; color: var(--ink); letter-spacing: -0.01em; margin-top: 0.75rem; }
.section-sub { color: var(--muted); font-size: 0.9rem; margin: 0.2rem 0 1.1rem; }
.summary { color: var(--muted); font-size: 0.85rem; margin: 0 0 1rem; }

/* Cards */
.card { background: var(--card); border: 1px solid var(--line); border-radius: 14px; padding: 1.25rem 1.35rem; margin-bottom: 1rem; box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04); transition: box-shadow 0.2s ease, border-color 0.2s ease; }
.card:hover { box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08); border-color: #CBD5E1; }
.card.nested { background: var(--soft); box-shadow: none; margin: 0.4rem 0 0; padding: 1rem 1.1rem; }
.card.nested:hover { box-shadow: none; border-color: var(--line); }
.card-top { display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem; }
.card-title { font-size: 1.1rem; font-weight: 600; color: var(--ink); letter-spacing: -0.01em; }
.card-sub { font-size: 0.85rem; color: var(--muted); margin-top: 0.15rem; }
.id-chip { font-size: 0.7rem; font-weight: 500; color: var(--muted); background: var(--soft); border: 1px solid var(--line); border-radius: 6px; padding: 0.1rem 0.4rem; margin-left: 0.4rem; vertical-align: middle; }

/* Score badge, coloured by how good the score is */
.score { text-align: right; line-height: 1; padding: 0.5rem 0.7rem; border-radius: 10px; white-space: nowrap; }
.score-num { font-size: 1.35rem; font-weight: 700; }
.score-unit { font-size: 0.7rem; font-weight: 500; margin-left: 0.2rem; }
.score-high { color: var(--good); background: var(--good-bg); }
.score-mid { color: var(--mid); background: var(--mid-bg); }
.score-low { color: var(--low); background: var(--low-bg); }

.rent { font-size: 1.35rem; font-weight: 700; color: var(--ink); margin: 0.9rem 0 0.6rem; }
.rent span { font-size: 0.85rem; font-weight: 400; color: var(--muted); }
.label { font-size: 0.7rem; letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted); font-weight: 600; margin: 0.9rem 0 0.4rem; }
.muted { color: var(--muted); font-size: 0.85rem; }
.facts { font-size: 0.82rem; color: var(--muted); margin-bottom: 0.8rem; }
.divider { height: 1px; background: var(--line); margin: 1rem 0 0.2rem; }

/* Pills (amenities and habits) */
.pills { display: flex; flex-wrap: wrap; gap: 0.4rem; margin-bottom: 0.6rem; }
.pill { font-size: 0.75rem; font-weight: 500; padding: 0.2rem 0.65rem; border-radius: 999px; background: var(--soft); border: 1px solid var(--line); color: #334155; }
.card.nested .pill { background: #FFFFFF; }

/* Progress bars */
.bar { height: 6px; border-radius: 999px; background: var(--line); overflow: hidden; }
.bar .fill { height: 100%; border-radius: 999px; background: #475569; }
.bar .fill-high { background: var(--good); }
.bar .fill-mid { background: #D97706; }
.bar .fill-low { background: var(--low); }
.bar-thin { height: 4px; }

/* Score breakdown (opens and closes by itself, no Python needed) */
.details { margin-top: 0.9rem; border-top: 1px solid var(--line); padding-top: 0.7rem; }
.details summary { cursor: pointer; font-size: 0.82rem; font-weight: 500; color: var(--muted); }
.bd-row { display: grid; grid-template-columns: 78px 1fr 42px; align-items: center; gap: 0.6rem; margin-top: 0.55rem; font-size: 0.8rem; color: #334155; }
.bd-value { text-align: right; color: var(--muted); }

/* Empty state */
.empty { border: 1px dashed #CBD5E1; border-radius: 14px; padding: 2.2rem 1rem; text-align: center; color: var(--muted); background: #FFFFFF; }
.empty-title { font-weight: 600; color: var(--ink); margin-bottom: 0.25rem; }

/* Forms */
[data-testid="stForm"] { background: #FFFFFF; border: 1px solid var(--line); border-radius: 14px; padding: 1.5rem; box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04); }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------
def call_api(method, path, **kwargs):
    """Calls the backend and always returns a small dictionary describing what happened."""
    try:
        response = requests.request(method, f"{API_URL}{path}", timeout=10, **kwargs)
    except requests.exceptions.RequestException:
        return {"ok": False, "error": "Backend offline. Please start FastAPI."}

    if response.status_code in (200, 201):
        return {"ok": True, "data": response.json()}

    try:
        detail = response.json().get("detail", response.text)
    except ValueError:
        detail = response.text
    return {"ok": False, "error": f"{detail}"}


def esc(value):
    """Makes text safe to place inside HTML (PG names come from users)."""
    return html.escape(str(value))


def score_tone(score):
    if score >= 80:
        return "high"
    if score >= 60:
        return "mid"
    return "low"


def pills_html(items):
    if not items:
        return "<span class='muted'>None</span>"
    return "".join(f"<span class='pill'>{esc(item)}</span>" for item in items)


def score_badge_html(score, unit):
    tone = score_tone(score)
    return (
        f"<div class='score score-{tone}'>"
        f"<span class='score-num'>{score:.1f}</span>"
        f"<span class='score-unit'>{esc(unit)}</span>"
        "</div>"
    )


def bar_html(score):
    width = min(max(score, 0), 100)
    return f"<div class='bar'><div class='fill fill-{score_tone(score)}' style='width:{width}%'></div></div>"


def breakdown_html(breakdown):
    rows = []
    for key, label in BREAKDOWN_LABELS:
        value = breakdown[key]
        width = min(max(value, 0), 100)
        rows.append(
            "<div class='bd-row'>"
            f"<span>{label}</span>"
            f"<div class='bar bar-thin'><div class='fill' style='width:{width}%'></div></div>"
            f"<span class='bd-value'>{value:.0f}%</span>"
            "</div>"
        )
    return "".join(rows)


# Note: the HTML below is joined with no blank lines on purpose.
# A blank line would make Streamlit stop treating the rest as HTML.
def pg_card_html(match, unit="% match", nested=False):
    pg = match["pg"]
    score = match["overall_score"]
    card_class = "card nested" if nested else "card"
    ac_text = "Yes" if pg["ac_available"] else "No"

    return "".join([
        f"<div class='{card_class}'>",
        "<div class='card-top'>",
        "<div>",
        f"<div class='card-title'>{esc(pg['name'])}</div>",
        f"<div class='card-sub'>{esc(pg['area'])} &middot; {pg['distance_km']} km away</div>",
        "</div>",
        score_badge_html(score, unit),
        "</div>",
        f"<div class='rent'>&#8377;{pg['rent']:,.0f}<span> / month</span></div>",
        f"<div class='pills'>{pills_html(sorted(pg['amenities_set']))}</div>",
        f"<div class='facts'>Food: {esc(pg['food_offered'])} &middot; AC: {ac_text}</div>",
        bar_html(score),
        "<details class='details'><summary>Score breakdown</summary>",
        breakdown_html(match["breakdown"]),
        "</details>",
        "</div>",
    ])


def flatmate_card_html(flatmate):
    score = flatmate["compatibility_score"]

    parts = [
        "<div class='card'>",
        "<div class='card-top'>",
        "<div>",
        f"<div class='card-title'>{esc(flatmate['name'])}<span class='id-chip'>{esc(flatmate['flatmate_id'])}</span></div>",
        "<div class='card-sub'>Potential flatmate</div>",
        "</div>",
        score_badge_html(score, "% compatible"),
        "</div>",
        "<div class='label'>Shared habits</div>",
        f"<div class='pills'>{pills_html(flatmate['shared_habits'])}</div>",
        bar_html(score),
        "<div class='divider'></div>",
        "<div class='label'>Currently staying at</div>",
    ]

    current_pg = flatmate.get("current_pg")
    if current_pg is None:
        parts.append("<div class='muted'>Not staying in a PG right now.</div>")
    else:
        parts.append(pg_card_html(current_pg, unit="% fit for you", nested=True))

    parts.append("</div>")
    return "".join(parts)


def section_header(title, subtitle):
    st.markdown(
        f"<div class='section-title'>{esc(title)}</div><div class='section-sub'>{esc(subtitle)}</div>",
        unsafe_allow_html=True,
    )


def empty_state(title, message):
    st.markdown(
        f"<div class='empty'><div class='empty-title'>{esc(title)}</div><div>{esc(message)}</div></div>",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------
# Page header
# ---------------------------------------------------------
st.markdown(
    "<div class='hero'>"
    "<div class='eyebrow'>Pune &middot; PGs and roommates</div>"
    "<h1>Smart PG &amp; Flatmate Matching</h1>"
    "<p>Find a place to stay and people to share it with, ranked by how well they fit you.</p>"
    "</div>",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# Sidebar: preferences
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("<div class='side-title'>Your preferences</div>", unsafe_allow_html=True)

    st.markdown("<div class='side-label'>Location</div>", unsafe_allow_html=True)
    area_prefix = st.text_input("Search area", "", placeholder="Start typing, for example Wak")
    area_options = DEFAULT_AREAS
    if area_prefix:
        autocomplete_result = call_api("GET", "/autocomplete", params={"q": area_prefix})
        if autocomplete_result["ok"] and autocomplete_result["data"]:
            area_options = autocomplete_result["data"]
        elif not autocomplete_result["ok"]:
            st.error(autocomplete_result["error"])
    selected_area = st.selectbox("Preferred area", area_options)

    st.markdown("<div class='side-label'>Budget and distance</div>", unsafe_allow_html=True)
    budget = st.slider("Max budget (INR per month)", 5000, 30000, 15000, step=500)
    distance = st.slider("Max distance (km)", 0.5, 20.0, 5.0, step=0.5)

    st.markdown("<div class='side-label'>Lifestyle</div>", unsafe_allow_html=True)
    food = st.radio("Food preference", ["Veg", "Non-Veg", "Any"], horizontal=True)
    sleep = st.selectbox("Sleep schedule", ["Early Bird", "Night Owl", "Flexible"])
    amenities = st.multiselect("Required amenities", ROOMMATE_AMENITY_OPTIONS, default=["WiFi"])
    habits = st.multiselect("Your habits", HABIT_OPTIONS, default=["reading"])

    st.markdown("<div class='side-label'>Flatmate matching</div>", unsafe_allow_html=True)
    flatmate_mode = st.radio(
        "Match flatmates using",
        ["My profile above", "An existing student ID"],
        label_visibility="collapsed",
    )
    existing_student_id = ""
    if flatmate_mode == "An existing student ID":
        existing_student_id = st.text_input("Existing student ID", "S01")

    st.write("")
    find_matches = ui.button("Find Matches", key="find_matches_btn")

# ---------------------------------------------------------
# Action: call the API and SAVE the results in session_state
# ---------------------------------------------------------
if find_matches:
    student_profile = {
        "id": "TEMP_USER",
        "name": "Guest User",
        "budget": budget,
        "preferred_area": selected_area,
        "max_distance_km": distance,
        "food_pref": food,
        "sleep_schedule": sleep,
        "habits_set": habits,
        "amenities_set": amenities,
    }

    with st.spinner("Finding your best matches..."):
        st.session_state["pg_result"] = call_api(
            "POST", "/match/pgs", params={"k": 5},
            json={"student": student_profile, "available_pgs": []},
        )

        if flatmate_mode == "My profile above":
            st.session_state["flatmate_result"] = call_api(
                "POST", "/match/flatmates/profile", params={"k": 5}, json=student_profile,
            )
        else:
            st.session_state["flatmate_result"] = call_api(
                "GET", "/match/flatmates",
                params={"student_id": existing_student_id, "k": 5},
            )

    if st.session_state["pg_result"]["ok"]:
        st.toast("Matches updated")

# ---------------------------------------------------------
# Main navigation (shadcn tabs)
# ---------------------------------------------------------
TAB_OPTIONS = ["PG Matches", "Flatmate Matches", "Add a PG", "Add Roommate", "How It Works"]


def render_navigation():
    """
    Shows the shadcn tabs. Different versions of streamlit-shadcn-ui name the
    starting-tab argument differently, so we try each style, and fall back to
    a plain Streamlit selector if neither works.
    """
    try:
        return ui.tabs(options=TAB_OPTIONS, default_value=TAB_OPTIONS[0], key="main_tabs")
    except Exception:
        pass

    try:
        return ui.tabs(options=TAB_OPTIONS, value=TAB_OPTIONS[0], key="main_tabs_v2")
    except Exception:
        pass

    return st.radio(
        "Navigation",
        TAB_OPTIONS,
        horizontal=True,
        label_visibility="collapsed",
        key="main_tabs_fallback",
    )


chosen_tab = render_navigation() or TAB_OPTIONS[0]

# ----- PG matches -----
if chosen_tab == "PG Matches":
    section_header("Top PG recommendations", "Ranked by how closely each PG fits your preferences.")
    pg_result = st.session_state.get("pg_result")

    if pg_result is None:
        empty_state("No search yet", "Set your preferences in the sidebar and click Find Matches.")
    elif not pg_result["ok"]:
        st.error(pg_result["error"])
    else:
        matches = pg_result["data"].get("matches", [])
        if not matches:
            empty_state("No PGs found", "Try widening your budget or distance.")
        else:
            best_score = matches[0]["overall_score"]
            st.markdown(
                f"<div class='summary'>Showing the top {len(matches)} PGs. Best fit: {best_score:.1f}%</div>",
                unsafe_allow_html=True,
            )
            columns = st.columns(2, gap="medium")
            for index, match in enumerate(matches):
                with columns[index % 2]:
                    st.markdown(pg_card_html(match), unsafe_allow_html=True)

# ----- Flatmate matches -----
elif chosen_tab == "Flatmate Matches":
    section_header("Compatible flatmates", "Each flatmate is shown with the PG they already live in, scored for you.")
    flatmate_result = st.session_state.get("flatmate_result")

    if flatmate_result is None:
        empty_state("No search yet", "Click Find Matches in the sidebar to see flatmates.")
    elif not flatmate_result["ok"]:
        st.warning(flatmate_result["error"])
    else:
        flatmates = flatmate_result["data"].get("top_flatmates", [])
        if not flatmates:
            empty_state("No flatmates found", "No one is compatible enough yet. Try adding more roommates.")
        else:
            columns = st.columns(2, gap="medium")
            for index, flatmate in enumerate(flatmates):
                with columns[index % 2]:
                    st.markdown(flatmate_card_html(flatmate), unsafe_allow_html=True)

# ----- Add a PG -----
elif chosen_tab == "Add a PG":
    section_header("Add a new PG", "List a PG so it shows up in everyone's searches.")

    with st.form("add_pg_form"):
        new_pg_name = st.text_input("PG name")
        new_pg_area = st.text_input("Area", placeholder="For example Wakad, or a brand new area")

        left_col, right_col = st.columns(2)
        with left_col:
            new_pg_rent = st.number_input("Rent (INR per month)", min_value=1000, max_value=200000, value=10000, step=500)
            new_pg_food = st.selectbox("Food offered", ["Any", "Veg", "Non-Veg"])
        with right_col:
            new_pg_distance = st.number_input("Distance from campus (km)", min_value=0.0, max_value=50.0, value=2.0, step=0.1)
            new_pg_ac = st.checkbox("AC available", value=False)

        new_pg_amenities = st.multiselect("Amenities", PG_AMENITY_OPTIONS, default=["WiFi"])
        submit_pg = st.form_submit_button("Save PG", type="primary")

    if submit_pg:
        if not new_pg_name.strip() or not new_pg_area.strip():
            st.error("Please fill in both the PG name and the area.")
        else:
            add_pg_result = call_api("POST", "/pgs", json={
                "name": new_pg_name,
                "area": new_pg_area,
                "rent": new_pg_rent,
                "distance_km": new_pg_distance,
                "food_offered": new_pg_food,
                "ac_available": new_pg_ac,
                "amenities_set": new_pg_amenities,
            })
            if add_pg_result["ok"]:
                saved_pg = add_pg_result["data"]
                st.success(f"Saved {saved_pg['name']} with ID {saved_pg['id']}. It will now show up in searches.")
            else:
                st.error(add_pg_result["error"])

# ----- Add yourself as a roommate -----
elif chosen_tab == "Add Roommate":
    section_header("Add yourself as a roommate", "Let others find you, and tell us which PG you already live in.")

    pg_list_result = call_api("GET", "/pgs")
    pg_labels = {}
    if pg_list_result["ok"]:
        for pg in pg_list_result["data"]:
            pg_labels[pg["id"]] = f"{pg['name']} ({pg['area']}, INR {pg['rent']:,.0f})"
    else:
        st.error(pg_list_result["error"])

    pg_choices = [None] + list(pg_labels.keys())

    with st.form("add_roommate_form"):
        rm_name = st.text_input("Your name")
        rm_current_pg = st.selectbox(
            "Which PG do you live in?",
            pg_choices,
            format_func=lambda pg_id: "Not staying in a PG" if pg_id is None else pg_labels[pg_id],
        )

        left_col, right_col = st.columns(2)
        with left_col:
            rm_area = st.text_input("Preferred area")
            rm_budget = st.number_input("Max budget (INR per month)", min_value=1000, max_value=200000, value=12000, step=500)
            rm_food = st.selectbox("Food preference", ["Any", "Veg", "Non-Veg"])
        with right_col:
            rm_distance = st.number_input("Max distance (km)", min_value=0.5, max_value=50.0, value=3.0, step=0.5)
            rm_sleep = st.selectbox("Sleep schedule", ["Flexible", "Early Bird", "Night Owl"])

        rm_amenities = st.multiselect("Required amenities", ROOMMATE_AMENITY_OPTIONS, default=["WiFi"])
        rm_habits = st.multiselect("Your habits", HABIT_OPTIONS)
        submit_roommate = st.form_submit_button("Save my profile", type="primary")

    if submit_roommate:
        if not rm_name.strip() or not rm_area.strip():
            st.error("Please fill in your name and preferred area.")
        else:
            add_student_result = call_api("POST", "/students", json={
                "name": rm_name,
                "preferred_area": rm_area,
                "budget": rm_budget,
                "max_distance_km": rm_distance,
                "food_pref": rm_food,
                "sleep_schedule": rm_sleep,
                "habits_set": rm_habits,
                "amenities_set": rm_amenities,
                "current_pg_id": rm_current_pg,
            })
            if add_student_result["ok"]:
                saved_student = add_student_result["data"]
                st.success(
                    f"Saved {saved_student['name']} with ID {saved_student['id']}. "
                    "Other people can now find you as a flatmate."
                )
            else:
                st.error(add_student_result["error"])

# ----- How it works -----
elif chosen_tab == "How It Works":
    section_header("How it works", "The data structures and algorithms behind the matching.")
    st.markdown("""
    This app keeps its data in memory using custom data structures instead of running a SQL query for every search.

    ### 1. Hash Maps (Dictionaries) -> $O(1)$ Lookups
    All `PGProfile` and `StudentProfile` records are loaded from SQLite into Python dictionaries at startup. New PGs and roommates are saved to SQLite and added to these dictionaries at the same time.
    - **Why?** Getting one record by its ID takes constant time, instead of scanning every row. This is also how a flatmate's current PG is found instantly from its ID.

    ### 2. Prefix Trie -> $O(P)$ to Find a Prefix
    The area autocomplete walks a custom `Trie`. Finding the spot for a prefix of length $P$ takes $O(P)$ steps, no matter how many locations are stored. Collecting the suggestions then costs time proportional to the number of matches under that prefix. When someone adds a PG in a brand new area, that area is inserted into the Trie right away.
    - **Why?** A plain array scan has to check every stored location, which is $O(N)$.

    ### 3. Bounded Min-Heap -> $O(N \\log K)$ Top-K Ranking
    Every PG gets a score. Instead of sorting all $N$ scores, we keep a small heap holding only the best $K$ so far. The weakest of those $K$ sits on top, so a newcomer only has to beat that one item to get in.
    - **Why?** Each of the $N$ PGs costs at most $O(\\log K)$, so the total is $O(N \\log K)$ using only $O(K)$ extra memory. When $K$ is small (like 5), that beats a full sort at $O(N \\log N)$.

    ### 4. Adjacency List Graph -> $O(1)$ Neighbor Lookup
    Students are **nodes** and compatibility scores are **weighted edges**, pre-computed at startup.
    - **Why?** Fetching a student's neighbors is $O(1)$. Ranking their $D$ neighbors with the bounded heap then costs $O(D \\log K)$, instead of recalculating every score from scratch.
    - **Adding a roommate:** a new student is scored against everyone already in the graph once, so adding one costs $O(N)$.
    - **Note:** "My profile" mode uses a profile that isn't in the graph, so it scores against all stored students, which is $O(N \\log K)$.
    """)