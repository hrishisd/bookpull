import os
import tempfile
from pathlib import Path

import main
from flask import Flask, Response, render_template, request, send_file
from flask_dropzone import Dropzone
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired

app = Flask(__name__)
app.config["SECRET_KEY"] = "your-secret-key"

UPLOADS_DIR = "uploads"
if not os.path.exists(UPLOADS_DIR):
    os.makedirs(UPLOADS_DIR)

app.config.update(
    DROPZONE_ALLOWED_FILE_TYPE="docx",
    DROPZONE_MAX_FILE_SIZE=50,
    DROPZONE_REDIRECT_VIEW="download_excel",
    DROPZONE_INPUT_NAME="file",
    UPLOADED_DOCX_DEST=UPLOADS_DIR,
)

dropzone = Dropzone(app)


class UploadForm(FlaskForm):
    file = FileField(
        validators=[FileRequired(), FileAllowed(["docx"], "DOCX files only!")]
    )


@app.route("/", methods=["GET", "POST"])
def index() -> Response | str:
    form = UploadForm()
    if request.method == "POST":
        f = request.files.get("file")
        if f:
            filename = Path(app.config["UPLOADED_DOCX_DEST"]) / f.filename
            f.save(filename)

            with tempfile.NamedTemporaryFile(
                suffix=".csv", delete=False
            ) as output_file:
                parse_footnotes_to_excel(filename, Path(output_file.name))
                output_file.flush()
                response = send_file(
                    output_file.name,
                    as_attachment=True,
                    download_name="citations.csv",
                )
                os.unlink(output_file.name)

            return response

    return render_template("index.html", form=form)


def parse_footnotes_to_excel(doc_path: Path, output_path: Path) -> None:
    footnotes = main.parse_footnotes(doc_path)
    citations_by_footnote = main.discover_link_citations(
        main.parse_citations(footnotes)
    )
    main.to_csv(citations_by_footnote, output_path)


if __name__ == "__main__":
    app.run(debug=True)
