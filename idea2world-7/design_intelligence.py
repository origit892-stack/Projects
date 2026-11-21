"""Design intelligence layer: translates game ideas into genre-aware playable design briefs.
Inspired by publicly observable design patterns; never copies proprietary assets or layouts."""
import re

GAME_PATTERNS = {
    "throw_collect_sim": {
        "matches": ["throw food", "throw_food", "animals", "animal", "feed", "attract", "collect pets", "חיות", "להאכיל", "לזרוק אוכל"],
        "inspiration": ["Throw Food for Animals", "Grow a Garden", "Pet Simulator-style collection loops"],
        "loop": ["Earn or obtain a resource", "Aim / throw / perform a short skill action", "Reach a new zone or attract a rarer creature", "Collect and display the creature", "Earn passive rewards and upgrade range / power"],
        "systems": ["skill-based throw arc", "rarity-weighted creature attraction", "collection book", "habitat display", "upgrade stations", "zone gates", "daily discoveries"],
        "audience": "Broad casual Roblox audience; collection, discovery and satisfying progression; mobile-first.",
        "map": "Readable hub with a clear throwing lane, visible distant targets, distinct habitat islands, safe return path and one obvious next unlock.",
        "ui": ["large throw / action button", "power and distance meter", "currency and next-zone goal", "creature collection grid", "upgrade cards", "simple rarity reveal"],
        "session": "A 2–5 minute first success, then repeatable 7–12 minute upgrade and collection sessions.",
    },
    "collection_garden": {
        "matches": ["garden", "grow", "plant", "farm", "גינה", "לגדל", "חקלאות"],
        "inspiration": ["Grow a Garden", "Adopt Me! social collection", "cozy tycoon patterns"],
        "loop": ["Plant or place", "Wait / tend / interact", "Harvest a visible reward", "Expand and decorate", "Trade or show progress"],
        "systems": ["growth stages", "rarity mutations", "plot ownership", "weather events", "collection journal", "social showcase"],
        "audience": "Casual/cozy players and social groups; low-pressure play and expressive ownership.",
        "map": "Personal plots around a shared social plaza, event garden and clear expansion rings.",
        "ui": ["plot status", "seed / inventory bar", "harvest feedback", "shop and collection", "event timer"],
        "session": "Short check-ins plus longer decorating and social sessions.",
    },
    "survival_exploration": {
        "matches": ["survival", "forest", "night", "monster", "survive", "יער", "לשרוד", "מפלצת"],
        "inspiration": ["99 Nights in the Forest", "The Strongest Battlegrounds-style readable combat telegraphs"],
        "loop": ["Explore for resources", "Prepare a safe base", "Survive an escalating threat", "Unlock a deeper region", "Return with new tools"],
        "systems": ["day-night cycle", "resource nodes", "safe hub", "threat escalation", "landmark discovery", "co-op rescue"],
        "audience": "Co-op explorers who enjoy tension, mastery and shared goals.",
        "map": "Strong central safe zone, readable radial routes, landmarks visible at distance, escalating danger bands and alternate shortcuts.",
        "ui": ["compact objective", "health / stamina", "day-night clock", "resource quick slots", "team status"],
        "session": "Clear 10–20 minute expeditions with meaningful checkpoints.",
    },
    "social_roleplay": {
        "matches": ["roleplay", "city", "school", "house", "town", "עיר", "בית ספר", "תפקידים"],
        "inspiration": ["Brookhaven RP", "Adopt Me! social spaces"],
        "loop": ["Choose an identity or home", "Meet players", "Create a shared story", "Personalize possessions", "Return for events"],
        "systems": ["homes", "social hubs", "vehicles / traversal", "emotes", "jobs / activities", "themed events"],
        "audience": "Social and imaginative players; high value on self-expression and friend play.",
        "map": "Compact walkable districts, memorable silhouettes, landmarks as meeting points and many safe interaction spaces.",
        "ui": ["minimal HUD", "quick emotes", "home / vehicle controls", "map / location labels", "avatar customization"],
        "session": "Open-ended; reduce friction to join friends and start roleplay immediately.",
    },
    "competitive_action": {
        "matches": ["battle", "arena", "pvp", "fight", "shooter", "קרב", "זירה", "לחימה"],
        "inspiration": ["RIVALS", "The Strongest Battlegrounds", "Murder Mystery 2 round readability"],
        "loop": ["Enter a fast readable match", "Master a small set of abilities", "Win / improve", "Unlock expression cosmetics", "Queue with friends"],
        "systems": ["spawn safety", "line-of-sight lanes", "cover", "round flow", "spectator state", "skill matchmaking hooks"],
        "audience": "Competitive players; fairness, responsive controls and legible combat are critical.",
        "map": "Symmetric or intentionally balanced routes, distinct combat lanes, clear spawn protection and no visual clutter in sightlines.",
        "ui": ["health / ability cooldowns", "round timer", "score / objective", "team indicators", "spectator panel"],
        "session": "Short repeatable rounds with low downtime.",
    },
}

STYLE_PROFILES = {
 "stud": {"label":"Classic Roblox Stud", "geometry":"chunky modular forms, visible stud language, simple readable silhouettes", "materials":"matte plastic, restrained metal, clean color blocks", "lighting":"bright readable daylight, soft ambient shadows", "ui":"bold playful panels, thick outlines, large icons", "avoid":"tiny noisy details, photoreal textures"},
 "stylized_low_poly": {"label":"Stylized Low Poly", "geometry":"clean faceted silhouettes, layered shapes, intentional negative space", "materials":"matte surfaces, selective roughness and emissive accents", "lighting":"cinematic but readable, controlled fog and color grade", "ui":"rounded cards, strong hierarchy, icon-first"},
 "fantasy_cinematic": {"label":"Fantasy Cinematic", "geometry":"monumental arches, layered ruins, organic silhouettes", "materials":"stone, aged metal, crystal, emissive runes", "lighting":"warm key light, cool fill, volumetric-feel fog", "ui":"ornamental but restrained, high-contrast labels"},
 "cosmic_art": {"label":"Cosmic Art Direction", "geometry":"floating masses, orbital rings, asymmetric crystal forms", "materials":"dark stone, translucent glass, iridescent metal, emissive cores", "lighting":"deep blue-violet ambience, bright focal glow, controlled bloom", "ui":"deep-space panels, constellation motifs, bright cyan/violet accent"},
 "sci_fi_clean": {"label":"Clean Sci-Fi", "geometry":"modular panels, pylons, rings, clean engineered proportions", "materials":"brushed metal, ceramic, glass, emissive strips", "lighting":"cool key lights, high readability, limited neon", "ui":"compact telemetry, crisp grids, restrained motion"},
}

def analyze_idea(idea, requested_style="auto"):
    text=(idea or "").lower()
    chosen="general_adventure"; best=0
    for key,p in GAME_PATTERNS.items():
        score=sum(1 for term in p["matches"] if term in text)
        if score>best: chosen,best=key,score
    if chosen=="general_adventure":
        p={"inspiration":["Roblox discovery and exploration experiences"],"loop":["Discover a landmark","Complete a short challenge","Earn a reward","Unlock a new route","Personalize progress"],"systems":["landmark discovery","quests","collectibles","unlockable zones","social showcase"],"audience":"Broad Roblox audience; tune challenge and visual density to the specific concept.","map":"A clear spawn hub, one strong focal landmark, 3–5 distinct districts and visible progression gates.","ui":["simple objective", "progress / currency", "inventory", "map / next unlock"],"session":"Immediate first reward, then short and long-term goals."}
    else: p=GAME_PATTERNS[chosen]
    if requested_style in STYLE_PROFILES:
        style=requested_style
    else:
        style="stylized_low_poly"
        if any(k in text for k in ["stud","studs","classic roblox"]): style="stud"
        elif any(k in text for k in ["cosmic","space","galaxy","nebula","חלל","קוסמי"]): style="cosmic_art"
        elif any(k in text for k in ["sci-fi","scifi","futuristic","עתידני"]): style="sci_fi_clean"
        elif any(k in text for k in ["fantasy","magic","enchanted","פנטזיה","קסום"]): style="fantasy_cinematic"
    return {"genre_profile":chosen,"research_inspirations":p["inspiration"],"core_loop":p["loop"],"gameplay_systems":p["systems"],"target_audience":p["audience"],"map_design_requirements":p["map"],"ui_ux_requirements":p["ui"],"session_design":p["session"],"art_direction":STYLE_PROFILES[style],"design_principles":["Get to the first satisfying action quickly","Make the next goal visible in-world and in UI","Use a small number of distinct visual signals for rarity and importance","Design mobile-first touch targets and keep the central play area unobstructed","Keep visual effects subordinate to gameplay readability","Create short-, medium- and long-term goals without forcing purchases"]}
