"""Official Eastern Region Bus lines shown on the supplied network map."""

EASTERN_ROUTES = (
    {"code": "A2", "color": "#55A9E4", "origin": "محطة الدمام الرئيسية", "destination": "حي عبدالله فؤاد", "type": "two_way"},
    {"code": "A3", "color": "#72D98C", "origin": "الخبر الشمالية 1", "destination": "الدوحة الجنوبية 1", "type": "two_way"},
    {"code": "B2", "color": "#4597A8", "origin": "الخبر الشمالية 1", "destination": "الخبر الشمالية 1", "type": "loop"},
    {"code": "C31", "color": "#927D98", "origin": "محطة الدمام الرئيسية", "destination": "المحطة القطيف الرئيسية", "type": "two_way"},
    {"code": "C32", "color": "#87E8D3", "origin": "محطة الدمام الرئيسية", "destination": "المحطة القطيف الرئيسية", "type": "two_way"},
    {"code": "D4", "color": "#477D3F", "origin": "الواجهة البحرية بالدمام", "destination": "أحد 7", "type": "two_way"},
    {"code": "E5", "color": "#E5833B", "origin": "محطة الدمام الرئيسية", "destination": "الخبر الشمالية 1", "type": "two_way"},
    {"code": "F6", "color": "#6D369F", "origin": "محطة الدمام الرئيسية", "destination": "الخبر الشمالية 1", "type": "two_way"},
    {"code": "G7", "color": "#F9E575", "origin": "محطة الدمام الرئيسية", "destination": "محطة مطار الملك فهد", "type": "two_way"},
    {"code": "H8", "color": "#BB3B3A", "origin": "محطة الدمام الرئيسية", "destination": "المدينة الصناعية الثانية 2", "type": "two_way"},
    {"code": "K9", "color": "#B655D2", "origin": "محطة الدمام الرئيسية", "destination": "المنطقة الصناعية 2", "type": "two_way"},
)

ROUTES_BY_CODE = {route["code"]: route for route in EASTERN_ROUTES}


def route_allows(route: dict, origin: str, destination: str) -> bool:
    """Validate a trip against the termini printed in the official map key."""
    if route["type"] == "loop":
        return origin == route["origin"] and destination == route["destination"]
    return (origin, destination) in {
        (route["origin"], route["destination"]),
        (route["destination"], route["origin"]),
    }
