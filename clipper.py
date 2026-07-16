import os
from config import OUTPUT_DIR

# Robust MoviePy import fallback structure to support both v1.x and v2.x releases
try:
    from moviepy.editor import VideoFileClip
except ImportError:
    try:
        from moviepy.video.io.VideoFileClip import VideoFileClip
    except ImportError as e:
        print("❌ Critical: MoviePy is not installed correctly in this virtual environment.")
        raise e

def crop_to_vertical(clip):
    """
    Crops a standard 16:9 widescreen video clip to a 9:16 vertical clip
    by centering the frame.
    """
    w, h = clip.size
    # Calculate the target width for a 9:16 aspect ratio based on the height
    target_width = int(h * (9 / 16))
    
    # Calculate the starting X coordinate to center the crop
    x1 = (w - target_width) // 2
    x2 = x1 + target_width
    
    # Crop the clip dynamically
    return clip.crop(x1=x1, y1=0, x2=x2, y2=h)

def create_video_clip(video_path, start_time, duration=30):
    """
    Cuts a video clip from video_path starting at start_time for a given duration,
    crops it to vertical 9:16, and saves it in the output directory.
    """
    print(f"🎬 Slicing video from {video_path}...")
    print(f"⏱️  Start: {start_time}s | Duration: {duration}s")
    
    if not os.path.exists(video_path):
        print(f"❌ Error: Video source not found at {video_path}")
        return None
        
    output_filename = f"clip_{int(start_time)}s.mp4"
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    
    try:
        # Load the raw video file
        with VideoFileClip(video_path) as video:
            # Check if duration exceeds video length
            end_time = min(start_time + duration, video.duration)
            
            # Cut the specific timeframe
            sub_clip = video.subclip(start_time, end_time)
            
            # Convert widescreen to mobile vertical layout
            vertical_clip = crop_to_vertical(sub_clip)
            
            # Write the file down to your disk
            print(f"💾 Exporting vertical MP4 to {output_path}...")
            vertical_clip.write_videofile(
                output_path,
                codec="libx264",
                audio_codec="aac",
                temp_audiofile="temp-audio.m4a",
                remove_temp=True,
                fps=24  # Standard cinematic 24fps
            )
            
        print(f"✅ Video clip successfully exported: {output_filename}")
        return output_path
        
    except Exception as e:
        print(f"❌ Video clipping failed: {e}")
        return None

if __name__ == "__main__":
    # Quick debug test - We can test cut 5 seconds from our video
    # Replace 'podcast.mp4' with a path to your video if you want to run a quick test run!
    test_video = "output/temp_uploaded_video.mp4"
    if os.path.exists(test_video):
        create_video_clip(test_video, start_time=5, duration=10)