import requests
from datetime import datetime
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
import os

def get_yankees_game_result():
    test_date = datetime(2025, 4, 8)  # Fixed test date
    date_str = test_date.strftime('%Y-%m-%d')

    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={date_str}&teamId=147"  # 147 = Yankees
    res = requests.get(url).json()

    if res["totalGames"] == 0:
        return None  # No game played

    game = res["dates"][0]["games"][0]
    status = game["status"]["detailedState"]
    is_final = "Final" in status

    if is_final:
        teams = game["teams"]
        yanks_score = teams["away"]["score"] if teams["away"]["team"]["id"] == 147 else teams["home"]["score"]
        opp_score = teams["home"]["score"] if teams["away"]["team"]["id"] == 147 else teams["away"]["score"]
        result = "loss" if yanks_score < opp_score else "win"

        return {
            "result": result,
            "opponent": teams["home"]["team"]["name"] if teams["away"]["team"]["id"] == 147 else teams["away"]["team"]["name"],
            "yankees_score": yanks_score,
            "opponent_score": opp_score,
            "game_date": game["gameDate"]
        }

    return None

def create_video_with_score(result):
    # Load the original video
    video_path = "/Users/dannyholman/Desktop/Yankees.Lose/da_jankees_lose.mp4"
    video_clip = VideoFileClip(video_path)

    # Extract the audio from the original video
    audio_clip = video_clip.audio

    # Format the game date
    game_date = datetime.strptime(result["game_date"], "%Y-%m-%dT%H:%M:%SZ").strftime("%B %d, %Y")

    # --- SCORE TEXT CLIP ---
    score_text = f"{result['yankees_score']} - {result['opponent_score']}"
    score_txt_clip = TextClip(
        score_text,
        fontsize=100,
        color='white',
        font="Comic-Sans-MS"  # Or try "Impact", "Futura", or any installed font
    )
    score_txt_clip = score_txt_clip.on_color(
        size=(score_txt_clip.w + 60, score_txt_clip.h + 30),
        color=(0, 0, 0),
        col_opacity=0.6
    )
    score_txt_clip = score_txt_clip.set_position(('center', 'center')).set_duration(video_clip.duration)

    # --- DATE TEXT CLIP ---
    date_text = f"Game Date: {game_date}"
    date_txt_clip = TextClip(
        date_text,
        fontsize=30,
        color='white',
        font="Arial"
    )
    date_txt_clip = date_txt_clip.on_color(
        size=(date_txt_clip.w + 40, date_txt_clip.h + 20),
        color=(0, 0, 0),
        col_opacity=0.6
    )
    date_txt_clip = date_txt_clip.set_position(('center', video_clip.h - 100)).set_duration(video_clip.duration)

    # Combine all layers
    final_clip = CompositeVideoClip([video_clip, score_txt_clip, date_txt_clip])

    # Set original audio
    final_clip = final_clip.set_audio(audio_clip)

    # Export final video
    output_path = "/Users/dannyholman/Desktop/Yankees.Lose/da_jankees_lose_with_score.mp4"
    final_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')

    return output_path

# Example usage
if __name__ == "__main__":
    result = get_yankees_game_result()
    if result and result["result"] == "loss":
        print(f"The Yankees lost to {result['opponent']} {result['opponent_score']}–{result['yankees_score']}")
        
        # Create video with score overlay and preserve audio
        video_with_score = create_video_with_score(result)
        print(f"Video created at: {video_with_score}")

        # Play video on macOS using the default video player
        os.system(f"open '{video_with_score}'")
    else:
        print("No Yankees loss detected.")
