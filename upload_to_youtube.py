"""
YouTube Upload Script - Lingexa Etymology
Custom metadata for word origin videos
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

load_dotenv()

CHANNEL_NAME = "Lingexa Etymology"

def get_authenticated_service():
    client_id = (os.getenv('YOUTUBE_CLIENT_ID') or os.getenv('YT_CLIENT_ID', '')).strip()
    client_secret = (os.getenv('YOUTUBE_CLIENT_SECRET') or os.getenv('YT_CLIENT_SECRET', '')).strip()
    refresh_token = (os.getenv('YOUTUBE_REFRESH_TOKEN') or os.getenv('YT_REFRESH_TOKEN', '')).strip()

    def mask(s): return f"{s[:4]}...{s[-4:]}" if s and len(s) > 8 else "MISSING"
    print(f"[youtube] Client ID: {mask(client_id)}")

    if not all([client_id, client_secret, refresh_token]):
        raise ValueError("Missing credentials! Set YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN")

    creds = Credentials(
        None, refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id, client_secret=client_secret,
        scopes=["https://www.googleapis.com/auth/youtube"]
    )

    try:
        creds.refresh(Request())
    except Exception as e:
        if "invalid_grant" in str(e).lower():
            print("\n[youtube] AUTH ERROR: Refresh token has EXPIRED or been REVOKED.")
        raise

    return build("youtube", "v3", credentials=creds)

def generate_video_metadata(words_data: list, reel_data: dict = None):
    if not words_data:
        return f"Word Origins - {CHANNEL_NAME}", f"Discover word origins with {CHANNEL_NAME}!", ["etymology", "word origins", CHANNEL_NAME.replace(' ', '')]

    first_words = [w.get("word", "") for w in words_data[:3]]
    words_count = len(words_data)

    title = f"Where Do These {words_count} Words Come From? {', '.join(first_words)} | Etymology"

    description_lines = [
        f"📜 Discover the origins of {words_count} English words with {CHANNEL_NAME}!",
        f"",
        f"=== TODAY'S WORDS ===",
        f"",
    ]

    for i, w in enumerate(words_data, 1):
        word = w.get("word", "")
        pos = w.get("part_of_speech", "")
        definition = w.get("definition", "")
        origin = w.get("origin", "")
        language = w.get("language", "")
        century = w.get("century", "")

        description_lines.append(f"{i}. {word.upper()} ({pos})")
        description_lines.append(f"   Definition: {definition}")
        if origin:
            description_lines.append(f"   Origin: {origin}")
        if language or century:
            desc_parts = []
            if language: desc_parts.append(f"Language: {language}")
            if century: desc_parts.append(f"Entered English: {century}")
            description_lines.append(f"   {' | '.join(desc_parts)}")
        description_lines.append(f"")

    description_lines.extend([
        f"=== ABOUT {CHANNEL_NAME.upper()} ===",
        f"",
        f"Discover the fascinating origins of English words every day!",
        f"🔔 Subscribe for daily etymology lessons!",
        f"",
        f"=== HASHTAGS ===",
        f"#{CHANNEL_NAME.replace(' ', '')} #Etymology #WordOrigins #Linguistics #English #History #Language #WordHistory #LearnEnglish #Vocabulary #WordFacts #Shorts",
    ])

    description = "\n".join(description_lines)

    all_words_lower = [w.get("word", "").lower() for w in words_data]
    tags = [
        "etymology", "word origins", "linguistics", "english language",
        "word history", "where words come from", "learn english",
        "vocabulary", "word facts", CHANNEL_NAME.replace(' ', '').lower(),
        "origin of words", "language history", "english vocabulary",
    ] + all_words_lower[:5]

    return title, description, tags

def upload_to_youtube(video_path, title, description, tags=None, category_id='27'):
    if tags is None:
        tags = ['etymology', 'word origins', CHANNEL_NAME.replace(' ', '').lower()]
    youtube = get_authenticated_service()

    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': tags,
            'categoryId': category_id,
        },
        'status': {
            'privacyStatus': 'public',
            'selfDeclaredMadeForKids': False,
        },
    }

    print(f"\n[youtube] Uploading: {title[:60]}...")
    print(f"[youtube] Description: {len(description)} chars")
    print(f"[youtube] Tags: {len(tags)} tags")

    media = MediaFileUpload(video_path, chunksize=1024*1024, resumable=True)

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            pct = int(status.progress() * 100)
            print(f"[youtube] Upload progress: {pct}%")

    video_id = response.get('id')
    print(f"[youtube] Uploaded! Video ID: {video_id}")
    print(f"[youtube] URL: https://youtu.be/{video_id}")

    return {"status": "success", "video_id": video_id, "title": title}

def generate_hashtags(words_data):
    all_words = [w.get("word", "") for w in words_data]
    hashtags = [f"#{w}Etymology" for w in all_words[:3]]
    return " ".join(hashtags)
