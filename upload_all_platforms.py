"""
Lingexa Etymology - Unified Social Media Upload Script
Uploads word origin videos to all connected platforms
"""

import os, sys, json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

upload_dir = Path(__file__).parent / "upload"
if upload_dir.exists() and str(upload_dir) not in sys.path:
    sys.path.insert(0, str(upload_dir))

upload_to_facebook = None
upload_to_instagram = None
upload_to_youtube = None

try:
    from upload_facebook import upload_to_facebook as fb_upload
    upload_to_facebook = fb_upload
except ImportError as e:
    print(f"[!] Facebook upload module not available: {e}")

try:
    from upload_instagram import upload_to_instagram as ig_upload
    upload_to_instagram = ig_upload
except ImportError as e:
    print(f"[!] Instagram upload module not available: {e}")

try:
    from upload_to_youtube import upload_to_youtube as yt_upload
    upload_to_youtube = yt_upload
except ImportError as e:
    print(f"[!] YouTube upload module not available: {e}")

CHANNEL_NAME = "Lingexa Etymology"

def get_latest_reel():
    video_dir = Path("output/video")
    if not video_dir.exists():
        print("No output/video directory found")
        return None
    reels = list(video_dir.glob("*/final_reel.mp4"))
    if not reels:
        print("No reels found in output/video directory")
        return None
    latest = max(reels, key=lambda p: p.stat().st_mtime)
    metadata_file = latest.parent / "metadata.json"
    metadata = {}
    if metadata_file.exists():
        with open(metadata_file, "r", encoding="utf-8") as f:
            metadata = json.load(f)
    words_data = metadata.get("words", [])
    all_words = [w.get("word", "") for w in words_data]
    return {
        "video_path": str(latest),
        "metadata": metadata,
        "words": words_data,
        "all_words": all_words,
        "word": all_words[0] if all_words else "Etymology",
    }

def generate_caption(reel_data, platform="facebook"):
    words = reel_data.get("words", [])
    all_words = reel_data.get("all_words", [])

    if not words:
        return f"Discover word origins with {CHANNEL_NAME}! #{CHANNEL_NAME.replace(' ', '')} #etymology #wordorigins"

    if platform == "facebook":
        lines = [
            f"📜 Discover the Origins of 5 English Words!",
            f"",
            f"Today's Etymology Lesson:",
            f"",
        ]
        for i, w in enumerate(words, 1):
            word = w.get("word", "")
            pos = w.get("part_of_speech", "")
            definition = w.get("definition", "")
            origin = w.get("origin", "")
            language = w.get("language", "")
            century = w.get("century", "")

            lines.append(f"{i}. {word.upper()} ({pos})")
            lines.append(f"   Definition: {definition}")
            lines.append(f"   Origin: {origin[:100]}{'...' if len(origin) > 100 else ''}")
            if language:
                lines.append(f"   From: {language} {f'| {century}' if century else ''}")
            lines.append(f"")

        lines.extend([
            f"💡 Save this post and discover more word origins!",
            f"👍 Like if you learned something new!",
            f"🔔 Follow {CHANNEL_NAME} for daily etymology lessons!",
            f"",
            f"#{CHANNEL_NAME.replace(' ', '')} #etymology #wordorigins #english #linguistics #history #language #wordhistory #learnenglish #vocabulary #wordfacts",
        ])

    elif platform == "instagram":
        lines = [
            f"📜 5 Word Origins to Learn Today!",
            f"",
        ]
        for i, w in enumerate(words, 1):
            word = w.get("word", "")
            pos = w.get("part_of_speech", "")
            definition = w.get("definition", "")
            language = w.get("language", "")
            lines.append(f"{i}. {word.upper()} ({pos})")
            lines.append(f"   {definition} — from {language}")
            lines.append(f"")

        lines.extend([
            f"💡 Save & discover more!",
            f"🔔 Follow @{CHANNEL_NAME.replace(' ', '').lower()} for daily word origins!",
            f"",
            f"#{CHANNEL_NAME.replace(' ', '')} #etymology #wordorigins #linguistics",
        ])

    else:
        lines = [
            f"Discover 5 word origins with {CHANNEL_NAME}!",
            f"",
        ]
        for i, w in enumerate(words[:3], 1):
            word = w.get("word", "")
            definition = w.get("definition", "")
            language = w.get("language", "")
            lines.append(f"{i}. {word.upper()} - {definition} (from {language})")

        lines.extend([
            f"",
            f"#{CHANNEL_NAME.replace(' ', '')} #etymology #wordorigins",
        ])

    return "\n".join(lines)

def upload_to_all_platforms(video_path, caption, word, reel_data=None):
    results = {
        "timestamp": datetime.now().isoformat(),
        "word": word,
        "video": video_path,
        "uploads": {},
        "platforms_attempted": [],
        "platforms_successful": [],
        "platforms_skipped": [],
        "platforms_failed": []
    }

    print("\n" + "="*80)
    print(f"{CHANNEL_NAME.upper()} - MULTI-PLATFORM UPLOAD")
    print("="*80)
    print(f"Video: {video_path}")
    print(f"Word: {word}")
    print(f"Caption length: {len(caption)} characters")
    print("="*80)

    if not Path(video_path).exists():
        print(f"Video file not found: {video_path}")
        return results

    platforms = [
        ("facebook", upload_to_facebook, "Facebook"),
        ("instagram", upload_to_instagram, "Instagram"),
        ("youtube", upload_to_youtube, "YouTube"),
    ]

    for platform_name, upload_func, display_name in platforms:
        print(f"\n{display_name} UPLOAD...")
        results["platforms_attempted"].append(platform_name)

        if upload_func:
            try:
                upload_result = None
                if platform_name == "facebook":
                    upload_result = upload_func(
                        video_path=video_path,
                        description=caption,
                        title=f"Word Origins: {word}"
                    )
                elif platform_name == "instagram":
                    upload_result = upload_func(
                        video_path=video_path,
                        caption=caption,
                        is_story=False
                    )
                elif platform_name == "youtube":
                    from upload_to_youtube import generate_video_metadata
                    words_data = reel_data.get("words", [])
                    yt_title, yt_description, yt_tags = generate_video_metadata(words_data, reel_data)
                    upload_result = upload_func(
                        video_path=video_path,
                        title=yt_title,
                        description=yt_description,
                        tags=yt_tags,
                        category_id='27'
                    )

                if upload_result:
                    results["uploads"][platform_name] = upload_result
                    results["platforms_successful"].append(platform_name)
                    print(f"  {display_name} upload successful")
                else:
                    results["uploads"][platform_name] = {"status": "failed", "error": "Upload function returned None"}
                    results["platforms_failed"].append(platform_name)
                    print(f"  {display_name} upload failed: No result returned")

            except Exception as e:
                error_msg = str(e)
                results["uploads"][platform_name] = {"status": "failed", "error": error_msg}
                results["platforms_failed"].append(platform_name)
                print(f"  {display_name} upload failed: {error_msg}")
        else:
            print(f"  {display_name} upload skipped (module not available)")
            results["uploads"][platform_name] = {"status": "skipped", "reason": "Module not available"}
            results["platforms_skipped"].append(platform_name)

    print("\n" + "="*80)
    print("UPLOAD SUMMARY")
    print("="*80)
    print(f"\nSuccessful: {len(results['platforms_successful'])}")
    print(f"Failed: {len(results['platforms_failed'])}")
    print(f"Skipped: {len(results['platforms_skipped'])}")

    results_file = Path("output") / f"upload_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    results_file.parent.mkdir(exist_ok=True)
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved: {results_file}")
    print("="*80)
    return results


PUBLISHED_LOG = "published_videos.json"

def get_published():
    if os.path.exists(PUBLISHED_LOG):
        with open(PUBLISHED_LOG, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return []
    return []

def save_published(word, video_name):
    published = get_published()
    published.append({"word": word, "video": video_name, "time": datetime.now().isoformat()})
    with open(PUBLISHED_LOG, "w", encoding="utf-8") as f:
        json.dump(published, f, indent=2)


def main():
    reel = get_latest_reel()
    if not reel:
        print("No reel found!")
        sys.exit(1)

    word = reel['word']
    published = get_published()
    published_words = [p.get("word", "") for p in published]

    if word in published_words:
        print("Word '" + word + "' already published! Skipping upload.")
        return

    caption = generate_caption(reel, platform="facebook")
    print("Caption (" + str(len(caption)) + " chars)")
    print(caption[:500])
    result = upload_to_all_platforms(reel['video_path'], caption, word, reel)
    if result.get("platforms_successful"):
        save_published(word, reel['video_path'])
        print("Published word: " + word)

if __name__ == "__main__":
    main()
