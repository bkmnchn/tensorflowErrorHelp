from flask import Flask, render_template, send_from_directory, url_for
from flask_uploads import UploadSet, IMAGES, configure_uploads
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField
import tensorflow as tf
from PIL import Image

app = Flask(__name__)
app.config['SECRET_KEY'] = 'asldfkjlj'
app.config['UPLOADED_PHOTOS_DEST'] = 'uploads'

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)

class UploadForm(FlaskForm):
    photo = FileField(
        validators=[
            FileAllowed(photos, 'Only images are allowed'),
            FileRequired('File field should not be empty'),
        ]
    )
    submit = SubmitField('Upload')

def predict_image(file_path):
    full_path = f"{app.config['UPLOADED_PHOTOS_DEST']}/{file_path}"
    img = Image.open(full_path)

    # 모델에 이미지 전달하여 예측
    model_path = './Model/Model'
    model = tf.saved_model.load(model_path)
    predictions = model.predict(img)
    # 예측 결과 반환
    return predictions

@app.route('/uploads/<filename>')
def get_file(filename):
    full_path = f"{app.config['UPLOADED_PHOTOS_DEST']}/{filename}"
    return send_from_directory(app.config['UPLOADED_PHOTOS_DEST'], full_path)

@app.route('/', methods=['GET', 'POST'])
def upload_image():
    form = UploadForm()
    if form.validate_on_submit():
        filename = photos.save(form.photo.data)
        file_url = url_for('get_file', filename=filename)

        # 이미지 예측
        predictions = predict_image(filename)
        # 예측 결과를 활용하는 추가 작업 수행

        return render_template('index.html', form=form, file_url=file_url, predictions=predictions)

    else:
        file_url = None
    return render_template('index.html', form=form, file_url=file_url)

if __name__ == '__main__':
    # 모델 로드 (적절한 경로와 모델 파일명 설정)
    app.run(debug=True)