from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, ImageClip
from PIL import Image
import numpy as np
import os
from datetime import datetime, timedelta
import requests
from instagrapi import Client
from dotenv import load_dotenv
from zoneinfo import ZoneInfo

# Load environment variables
load_dotenv()
IG_USERNAME = os.getenv("IG_USERNAME")
IG_PASSWORD = os.getenv("IG_PASSWORD")

# Team logo map
team_logo_map = {
    "Boston Red Sox": "boston.png",
    "Detroit Tigers": "detroit.png",
    "Toronto Blue Jays": "toronto.png",
    "Tampa Bay Rays": "tampa_bay.png",
    "Baltimore Orioles": "baltimore.png",
    "New York Mets": "new_york.png",
    "Chicago White Sox": "chicago_white.png",
    "Chicago Cubs": "chicago_cubs.png",
    "Los Angeles Dodgers": "los_angeles.png",
    "San Francisco Giants": "san_francisco.png",
    "Houston Astros": "houston.png",
    "Cleveland Guardians": "cleveland.png",
    "New York Yankees": "yankees.png",
    "Los Angeles Angels": "los_angeles_angels.png",
    "Miami Marlins": "miami.png",
    "Milwaukee Brewers": "milwaukee.png",
    "Minnesota Twins": "minnesota.png",
    "Kansas City Royals": "kansas_city.png",
    "Arizona Diamondbacks": "arizona.png",
    "Atlanta Braves": "atlanta.png",
    "Philadelphia Phillies": "philadelphia.png",
    "Seattle Mariners": "seattle.png",
    "St. Louis Cardinals": "st_louis.png",
    "Oakland Athletics": "oakland.png",
    "Washington Nationals": "washington.png",
    "Pittsburgh Pirates": "pittsburgh.png",
    "San Diego Padres": "san_diego.png",
    "Texas Rangers": "texas.png",
    "Cincinnati Reds": "cincinnati.png",
    "Colorado Rockies": "colorado.png"
}

# Resize logo with Pillow
def resize_logo(image_path, height):
    img = Image.open(image_path).convert("RGBA")
    aspect_ratio = img.width / img.height
    new_width = int(height * aspect_ratio)
    resized_img = img.resize((new_width, height), Image.Resampling.LANCZOS)
    return np.array(resized_img)

# Fetch game result
def fetch_yankees_game_result(game_date_str):
    base_url = "https://statsapi.mlb.com/api/v1/schedule"
    params = {"sportId": 1, "date": game_date_str, "teamId": 147}
    response = requests.get(base_url, params=params)
    data = response.json()

    try:
        game = data["dates"][0]["games"][0]
        game_id = game["gamePk"]
        boxscore_url = f"https://statsapi.mlb.com/api/v1/game/{game_id}/boxscore"
        boxscore_data = requests.get(boxscore_url).json()

        teams = boxscore_data["teams"]
        yankees = teams["away"] if teams["away"]["team"]["id"] == 147 else teams["home"]
        opponent = teams["home"] if yankees == teams["away"] else teams["away"]

        return {
            "result": "loss" if yankees["teamStats"]["batting"]["runs"] < opponent["teamStats"]["batting"]["runs"] else "win",
            "opponent": opponent["team"]["name"],
            "yankees_score": yankees["teamStats"]["batting"]["runs"],
            "opponent_score": opponent["teamStats"]["batting"]["runs"],
            "game_date": game["gameDate"]
        }
    except (IndexError, KeyError):
        print("⚠️ Could not find Yankees game for that date.")
        return None

# Create video with score overlay
def create_video_with_score(result):
    video_path = "/Users/dannyholman/Desktop/Yankees.Lose/da_jankees_lose.mp4"
    video_clip = VideoFileClip(video_path)
    audio_clip = video_clip.audio

    utc_dt = datetime.strptime(result["game_date"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=ZoneInfo("UTC"))
    local_dt = utc_dt.astimezone(ZoneInfo("America/New_York"))
    game_date = local_dt.strftime("%B %d, %Y")

    score_text = f"{result['yankees_score']} - {result['opponent_score']}"

    # Score text
    raw_score_txt = TextClip(score_text,
                             fontsize=60,
                             color='white',
                             font='Impact',
                             stroke_color='black',
                             stroke_width=1)

    score_txt_clip = raw_score_txt.on_color(
        size=(raw_score_txt.w + 80, raw_score_txt.h + 40),
        color=(0, 0, 0),
        col_opacity=0.7
    ).set_position(('center', 'center')).set_duration(video_clip.duration)

    # Date text
    raw_date_txt = TextClip(game_date,
                            fontsize=30,
                            color='white',
                            font='Impact',
                            stroke_color='black',
                            stroke_width=1)

    date_txt_clip = raw_date_txt.on_color(
        size=(raw_date_txt.w + 40, raw_date_txt.h + 10),
        color=(0, 0, 0),
        col_opacity=0.65
    ).set_position(('center', video_clip.h - 100)).set_duration(video_clip.duration)

    # Logos
    yankees_logo_path = "/Users/dannyholman/Desktop/Yankees.Lose/logos/yankees.png"
    yankees_logo_resized = resize_logo(yankees_logo_path, 80)
    yankees_logo = ImageClip(yankees_logo_resized).set_duration(video_clip.duration).set_position((90, 'center'))

    opponent_logo_file = team_logo_map.get(result["opponent"], "default_logo.png")
    opponent_logo_path = f"/Users/dannyholman/Desktop/Yankees.Lose/logos/{opponent_logo_file}"
    if not os.path.exists(opponent_logo_path):
        opponent_logo_path = "/Users/dannyholman/Desktop/Yankees.Lose/logos/default_logo.png"

    opponent_logo_resized = resize_logo(opponent_logo_path, 80)
    opponent_logo = ImageClip(opponent_logo_resized).set_duration(video_clip.duration).set_position((video_clip.w - 190, 'center'))

    # Combine everything
    final_clip = CompositeVideoClip([
        video_clip,
        score_txt_clip,
        date_txt_clip,
        yankees_logo,
        opponent_logo
    ]).set_audio(audio_clip)

    output_path = "/Users/dannyholman/Desktop/Yankees.Lose/da_jankees_lose_with_score.mp4"
    final_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')
    return output_path

# Upload video to Instagram
def upload_to_instagram(video_path, caption="Daaa Yankees Lose."):
    cl = Client()
    session_path = "insta_session.json"

    if os.path.exists(session_path):
        cl.load_settings(session_path)

    try:
        cl.login(IG_USERNAME, IG_PASSWORD)
    except Exception:
        cl.relogin(IG_USERNAME, IG_PASSWORD)

    cl.dump_settings(session_path)

    cl.clip_upload(
        video_path,
        caption,
        extra_data={"thumbnail": video_path}
    )
    print("✅ Uploaded to Instagram!")

# Main logic
if __name__ == "__main__":
    start_date = datetime(2025, 5, 5)
    today = datetime.now()

    current_date = start_date
    while current_date <= today:
        target_date = current_date.strftime("%Y-%m-%d")
        print(f"📅 Checking game for {target_date}...")
        result = fetch_yankees_game_result(target_date)

        if result and result["result"] == "loss":
            print(f"💀 The Yankees lost to {result['opponent']} {result['opponent_score']}–{result['yankees_score']} on {target_date}")
            video_with_score = create_video_with_score(result)
            print(f"🎬 Video created at: {video_with_score}")
            upload_to_instagram(
                video_with_score,
                caption=f"Daaa Yankees Lose to the {result['opponent']} \nFinal Score: {result['yankees_score']}–{result['opponent_score']}"
            )
        else:
            print("No Yankees loss detected or no game found.")

        current_date += timedelta(days=1)
