"""Token cost logic — how much each type of API call costs."""

# For now every call costs 1 token (as per the assignment spec).
# This file exists so you can extend costs per endpoint later if needed.

COST_DEFAULT = 1
COST_SPORT_QUERY = 1  # GET /sport with filters
COST_ATHLETE = 1
COST_COUNTRY = 1

# TODO: if you want tiered pricing (e.g. PNG charts cost more), add it here
COST_PNG_CHART = 5  # bonus feature
