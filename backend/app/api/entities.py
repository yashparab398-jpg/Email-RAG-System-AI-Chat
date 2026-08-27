from fastapi import APIRouter

from app.api.hubs import hubs as get_hubs


router = APIRouter(
    prefix="/insights",
    tags=["Insights"]
)


# =========================================================
# CACHE
# =========================================================

_cached_entities = None


# =========================================================
# CONFIGURATION
# =========================================================

TOP_ENTITY_COUNT = 20


# =========================================================
# ENTITY CALCULATION
# =========================================================

def calculate_entities():

    print(
        "[ENTITIES] Calculating entities...",
        flush=True
    )

    hub_data = get_hubs()

    if not isinstance(hub_data, dict):

        print(
            "[ENTITIES] Invalid hub response.",
            flush=True
        )

        return []

    communication_hubs = hub_data.get(
        "communication_hubs",
        []
    )

    if not isinstance(
        communication_hubs,
        list
    ):

        print(
            "[ENTITIES] communication_hubs is not a list.",
            flush=True
        )

        return []

    entities = []

    for item in communication_hubs:

        if (
            isinstance(item, (list, tuple))
            and len(item) >= 2
        ):

            entity = str(
                item[0]
            ).strip()

            try:

                count = int(
                    item[1]
                )

            except (
                TypeError,
                ValueError
            ):

                count = 0

            if entity and count > 0:

                entities.append(
                    [
                        entity,
                        count
                    ]
                )

    entities = entities[
        :TOP_ENTITY_COUNT
    ]

    print(
        f"[ENTITIES] Found {len(entities)} entities.",
        flush=True
    )

    if entities:

        print(
            f"[ENTITIES] Top entity: "
            f"{entities[0][0]} "
            f"({entities[0][1]})",
            flush=True
        )

    return entities


# =========================================================
# API
# =========================================================

@router.get("/entities")
def entities():

    global _cached_entities

    try:

        # -------------------------------------------------
        # RETURN CACHE ONLY IF IT CONTAINS REAL DATA
        # -------------------------------------------------

        if _cached_entities:

            return {
                "top_entities":
                    _cached_entities
            }

        # -------------------------------------------------
        # CALCULATE
        # -------------------------------------------------

        calculated = calculate_entities()

        # -------------------------------------------------
        # IMPORTANT:
        #
        # Never cache an empty result.
        # This allows a temporary MongoDB/startup failure
        # to recover automatically.
        # -------------------------------------------------

        if calculated:

            _cached_entities = calculated

        return {
            "top_entities":
                calculated
        }

    except Exception as error:

        print(
            "[ENTITIES] ERROR:",
            repr(error),
            flush=True
        )

        return {
            "top_entities": [],
            "error":
                "Entity data is temporarily unavailable."
        }