#\"""Publish Park View Drugs to here.now static hosting.\"""
import hashlib
import json
import mimetypes
import os
import shutil
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from app import app

DIST_DIR = "publish_dist"

ROUTES = [
    ("/", "index.html"),
    ("/services", "services"),
    ("/services/compounding", "services/compounding"),
    ("/services/delivery", "services/delivery"),
    ("/services/medication-review", "services/medication-review"),
    ("/services/minor-ailment", "services/minor-ailment"),
    ("/services/prescription-refills", "services/prescription-refills"),
    ("/services/vaccinations", "services/vaccinations"),
    ("/products", "products"),
    ("/weekly-flyer", "weekly-flyer"),
    ("/minor-ailment", "minor-ailment"),
    ("/about", "about"),
    ("/contact", "contact"),
    ("/legal/privacy", "legal/privacy"),
    ("/legal/terms", "legal/terms"),
    ("/robots.txt", "robots.txt"),
    ("/sitemap.xml", "sitemap.xml")
]

def export_site():
    print("Exporting static site from Flask...")
    if os.path.exists(DIST_DIR):
        shutil.rmtree(DIST_DIR)
    os.makedirs(DIST_DIR, exist_ok=True)

    # Copy static assets
    shutil.copytree("static", os.path.join(DIST_DIR, "static"))

    with app.test_client() as client:
        for url, target in ROUTES:
            res = client.get(url)
            if res.status_code == 200:
                if target.endswith((".txt", ".xml", ".html")):
                    out_path = os.path.join(DIST_DIR, target)
                    os.makedirs(os.path.dirname(out_path), exist_ok=True)
                    with open(out_path, "wb") as f:
                        f.write(res.data)
                else:
                    dir_path = os.path.join(DIST_DIR, target)
                    os.makedirs(dir_path, exist_ok=True)
                    with open(os.path.join(dir_path, "index.html"), "wb") as f:
                        f.write(res.data)
                    with open(os.path.join(DIST_DIR, target + ".html"), "wb") as f:
                        f.write(res.data)
            else:
                print(f"Warning: {url} returned {res.status_code}")

    print("Export completed successfully.")

def get_api_key():
    key = os.environ.get("HERENOW_API_KEY")
    if key:
        return key.strip()
    cred_path = os.path.expanduser("~/.herenow/credentials")
    if os.path.exists(cred_path):
        try:
            with open(cred_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception:
            pass
    return None

def publish():
    export_site()

    mimetypes.add_type("image/svg+xml", ".svg")
    mimetypes.add_type("text/css", ".css")
    mimetypes.add_type("application/javascript", ".js")

    files_payload = []
    for root, _, files in os.walk(DIST_DIR):
        for f in files:
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, DIST_DIR).replace("\\", "/")
            size = os.path.getsize(full_path)
            with open(full_path, "rb") as fp:
                file_hash = hashlib.sha256(fp.read()).hexdigest()
            content_type = mimetypes.guess_type(full_path)[0] or "application/octet-stream"
            files_payload.append({
                "path": rel_path,
                "size": size,
                "contentType": content_type,
                "hash": file_hash
            })

    api_key = get_api_key()
    headers = {
        "Content-Type": "application/json",
        "X-HereNow-Client": "antigravity/publish-py",
        "User-Agent": "Antigravity/1.0"
    }
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    req_body = {
        "displayName": "Park View Drugs & Pharmacy",
        "displayDescription": "Official community pharmacy website for Park View Drugs, Esperance, Trinidad & Tobago.",
        "files": files_payload
    }

    print(f"Submitting {len(files_payload)} files to here.now API...")
    req = urllib.request.Request(
        "https://here.now/api/v1/publish",
        data=json.dumps(req_body).encode("utf-8"),
        headers=headers,
        method="POST"
    )

    with urllib.request.urlopen(req) as resp:
        session = json.loads(resp.read().decode("utf-8"))

    uploads = session["upload"]["uploads"]
    finalize_url = session["upload"]["finalizeUrl"]
    version_id = session["upload"]["versionId"]

    def upload_single_file(item):
        rel = item["path"]
        loc = os.path.join(DIST_DIR, rel.replace("/", os.sep))
        u = item["url"]
        h = item.get("headers", {})
        with open(loc, "rb") as fp:
            d = fp.read()
        r = urllib.request.Request(u, data=d, headers=h, method="PUT")
        with urllib.request.urlopen(r) as res:
            return rel, res.status

    print(f"Uploading {len(uploads)} assets...")
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = [executor.submit(upload_single_file, item) for item in uploads]
        for future in as_completed(futures):
            future.result()

    print("Finalizing live site version...")
    fin_req = urllib.request.Request(
        finalize_url,
        data=json.dumps({"versionId": version_id}).encode("utf-8"),
        headers=headers,
        method="POST"
    )
    with urllib.request.urlopen(fin_req) as fin_resp:
        fin_data = json.loads(fin_resp.read().decode("utf-8"))

    print("\n" + "=" * 54)
    print("  ?? SITE IS LIVE ON HERE.NOW!")
    print("=" * 54)
    print("  Live URL:  ", session["siteUrl"])
    if session.get("claimUrl"):
        print("  Claim URL: ", session["claimUrl"])
    print("=" * 54)

if __name__ == "__main__":
    publish()
