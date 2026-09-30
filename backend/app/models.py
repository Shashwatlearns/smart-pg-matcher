from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Set, List
from enum import Enum


class FoodPreference(str, Enum):
        VEG = "Veg"
        NON_VEG = "Non-Veg"
        ANY = "Any"


class SleepSchedule(str, Enum):
        EARLY_BIRD = "Early Bird"
        NIGHT_OWL = "Night Owl"
        FLEXIBLE = "Flexible"


# ---------------------------------------------------------
# Used when SEARCHING
# ---------------------------------------------------------
class StudentProfile(BaseModel):
        # use_enum_values makes model_dump() give plain strings like "Veg"
        model_config = ConfigDict(use_enum_values=True)

        id: str = Field(..., description="Unique identifier for the student")
        name: str
        budget: float = Field(..., gt=0, description="Maximum monthly budget")
        preferred_area: str
        max_distance_km: float = Field(..., gt=0, description="Maximum acceptable distance from campus/work")
        food_pref: FoodPreference
        sleep_schedule: SleepSchedule
        habits_set: Set[str] = Field(default_factory=set, description="E.g., {'gaming', 'studying_late'}")
        amenities_set: Set[str] = Field(default_factory=set, description="Required amenities, e.g., {'WiFi', 'Gym'}")


class PGProfile(BaseModel):
        model_config = ConfigDict(use_enum_values=True)

        id: str
        name: str
        rent: float = Field(..., gt=0)
        area: str
        distance_km: float = Field(..., ge=0)
        food_offered: FoodPreference
        ac_available: bool
        amenities_set: Set[str] = Field(default_factory=set)


# ---------------------------------------------------------
# Used when ADDING new records (no id yet, the server makes one)
# ---------------------------------------------------------
class PGCreate(BaseModel):
        model_config = ConfigDict(use_enum_values=True, str_strip_whitespace=True)

        name: str = Field(..., min_length=1)
        rent: float = Field(..., gt=0)
        area: str = Field(..., min_length=1)
        distance_km: float = Field(..., ge=0)
        food_offered: FoodPreference
        ac_available: bool = False
        amenities_set: Set[str] = Field(default_factory=set)


class StudentCreate(BaseModel):
        model_config = ConfigDict(use_enum_values=True, str_strip_whitespace=True)

        name: str = Field(..., min_length=1)
        budget: float = Field(..., gt=0)
        preferred_area: str = Field(..., min_length=1)
        max_distance_km: float = Field(..., gt=0)
        food_pref: FoodPreference
        sleep_schedule: SleepSchedule
        habits_set: Set[str] = Field(default_factory=set)
        amenities_set: Set[str] = Field(default_factory=set)
        current_pg_id: Optional[str] = Field(default=None, description="The PG this person already lives in, if any")


class StudentRecord(StudentProfile):
        """A saved student: everything in StudentProfile plus the PG they live in."""
        current_pg_id: Optional[str] = None


# ---------------------------------------------------------
# Results
# ---------------------------------------------------------
class MatchScoreBreakdown(BaseModel):
        budget_score: float = Field(..., ge=0, le=100)
        distance_score: float = Field(..., ge=0, le=100)
        area_score: float = Field(default=0.0, ge=0, le=100)
        amenities_score: float = Field(..., ge=0, le=100)
        food_score: float = Field(..., ge=0, le=100)


class PGMatchResult(BaseModel):
        pg: PGProfile
        overall_score: float = Field(..., ge=0, le=100, description="Weighted sum of component scores")
        breakdown: MatchScoreBreakdown


class MatchRequest(BaseModel):
        student: StudentProfile
        # The server uses its own PG list, so this is optional.
        available_pgs: List[PGProfile] = Field(default_factory=list)


class MatchResponse(BaseModel):
        student_id: str
        matches: List[PGMatchResult] = Field(..., description="List of PGs sorted by overall_score descending")