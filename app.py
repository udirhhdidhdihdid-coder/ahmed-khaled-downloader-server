from flask import Flask, request, send_file, jsonify
import yt_dlp
import os
import uuid

app = Flask(__name__)

DOWNLOAD_DIR = "/tmp/ahmed_khaled_downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


@app.route("/")
def home():
    return jsonify({
        "status": "ok",
        "server": "Ahmed Khaled Downloader"
    })


@app.route("/download", methods=["GET"])
def download_video():
    url = request.args.get("url")

    if not url:
        return jsonify({
            "success": False,
            "error": "الرابط مفقود"
        }), 400

    if not (
        url.startswith("http://")
        or url.startswith("https://")
    ):
        return jsonify({
            "success": False,
            "error": "الرابط غير صحيح"
        }), 400

    file_id = str(uuid.uuid4())
    output_template = os.path.join(
        DOWNLOAD_DIR,
        file_id + ".%(ext)s"
    )

    options = {
        "outtmpl": output_template,
        "format": "best[ext=mp4]/best",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "restrictfilenames": True
    }

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=True)

            filename = ydl.prepare_filename(info)

            if not os.path.exists(filename):
                base = os.path.splitext(filename)[0]

                for ext in ["mp4", "webm", "mkv", "mov"]:
                    test_file = base + "." + ext
                    if os.path.exists(test_file):
                        filename = test_file
                        break

            if not os.path.exists(filename):
                return jsonify({
                    "success": False,
                    "error": "لم يتم العثور على الملف"
                }), 500

            return send_file(
                filename,
                as_attachment=True,
                download_name="Ahmed-Khaled-Video.mp4"
            )

    except Exception as e:
        return jsonify({
            "success": False,
            "error": "تعذر تحميل الفيديو",
            "details": str(e)
        }), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))

    app.run(
        host="0.0.0.0",
        port=port
    )
