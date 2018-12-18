from flask import Blueprint, render_template


upload = Blueprint('upload', __name__, template_folder='templates')


from flask import url_for, redirect, render_template
from flask_wtf import Form
from flask_wtf.file import FileField
from werkzeug import secure_filename

class UploadForm(Form):
    file = FileField()


@upload.route('/upload', methods=['GET', 'POST'])
def file_upload():
    form = UploadForm()

    if form.validate_on_submit():
        filename = secure_filename(form.file.data.filename)
        form.file.data.save('./data/' + filename)
        #return redirect(url_for('upload'))
    else:
        filename=None

    return render_template('upload/upload.html' ,form=form, filename=filename)
