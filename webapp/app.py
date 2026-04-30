import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, render_template, jsonify
from data.mock_data import GAME_STATE, POLITICS_MENU, get_faction_total_forces, get_loyalty_color

app = Flask(__name__)

@app.route("/")
def index():
    oda_forces = get_faction_total_forces("oda")
    imagawa_forces = get_faction_total_forces("imagawa")
    return render_template(
        "index.html",
        state=GAME_STATE,
        oda_forces=oda_forces,
        imagawa_forces=imagawa_forces,
        active="map",
    )

@app.route("/retainers")
@app.route("/retainers/<faction_id>")
def retainers(faction_id="oda"):
    faction_retainers = [r for r in GAME_STATE["retainers"] if r["faction"] == faction_id]
    return render_template(
        "retainers.html",
        state=GAME_STATE,
        retainers=faction_retainers,
        faction_id=faction_id,
        get_loyalty_color=get_loyalty_color,
        active="retainers",
    )

@app.route("/politics")
def politics():
    return render_template(
        "politics.html",
        state=GAME_STATE,
        menu=POLITICS_MENU,
        active="politics",
    )

@app.route("/council")
def council():
    council_retainers = [r for r in GAME_STATE["retainers"]
                         if r["faction"] == "oda" and r["rank"] in ("宿老", "家老")]
    return render_template(
        "council.html",
        state=GAME_STATE,
        council_retainers=council_retainers,
        active="council",
    )

@app.route("/api/state")
def api_state():
    return jsonify(GAME_STATE)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
