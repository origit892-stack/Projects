"""Genre and world-archetype research: which districts and landmarks belong in which world.

This is deliberately a vocabulary, not a template. The archetype chooses the *palette of region
kinds* available to the planner; the Level Architect then composes a unique layout with seeded
placement, distinct names and a real route graph.
"""
from __future__ import annotations

ARCHETYPES: dict[str, dict] = {
    "temperate": {
        "label": "Verdant Frontier",
        "keywords": ["forest", "woods", "meadow", "valley", "nature", "יער", "כר", "טבע"],
        "kinds": ["forest", "highlands", "lake", "village", "ruins", "garden"],
        "pois": ["giant_tree", "waterfall", "village", "tower", "ruins", "lake", "gate", "monument"],
        "palette_bias": "field",
    },
    "tropical": {
        "label": "Emerald Reach",
        "keywords": ["jungle", "tropical", "island", "rainforest", "palm", "ג'ונגל", "טרופי", "אי"],
        "kinds": ["coast", "forest", "lake", "ruins", "marsh", "village"],
        "pois": ["dock", "temple", "waterfall", "giant_tree", "lake", "ruins", "village", "portal"],
        "palette_bias": "field_alt",
    },
    "volcanic": {
        "label": "Ashen Caldera",
        "keywords": ["volcano", "lava", "ash", "caldera", "הר געש", "לבה", "אפר"],
        "kinds": ["canyon", "highlands", "ruins", "marsh", "arena"],
        "pois": ["volcano", "ruins", "bridge", "arena", "tower", "gate", "monument"],
        "palette_bias": "structure",
    },
    "desert": {
        "label": "Sunscar Expanse",
        "keywords": ["desert", "dune", "sand", "canyon", "מדבר", "חול", "קניון"],
        "kinds": ["canyon", "highlands", "market", "ruins", "lake"],
        "pois": ["temple", "market", "ruins", "monument", "tower", "gate", "lake"],
        "palette_bias": "highlight",
    },
    "snow": {
        "label": "Frostbound Wilds",
        "keywords": ["snow", "ice", "frozen", "glacier", "winter", "שלג", "קרח", "חורף"],
        "kinds": ["highlands", "forest", "lake", "village", "ruins"],
        "pois": ["lighthouse", "village", "tower", "lake", "ruins", "gate", "monument"],
        "palette_bias": "highlight",
    },
    "urban": {
        "label": "Frontier Metropolis",
        "keywords": ["city", "town", "urban", "industrial", "street", "עיר", "כפר", "תעשייה"],
        "kinds": ["village", "market", "industrial", "arena", "observatory", "garden"],
        "pois": ["castle", "factory", "market", "arena", "tower", "monument", "gate"],
        "palette_bias": "structure",
    },
    "cosmic": {
        "label": "Stellar Observatory",
        "keywords": ["cosmic", "space", "galaxy", "nebula", "star", "celestial", "חלל", "קוסמי", "גלקסיה"],
        "kinds": ["observatory", "highlands", "ruins", "arena", "lake"],
        "pois": ["observatory", "portal", "monument", "tower", "arena", "ruins", "gate"],
        "palette_bias": "accent",
    },
    "swamp": {
        "label": "Mirewood Basin",
        "keywords": ["swamp", "marsh", "bog", "wetland", "ביצה", "ביצות"],
        "kinds": ["marsh", "forest", "lake", "village", "ruins"],
        "pois": ["giant_tree", "village", "ruins", "dock", "tower", "gate", "lake"],
        "palette_bias": "field_alt",
    },
}

DEFAULT_ARCHETYPE = "temperate"

REGION_NAMES: dict[str, list[str]] = {
    "hub": ["Wayfarer's Rest", "Central Plaza", "Crossroads", "The Hearth"],
    "forest": ["Whisperwood", "Elder Grove", "Mosslight Thicket", "Fernhollow", "Thornveil Woods"],
    "garden": ["Bloomstead", "Petal Terrace", "Sunwake Gardens", "Greenhouse Row"],
    "village": ["Pinewatch", "Hollowmere", "Stonebrook", "Amberfield", "Kingsdraft"],
    "market": ["Copper Row", "Spicewalk", "The Exchange", "Lantern Market"],
    "lake": ["Mirror Basin", "Stillwater Reach", "Aurora Lake", "Drowned Hollow"],
    "coast": ["Saltmarsh Point", "Gullwing Shore", "Tidebreak", "Coral Steps"],
    "marsh": ["Fenmire", "Reedwater", "The Sinking Fields", "Mistfen"],
    "highlands": ["Greycrag Rise", "Windscar Peaks", "Highwatch", "Stormcradle"],
    "canyon": ["Ember Rift", "Redstone Gorge", "The Long Cut", "Cinder Draw"],
    "ruins": ["Fallen Sanctum", "Old Concord", "The Broken Ring", "Ashen Library"],
    "arena": ["Trial Ring", "The Proving Grounds", "Stonecrown Arena"],
    "industrial": ["Ironworks", "Foundry Flats", "Steamrow", "The Kilns"],
    "observatory": ["Starfall Terrace", "Meridian Dome", "The Quiet Array"],
}

POI_NAMES: dict[str, list[str]] = {
    "tower": ["Beacon Spire", "Watchful Tower", "Signal Spire", "Old Lantern Tower"],
    "monument": ["World Pillar", "The First Stone", "Cairn of Names", "Standing Star"],
    "village": ["Hearthstone Hamlet", "Little Amber", "Bridgeford", "Millbottom"],
    "temple": ["Sunken Shrine", "Verdant Sanctum", "Temple of the Quiet Sun"],
    "ruins": ["Forgotten Gate", "Broken Citadel", "Hollow Archive", "The Fallen Arch"],
    "castle": ["Highkeep", "Crownwatch", "Royal Bastion"],
    "arena": ["Stone Ring", "The Trial Grounds", "Echo Arena"],
    "portal": ["Rift Nexus", "The Soft Rift", "Gateway of Tides"],
    "observatory": ["Meridian Observatory", "The Star Lens", "Nightglass Dome"],
    "factory": ["Old Works", "The Foundry", "Smokestack Yard"],
    "dock": ["Harbor Point", "Gullwing Pier", "Longwater Dock"],
    "lighthouse": ["Tideflame Light", "The Keeper's Lamp", "Saltlight"],
    "giant_tree": ["Elderwood", "The Mother Tree", "Crownroot"],
    "garden": ["Sunwake Garden", "The Glasshouse", "Petal Yard"],
    "gate": ["Traveler's Gate", "The Green Gate", "Broken Threshold"],
    "cave": ["Echo Caverns", "Crystal Hollow", "The Hush"],
    "volcano": ["Ember Crown", "Magma Observatory", "The Breathing Mountain"],
    "bridge": ["Skyspan Crossing", "Old Stone Bridge", "Rootbridge"],
    "lake": ["Mirror Lake", "Blue Basin", "Stillwater"],
    "waterfall": ["Silverfall", "Hidden Cascade", "The Long Drop"],
    "market": ["Lantern Market", "Copper Row Plaza", "The Open Exchange"],
}


def detect_archetype(idea: str) -> str:
    text = (idea or "").lower()
    best, best_score = DEFAULT_ARCHETYPE, 0
    for key, arch in ARCHETYPES.items():
        score = sum(1 for kw in arch["keywords"] if kw in text)
        if score > best_score:
            best, best_score = key, score
    return best


def archetype(key: str) -> dict:
    return dict(ARCHETYPES.get(key, ARCHETYPES[DEFAULT_ARCHETYPE]), key=key)


def region_plan(archetype_key: str, seed: int, region_count: int = 7) -> list[dict]:
    """Choose the ordered ring of districts: hub first, then distinct kinds."""
    import random
    arch = archetype(archetype_key)
    rng = random.Random(f"{seed}:regions")
    kinds = list(arch["kinds"])
    rng.shuffle(kinds)
    plan = [{"kind": "hub", "role": "hub"}]
    # Guarantee visual + functional variety: one elevated, one water, one settlement.
    for required in ("highlands", "lake", "village", "forest"):
        if required in kinds and len(plan) < region_count and all(p["kind"] != required for p in plan):
            plan.append({"kind": required, "role": "district"})
    for kind in kinds:
        if len(plan) >= region_count:
            break
        if all(p["kind"] != kind for p in plan):
            plan.append({"kind": kind, "role": "district"})
    if len(plan) < region_count:
        for kind in kinds:
            if len(plan) >= region_count:
                break
            plan.append({"kind": kind, "role": "district"})
    return plan


def poi_kinds_for(archetype_key: str, region_kind: str, region_index: int) -> list[str]:
    """Thematic POI selection per district, with a guaranteed landmark in the hub."""
    arch = archetype(archetype_key)
    pool = list(arch["pois"])
    special = {
        "hub": ["monument", "market", "portal"],
        "lake": ["lake", "dock", "bridge"],
        "coast": ["dock", "lighthouse", "bridge"],
        "highlands": ["tower", "observatory", "gate"],
        "canyon": ["bridge", "ruins", "volcano"],
        "ruins": ["ruins", "temple", "gate"],
        "village": ["village", "market", "tower"],
        "market": ["market", "gate", "monument"],
        "forest": ["giant_tree", "gate", "temple"],
        "garden": ["garden", "waterfall"],
        "marsh": ["dock", "ruins", "giant_tree"],
        "arena": ["arena", "monument"],
        "industrial": ["factory", "tower"],
        "observatory": ["observatory", "portal"],
    }
    first = special.get(region_kind, pool)
    picks = [first[region_index % len(first)]]
    for kind in pool:
        if len(picks) >= (2 if region_kind != "hub" else 3):
            break
        if kind not in picks:
            picks.append(kind)
    return picks
