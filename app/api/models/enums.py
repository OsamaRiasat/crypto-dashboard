import enum

class Intent(enum.Enum):
    growth = "growth"
    tax = "tax"
    learning = "learning"
    fun = "fun"

class ExperienceLevel(enum.Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"

class Layer(enum.Enum):
    Collateral = "Collateral"
    Growth = "Growth"
    Wildcard = "Wildcard"

class AllocationPreset(enum.Enum):
    Conservative = "Conservative"
    Moderate = "Moderate"
    Aggressive = "Aggressive"
    YOLO = "YOLO"

class RebalanceFrequency(enum.Enum):
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"
    quarterly = "quarterly"

class ContributionFrequency(enum.Enum):
    weekly = "weekly"
    biweekly = "biweekly"
    monthly = "monthly"
    quarterly = "quarterly"

class ConnectionMethod(enum.Enum):
    email = "email"
    api = "api"
    csv = "csv"
