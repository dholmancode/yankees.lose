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
        }

    return None

def create_video_with_score(result):
    # Load the original video
    video_path = "/Users/dannyholman/Desktop/Yankees.Lose/da_jankees_lose.mp4"
    video_clip = VideoFileClip(video_path)

    # Extract the audio from the original video
    audio_clip = video_clip.audio

    # Create text clip with score
    score_text = f"Da Jankees Lose! {result['yankees_score']} - {result['opponent_score']}"
    txt_clip = TextClip(score_text, fontsize=50, color='white', bg_color='none', font="Arial", size=video_clip.size)
    txt_clip = txt_clip.set_position('center').set_duration(video_clip.duration)

    # Combine the video and text
    final_clip = CompositeVideoClip([video_clip, txt_clip])

    # Set the audio back to the video
    final_clip = final_clip.set_audio(audio_clip)

    # Write the result to a new file
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
