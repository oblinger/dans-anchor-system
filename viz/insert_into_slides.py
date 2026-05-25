#!/usr/bin/env python3
"""Upload an image to Google Drive and insert it into a Google Slide.

Usage: python3 insert_into_slides.py <image_path> <slides_url> [--slide-index N]

The slides_url should be a full Google Slides URL like:
  https://docs.google.com/presentation/d/<id>/edit#slide=id.<slide_id>

If no #slide= fragment is present, uses the first slide.

OAuth credentials are loaded from:
  ~/.google_workspace_mcp/credentials/{user}@gmail.com.json
"""

import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request


CREDS_PATH = os.path.expanduser(
    "~/.google_workspace_mcp/credentials/{user}@gmail.com.json")


def load_token():
    """Load the OAuth access token from the MCP credentials file."""
    if not os.path.exists(CREDS_PATH):
        print(f"Error: Credentials not found at {CREDS_PATH}")
        print("Start the Google Workspace MCP server and authenticate first.")
        sys.exit(1)

    with open(CREDS_PATH) as f:
        creds = json.load(f)

    token = creds.get("token")
    if not token:
        print("Error: No 'token' field in credentials file.")
        sys.exit(1)

    return token, creds


def refresh_token(creds):
    """Attempt to refresh the OAuth token using the refresh_token."""
    refresh = creds.get("refresh_token")
    client_id = creds.get("client_id")
    client_secret = creds.get("client_secret")

    if not all([refresh, client_id, client_secret]):
        return None

    data = urllib.parse.urlencode({
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh,
        "grant_type": "refresh_token"
    }).encode()

    req = urllib.request.Request(
        "https://oauth2.googleapis.com/token", data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")

    try:
        resp = urllib.request.urlopen(req)
        token_data = json.loads(resp.read())
        new_token = token_data.get("access_token")
        if new_token:
            # Update the credentials file with the new token
            creds["token"] = new_token
            with open(CREDS_PATH, "w") as f:
                json.dump(creds, f, indent=2)
            print("Token refreshed successfully.")
            return new_token
    except urllib.error.URLError as e:
        print(f"Token refresh failed: {e}")

    return None


def parse_slides_url(url):
    """Extract presentation_id and slide_id from a Google Slides URL."""
    # Extract presentation ID
    m = re.search(r'/presentation/d/([a-zA-Z0-9_-]+)', url)
    if not m:
        print(f"Error: Could not extract presentation ID from URL: {url}")
        sys.exit(1)
    presentation_id = m.group(1)

    # Extract slide ID from fragment
    slide_id = None
    m2 = re.search(r'#slide=id\.([a-zA-Z0-9_]+)', url)
    if m2:
        slide_id = m2.group(1)

    return presentation_id, slide_id


def get_first_slide_id(presentation_id, token):
    """Fetch the first slide ID from the presentation."""
    req = urllib.request.Request(
        f"https://slides.googleapis.com/v1/presentations/{presentation_id}"
        f"?fields=slides.objectId")
    req.add_header("Authorization", f"Bearer {token}")
    resp = urllib.request.urlopen(req)
    data = json.loads(resp.read())
    slides = data.get("slides", [])
    if not slides:
        print("Error: Presentation has no slides.")
        sys.exit(1)
    return slides[0]["objectId"]


def get_slide_by_index(presentation_id, token, index):
    """Fetch a slide ID by its 0-based index."""
    req = urllib.request.Request(
        f"https://slides.googleapis.com/v1/presentations/{presentation_id}"
        f"?fields=slides.objectId")
    req.add_header("Authorization", f"Bearer {token}")
    resp = urllib.request.urlopen(req)
    data = json.loads(resp.read())
    slides = data.get("slides", [])
    if index >= len(slides):
        print(f"Error: Slide index {index} out of range (presentation has {len(slides)} slides).")
        sys.exit(1)
    return slides[index]["objectId"]


def upload_to_drive(image_path, token):
    """Upload an image to Google Drive and return the file ID."""
    with open(image_path, "rb") as f:
        image_data = f.read()

    filename = os.path.basename(image_path)
    ext = os.path.splitext(filename)[1].lower()
    mime_types = {
        ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".gif": "image/gif", ".svg": "image/svg+xml", ".webp": "image/webp",
    }
    mime_type = mime_types.get(ext, "application/octet-stream")

    print(f"Uploading {filename} ({len(image_data)} bytes)...")

    boundary = "----ExcalidrawExportBoundary7890"
    metadata = json.dumps({
        "name": filename,
        "mimeType": mime_type
    }).encode()

    body = (
        f"--{boundary}\r\n"
        f"Content-Type: application/json; charset=UTF-8\r\n\r\n"
    ).encode() + metadata + (
        f"\r\n--{boundary}\r\n"
        f"Content-Type: {mime_type}\r\n\r\n"
    ).encode() + image_data + f"\r\n--{boundary}--".encode()

    req = urllib.request.Request(
        "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart",
        data=body, method="POST")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", f"multipart/related; boundary={boundary}")

    resp = urllib.request.urlopen(req)
    result = json.loads(resp.read())
    file_id = result["id"]
    print(f"Uploaded to Drive. File ID: {file_id}")
    return file_id


def share_publicly(file_id, token):
    """Make a Drive file publicly readable."""
    share_body = json.dumps({"role": "reader", "type": "anyone"}).encode()
    req = urllib.request.Request(
        f"https://www.googleapis.com/drive/v3/files/{file_id}/permissions",
        data=share_body, method="POST")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    urllib.request.urlopen(req)
    print("Shared publicly.")


def insert_into_slide(presentation_id, slide_id, image_url, token):
    """Insert an image into a Google Slide, centered and scaled to fit."""
    # Google Slides page size: 9144000 x 5143500 EMU
    page_w, page_h = 9144000, 5143500
    margin = 200000

    img_height = page_h - 2 * margin
    # Default to ~16:9-ish aspect; the image will be auto-scaled by Slides
    img_width = int(img_height * 1.43)
    x_offset = (page_w - img_width) // 2
    y_offset = margin

    slides_body = json.dumps({
        "requests": [{
            "createImage": {
                "url": image_url,
                "elementProperties": {
                    "pageObjectId": slide_id,
                    "size": {
                        "width": {"magnitude": img_width, "unit": "EMU"},
                        "height": {"magnitude": img_height, "unit": "EMU"}
                    },
                    "transform": {
                        "scaleX": 1, "scaleY": 1,
                        "translateX": x_offset, "translateY": y_offset,
                        "unit": "EMU"
                    }
                }
            }
        }]
    }).encode()

    req = urllib.request.Request(
        f"https://slides.googleapis.com/v1/presentations/{presentation_id}:batchUpdate",
        data=slides_body, method="POST")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")

    resp = urllib.request.urlopen(req)
    result = json.loads(resp.read())
    print("Inserted into slide!")
    return result


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 insert_into_slides.py <image_path> <slides_url> [--slide-index N]")
        sys.exit(1)

    image_path = sys.argv[1]
    slides_url = sys.argv[2]

    slide_index = None
    if "--slide-index" in sys.argv:
        idx = sys.argv.index("--slide-index")
        if idx + 1 < len(sys.argv):
            slide_index = int(sys.argv[idx + 1])

    if not os.path.exists(image_path):
        print(f"Error: Image not found: {image_path}")
        sys.exit(1)

    # Load OAuth token
    token, creds = load_token()

    # Parse the slides URL
    presentation_id, slide_id = parse_slides_url(slides_url)

    # Resolve slide ID
    if slide_index is not None:
        slide_id = get_slide_by_index(presentation_id, token, slide_index)
    elif not slide_id:
        slide_id = get_first_slide_id(presentation_id, token)

    print(f"Target: presentation={presentation_id}, slide={slide_id}")

    try:
        # Upload image to Drive
        file_id = upload_to_drive(image_path, token)

        # Share publicly so Slides can access it
        share_publicly(file_id, token)

        # Get the public URL
        image_url = f"https://drive.google.com/uc?id={file_id}&export=download"

        # Insert into slide
        insert_into_slide(presentation_id, slide_id, image_url, token)

        slide_url = f"https://docs.google.com/presentation/d/{presentation_id}/edit#slide=id.{slide_id}"
        print(f"\nSlide URL: {slide_url}")

    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        if e.code == 401:
            print(f"\nAuth error (401): Token expired or revoked.")
            # Try to refresh
            new_token = refresh_token(creds)
            if new_token:
                print("Retrying with refreshed token...")
                token = new_token
                file_id = upload_to_drive(image_path, token)
                share_publicly(file_id, token)
                image_url = f"https://drive.google.com/uc?id={file_id}&export=download"
                insert_into_slide(presentation_id, slide_id, image_url, token)
                slide_url = f"https://docs.google.com/presentation/d/{presentation_id}/edit#slide=id.{slide_id}"
                print(f"\nSlide URL: {slide_url}")
            else:
                print("\nCould not refresh token automatically.")
                print("Re-authenticate via the Google Workspace MCP server:")
                print("  1. Use google_oauth_get_auth_url tool in Claude Code")
                print("  2. Open the URL in a browser to authorize")
                print("  3. Retry this command")
                sys.exit(1)
        else:
            print(f"\nHTTP Error {e.code}: {error_body[:500]}")
            sys.exit(1)


if __name__ == "__main__":
    main()
