import os
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
from flask import send_from_directory
from io import StringIO
import pandas as pd
from app.banker import produce
from app.banker import make_pivot
from flask import send_file
import zipfile


UPLOAD_FOLDER = "."
ALLOWED_EXTENSIONS = {"csv"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def send_the_stupid_files(df, labels):
    labels.to_csv("label_download.csv", index=False)
    pivot_table = make_pivot(df)
    pivot_table.to_csv("pivot_table_download.csv")
    names = ["date", "unsure_1", "unsure_2", "Category", "company", "ammount"]
    df.to_csv("updateable_dataset.csv", header=False, index=False, columns=names)
    zf = zipfile.ZipFile("zipfile_append.zip", mode="w")
    try:
        zf.write("label_download.csv")
        zf.write("pivot_table_download.csv")
        zf.write("updateable_dataset.csv")
    finally:
        zf.close()
    os.remove("pivot_table_download.csv")
    os.remove("label_download.csv")
    os.remove("updateable_dataset.csv")

    return send_file("../zipfile_append.zip", as_attachment=True)


@app.route("/", methods=["GET", "POST", "PUT"])
def upload_file():
    if request.method == "POST":
        # check if the post request has the file part
        if "raw_data" not in request.files or "labels" not in request.files:
            flash("No file part")
            return redirect(request.url)
        raw_data = request.files["raw_data"]
        labels = request.files["labels"]

        # if user does not select file, browser also
        # submit an empty part without filename
        if raw_data.filename == "" or labels.filename == "":
            flash("No selected file")
            return redirect(request.url)
        if (
            raw_data
            and allowed_file(raw_data.filename)
            and labels
            and allowed_file(labels.filename)
        ):
            raw_data_name = secure_filename(raw_data.filename)
            labels_name = secure_filename(labels.filename)
            labels.save(os.path.join(app.config["UPLOAD_FOLDER"], labels_name))
            raw_data.save(os.path.join(app.config["UPLOAD_FOLDER"], raw_data_name))
            names = ["date", "unsure_1", "unsure_2", "Category", "company", "ammount"]
            df = pd.read_csv(
                os.path.join(app.config["UPLOAD_FOLDER"], raw_data_name),
                header=None,
                names=names,
                dtype={"company": str},
            ).dropna(how="all")
            catagries = (
                pd.read_csv(os.path.join(app.config["UPLOAD_FOLDER"], labels_name))
                .drop(columns="company")
                .dropna()
            )
            df, catagries = produce(df, catagries)

            return send_the_stupid_files(df, catagries)
    return """
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=raw_data>
      <input type=file name=labels>
      <input type=submit value=Upload>
    </form>
    """
