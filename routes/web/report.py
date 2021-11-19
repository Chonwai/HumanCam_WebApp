from flask import Blueprint, render_template, send_from_directory
import glob
import os

report = Blueprint('report', __name__)


@report.route("/reports")
def reportList():
    files = glob.glob(os.path.realpath('storage/report/*.csv'))
    files.sort(key=os.path.getmtime)
    reportList = [os.path.basename(x) for x in files]
    return render_template('reports.html', reportList=reportList[::-1])


@report.route("/reports/<path:filename>/download")
def reportDownload(filename):
    uploads = os.path.join('storage/report/')
    return send_from_directory(directory=uploads, path=filename)


@report.route("/reports/<path:filename>")
def reportViewer(filename):
    return render_template('report.html', filename=filename)
