from contextlib import asynccontextmanager
from typing import Dict, List
import itertools

from fastapi import FastAPI, HTTPException, Query

from app.models import (
    StudentProfile,
    StudentCreate,
    StudentRecord,
    PGCreate,
    MatchRequest,
    MatchResponse,
    PGMatchResult,
    PGProfile,
    MatchScoreBreakdown,
)
from app.database import ensure_db, get_all_pgs, get_all_students, add_pg, add_student
from app.dsa.trie import Trie
from app.dsa.heap import TopKHeap
from app.dsa.graph import AdjacencyListGraph
from app.dsa.scoring import calculate_pg_match_score, calculate_flatmate_match_score

# ---------------------------------------------------------
# In-Memory Data Structures (filled at startup, updated when you add records)
# ---------------------------------------------------------
pgs_map: Dict[str, dict] = {}
students_map: Dict[str, dict] = {}
area_lookup: Dict[str, str] = {}   # "viman nagar" -> "Viman Nagar" (one official spelling per area)
location_trie = Trie()
student_graph = AdjacencyListGraph()

FLATMATE_EDGE_THRESHOLD = 30.0


def connect_student_to_graph(new_student: dict):
    """
    Adds a student to the graph and connects them to everyone already in it.
    Cost: one score calculation per existing student, so O(N).
    """
    student_graph.add_node(new_student['id'])
    for other_id, other_student in students_map.items():
        if other_id == new_student['id']:
            continue
        score = calculate_flatmate_match_score(new_student, other_student)
        if score > FLATMATE_EDGE_THRESHOLD:
            student_graph.add_edge(new_student['id'], other_id, score)


def load_data():
    global location_trie, student_graph

    # Creates (or upgrades) the database first if needed
    ensure_db()

    raw_pgs = get_all_pgs()
    raw_students = get_all_students()

    pgs_map.clear()
    students_map.clear()
    area_lookup.clear()
    location_trie = Trie()
    student_graph = AdjacencyListGraph()

    for pg in raw_pgs:
        pgs_map[pg['id']] = pg
        area_key = pg['area'].lower()
        if area_key not in area_lookup:
            area_lookup[area_key] = pg['area']
            location_trie.insert(pg['area'])

    for student in raw_students:
        students_map[student['id']] = student
        student_graph.add_node(student['id'])

    for student_one, student_two in itertools.combinations(raw_students, 2):
        score = calculate_flatmate_match_score(student_one, student_two)
        if score > FLATMATE_EDGE_THRESHOLD:
            student_graph.add_edge(student_one['id'], student_two['id'], score)

    print("Startup complete: Data loaded into Hash Maps, Trie, and Graph.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_data()
    yield


app = FastAPI(title="Smart PG & Flatmate Matcher", lifespan=lifespan)


def build_current_pg_result(searcher: dict, pg_id):
    """
    Scores the PG a flatmate already lives in against the person searching.
    Returns None if the flatmate isn't staying in a PG.
    """
    if not pg_id or pg_id not in pgs_map:
        return None

    pg_data = pgs_map[pg_id]
    score_data = calculate_pg_match_score(searcher, pg_data)
    return {
        "pg": PGProfile(**pg_data).model_dump(mode="json"),
        "overall_score": score_data["overall_score"],
        "breakdown": score_data["breakdown"],
    }


def build_flatmate_entry(searcher: dict, neighbor_id: str, score: float) -> dict:
    neighbor_data = students_map[neighbor_id]
    shared_habits = set(searcher["habits_set"]) & set(neighbor_data["habits_set"])
    return {
        "flatmate_id": neighbor_id,
        "name": neighbor_data["name"],
        "compatibility_score": score,
        "shared_habits": sorted(shared_habits),
        "current_pg": build_current_pg_result(searcher, neighbor_data.get("current_pg_id")),
    }


# ---------------------------------------------------------
# Search endpoints
# ---------------------------------------------------------
@app.get("/autocomplete", response_model=List[str])
def autocomplete_locations(q: str = ""):
    if not q:
        return []
    return location_trie.search_prefix(q)


@app.post("/match/pgs", response_model=MatchResponse)
def match_pgs(request: MatchRequest, k: int = Query(5, ge=1, le=50)):
    student_dict = request.student.model_dump()

    # Bounded heap: only the best K PGs are ever kept, so this is O(N log K)
    top_heap = TopKHeap(k)

    for pg_id, pg_data in pgs_map.items():
        score_data = calculate_pg_match_score(student_dict, pg_data)
        top_heap.push((score_data["overall_score"], {
            "pg": pg_data,
            "overall_score": score_data["overall_score"],
            "breakdown": score_data["breakdown"],
        }))

    top_matches = []
    for score, match_data in top_heap.get_sorted_desc():
        pg_profile = PGProfile(**match_data["pg"])
        breakdown = MatchScoreBreakdown.model_validate(match_data["breakdown"])
        top_matches.append(
            PGMatchResult(
                pg=pg_profile,
                overall_score=match_data["overall_score"],
                breakdown=breakdown,
            )
        )

    return MatchResponse(student_id=request.student.id, matches=top_matches)


@app.get("/match/flatmates")
def match_flatmates(student_id: str, k: int = Query(5, ge=1, le=50)):
    """Flatmates for an EXISTING student, using the graph. Their PG is scored against this student's preferences."""
    if student_id not in students_map:
        raise HTTPException(status_code=404, detail="Student not found")

    searcher = students_map[student_id]
    top_connections = student_graph.get_top_k_neighbors(student_id, k)

    results = []
    for connection in top_connections:
        results.append(build_flatmate_entry(searcher, connection["neighbor_id"], connection["score"]))

    return {"student_id": student_id, "top_flatmates": results}


@app.post("/match/flatmates/profile")
def match_flatmates_for_profile(student: StudentProfile, k: int = Query(5, ge=1, le=50)):
    """
    Flatmates for a NEW profile (the one typed into the sidebar).
    This person isn't in the graph, so we score them against every stored
    student and keep the best K with the bounded heap.
    """
    profile_dict = student.model_dump()
    top_heap = TopKHeap(k)

    for other_id, other_student in students_map.items():
        if other_id == student.id:
            continue
        score = calculate_flatmate_match_score(profile_dict, other_student)
        top_heap.push((score, other_id))

    results = []
    for score, other_id in top_heap.get_sorted_desc():
        results.append(build_flatmate_entry(profile_dict, other_id, score))

    return {"student_id": student.id, "top_flatmates": results}


# ---------------------------------------------------------
# Add-new-data endpoints
# ---------------------------------------------------------
@app.get("/pgs", response_model=List[PGProfile])
def list_pgs():
    """All PGs, used by the roommate form's 'Which PG do you live in?' dropdown."""
    return [PGProfile(**pg) for pg in pgs_map.values()]


@app.post("/pgs", response_model=PGProfile, status_code=201)
def create_pg(new_pg: PGCreate):
    pg_data = new_pg.model_dump()

    # Reject the same PG name in the same area
    for existing_pg in pgs_map.values():
        same_name = existing_pg["name"].lower() == pg_data["name"].lower()
        same_area = existing_pg["area"].lower() == pg_data["area"].lower()
        if same_name and same_area:
            raise HTTPException(status_code=409, detail="A PG with this name already exists in that area.")

    # Reuse the official spelling if the area is already known ("wakad" -> "Wakad")
    area_key = pg_data["area"].lower()
    is_new_area = area_key not in area_lookup
    if not is_new_area:
        pg_data["area"] = area_lookup[area_key]

    # Save to the database FIRST, then update memory
    saved_pg = add_pg(pg_data)
    pgs_map[saved_pg["id"]] = saved_pg

    if is_new_area:
        area_lookup[area_key] = saved_pg["area"]
        location_trie.insert(saved_pg["area"])

    return PGProfile(**saved_pg)


@app.post("/students", response_model=StudentRecord, status_code=201)
def create_student(new_student: StudentCreate):
    student_data = new_student.model_dump()

    if student_data["current_pg_id"] and student_data["current_pg_id"] not in pgs_map:
        raise HTTPException(status_code=400, detail="That PG does not exist. Pick one from the list.")

    for existing_student in students_map.values():
        if existing_student["name"].lower() == student_data["name"].lower():
            raise HTTPException(status_code=409, detail="A student with this name already exists.")

    area_key = student_data["preferred_area"].lower()
    if area_key in area_lookup:
        student_data["preferred_area"] = area_lookup[area_key]

    # Save to the database FIRST, then update memory
    saved_student = add_student(student_data)
    students_map[saved_student["id"]] = saved_student
    connect_student_to_graph(saved_student)

    return StudentRecord(**saved_student)