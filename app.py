from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import requests
import io
import os
import base64
from PIL import Image


from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_bcrypt import Bcrypt
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
import mysql.connector
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from smtplib import SMTP, SMTPException
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from wtforms.validators import DataRequired, Email, Length

import os
import random
from email_validator import validate_email, EmailNotValidError
from flask_wtf import CSRFProtect
from flask_wtf import CSRFProtect, FlaskForm
from wtforms import TextAreaField, IntegerField, PasswordField, StringField, IntegerField, SelectField, SubmitField

import google.generativeai as genai

app = Flask(__name__)

from dotenv import load_dotenv
load_dotenv() 


app.config['SESSION_COOKIE_SECURE'] = False
bcrypt = Bcrypt(app)
csrf = CSRFProtect(app)

app.secret_key = os.urandom(24)

MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD')

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = MYSQL_PASSWORD
app.config['MYSQL_DB'] = 'aizen2'

# Establishing MySQL connection
mysql = mysql.connector.connect(
    host=app.config['MYSQL_HOST'],
    user=app.config['MYSQL_USER'],
    password=app.config['MYSQL_PASSWORD'],
    database=app.config['MYSQL_DB'],
    port=os.environ.get('DB_PORT', 3306),
)

# Setup email
s = URLSafeTimedSerializer(app.secret_key)

# Forms
class SignupForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')

class OTPForm(FlaskForm):
    otp = StringField('OTP', validators=[DataRequired(), Length(min=6, max=6)])
    submit = SubmitField('Verify')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        cursor = mysql.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        if user:
            flash('Email address already registered. Please log in.')
            return redirect(url_for('login'))
        
        otp = random.randint(100000, 999999)
        session['name'] = name
        session['email'] = email
        session['password'] = hashed_password
        session['otp'] = otp
        
        send_otp(email, otp)
        flash('OTP has been sent to your email address.')
        return redirect(url_for('otp_verification'))
    
    return render_template('signup.html', form=form)

smtp_pass = os.environ.get('SMTP_PASSWORD')
def send_otp(email, otp):
    # Gmail SMTP server setup
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_username = 'aizen.site@gmail.com'
    smtp_password = smtp_pass  

    message = MIMEMultipart()
    message['From'] = smtp_username
    message['To'] = email
    message['Subject'] = 'Your OTP Code'

    body = f'Your OTP code is {otp}'
    message.attach(MIMEText(body, 'plain'))

    try:
        server = SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(smtp_username, email, message.as_string())
        server.quit()
        print(f'OTP sent to {email}')
    except SMTPException as e:
        print(f'Failed to send OTP: {e}')

@app.route('/otp_verification', methods=['GET', 'POST'])
def otp_verification():
    form = OTPForm()
    if form.validate_on_submit():
        entered_otp = form.otp.data
        if 'otp' in session and int(entered_otp) == session['otp']:
            cursor = mysql.cursor()
            cursor.execute("INSERT INTO users (name, email, password, is_verified) VALUES (%s, %s, %s, %s)",
                           (session['name'], session['email'], session['password'], True))
            mysql.commit()
            cursor.close()
            flash('Your account has been verified and created successfully.')
            return redirect(url_for('login'))
        else:
            flash('Invalid OTP. Please try again.')
            return redirect(url_for('otp_verification'))
    return render_template('otp_verification.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        cursor = mysql.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        if user and bcrypt.check_password_hash(user[3], password):
            session['user_id'] = user[0]
            flash('Login successful!')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password. Please try again.')
    return render_template('login.html', form=form)

CLIENT_ID = os.environ.get('CLIENT_ID')
Client_secret = os.environ.get('Client_secret')
@app.route('/google_signin', methods=['POST'])
def google_signin():
    try:
        token = request.json['token']
        CLIENT_ID = CLIENT_ID

        idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), CLIENT_ID)

        if idinfo['aud'] != CLIENT_ID:
            raise ValueError('Token client ID does not match app client ID')

        userid = idinfo['sub']
        name = idinfo.get('name', 'Unknown')
        email = idinfo['email']

        cursor = mysql.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if not user:
            cursor.execute("INSERT INTO users (name, email, verified) VALUES (%s, %s, %s)", (name, email, True))
            mysql.commit()

        cursor.close()
        session['user_id'] = userid
        return jsonify(success=True)
    
    except ValueError as e:
        return jsonify(success=False, error=str(e)), 400

# =====< CONTACT US >======

class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    message = TextAreaField('Message', validators=[DataRequired(), Length(min=10, max=500)])
    submit = SubmitField('Submit')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        message = form.message.data

        cursor = mysql.cursor()
        cursor.execute('INSERT INTO contactUs (name, email, message) VALUES (%s, %s, %s)', (name, email, message))
        mysql.commit()
        cursor.close()

        flash('Thanks for contacting us. We will reach out to you soon !!')
        return redirect(url_for('home'))
    return render_template('contact.html', form=form)


# ======================--=< Generate Image >===================================================

api_key = os.environ.get('HF_TOKEN')
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
# Define a WTForms form for the input
class ImageForm(FlaskForm):
    prompt = StringField('Prompt', validators=[DataRequired()])
    submit = SubmitField('Generate Image')

# Function to query the Hugging Face API
def query(payload):
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.content if response.status_code == 200 else None

@app.route('/generate_image', methods=['GET', 'POST'])
def generate_image():
    form = ImageForm()
    image_base64 = None
    
    if form.validate_on_submit():
        user_input = form.prompt.data
       
        image_bytes = query({"inputs": user_input})
        if image_bytes:
            try:
                # Process the image
                image = Image.open(io.BytesIO(image_bytes))
                buffered = io.BytesIO()
                image.save(buffered, format="PNG")
                image_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
            except Exception as e:
                error_message = f"Failed to process image: {str(e)}"
                return render_template('generate_image.html', form=form, error=error_message)
    return render_template('generate_image.html', form=form, image=image_base64)

# ===================< Blog Generator >===========================

API_KEY_GEN = os.getenv('GEN_API_KEY')
# Configure Generative AI model
genai.configure(api_key=API_KEY_GEN)

geneconfig ={
  "temperature" : 0.8,
  "max_output_tokens": 500
}
gemini_model = genai.GenerativeModel('gemini-1.5-flash', generation_config=geneconfig)

class BlogForm(FlaskForm):
    topic = StringField('Topic', validators=[DataRequired()])
    word_limit = IntegerField('Word Limit', validators=[DataRequired()])
    keyword = StringField('Keyword', validators=[DataRequired()])
    tone = SelectField('Tone', choices=[('Informative', 'Informative'), ('Conversational', 'Conversational'), ('Humorous', 'Humorous'), ('Formal', 'Formal')], validators=[DataRequired()])
    audience = SelectField('Audience', choices=[('Common people', 'Common people'), ('Students', 'Students'), ('Professionals', 'Professionals')], validators=[DataRequired()])
@app.route('/generate_blog', methods=['GET', 'POST'])
def generate_blog():
    form = BlogForm()
    if form.validate_on_submit():
        topic = form.topic.data
        word_limit = form.word_limit.data
        keyword = form.keyword.data
        tone = form.tone.data
        audience = form.audience.data
        
        prompt = f"Create a compelling {word_limit}-word blog post on {topic} tailored to {audience}. The tone should be {tone} to captivate readers. The post must deliver valuable insights and vivid descriptions, seamlessly integrating the keyword {keyword} throughout."

        response = gemini_model.generate_content(prompt)
        generated_content = response.text

        generated_content = generated_content.replace('*', '\n')
        generated_content = generated_content.replace('#', '')

        return render_template('generate_blog.html', form=form, generated_content=generated_content)

    return render_template('generate_blog_form.html', form=form)


# ===================< Text Summarization >===========================

csrf.init_app(app)

SUMMARIZE_API_URL = "https://api-inference.huggingface.co/models/AnjaliPancheta/pegasus-finetuned-xsum"

class SummarizeTextForm(FlaskForm):
    # user_text = TextAreaField('Paste or type the text you would like to summarize...', 
    #                           validators=[DataRequired()])
    user_text = TextAreaField('Enter text to summarize:', 
                              validators=[DataRequired()],
                              render_kw={"placeholder": "Paste or type the text here you would like to summarize..."})


def query2(payload):
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.post(SUMMARIZE_API_URL, headers=headers, json=payload)
    return response.json()

@app.route('/summarize_text', methods=['GET', 'POST'])
def summarize_text():
    form = SummarizeTextForm()
    summary = None
    if request.method == 'POST' and form.validate():
        user_text = form.user_text.data

        try:
            # Send text to the API for summarization
            payload = {"inputs": user_text,
                        "wait_for_model": True}
            api_response = query2(payload)
            
            # Extract the generated_text from the API response
            summary = api_response
            
            if not summary:
                error_message = "Failed to generate summary. Please try again."
                return render_template('summarize_text.html', form=form, error=error_message)

        except Exception as e:
            error_message = f"Summarization failed: {str(e)}"
            return render_template('summarize_text.html', form=form, error=error_message)

        return render_template('summarize_text.html', form=form, user_text=user_text, summary=summary)

    return render_template('summarize_text.html', form=form)


# ===================< without fine tuning >========================

# @app.route('/summarize_text', methods=['GET', 'POST'])
# def summarize_text():
#     if request.method == 'POST':
#         user_text = request.form['user_text']
#         max_length = int(request.form['max_length'])
        
#         model_name = "google/pegasus-xsum"
#         pegasus_tokenizer = PegasusTokenizer.from_pretrained(model_name)
#         pegasus_model = PegasusForConditionalGeneration.from_pretrained(model_name)
#         summarizer = pipeline("summarization", model=model_name, tokenizer=pegasus_tokenizer, framework="pt")
        
#         summary = summarizer(user_text, max_length=max_length)
#         summarized_text = summary[0]["summary_text"]
        
#         return render_template('summarize_text.html', summarized_text=summarized_text)
    
#     return render_template('summarize_text.html')


os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'


if __name__ == '__main__':
    app.run(debug=True)


# ----------> Sample text
# As the world grapples with climate change, the need for clean energy solutions is more pressing than ever. Enter solar panels: these ingenious devices harness the power of the sun, a virtually limitless and renewable resource, to generate electricity. By embracing solar energy, we can move towards a more sustainable future for our planet. Solar panels work by converting sunlight into electricity using a process called the photovoltaic effect. When sunlight hits the panels, it excites electrons in the material, creating a flow of electricity. This electricity can be used to power homes, businesses, and even entire communities. The benefits of solar energy are numerous. Unlike fossil fuels, solar power doesn't produce harmful greenhouse gases, contributing to a cleaner environment. It's also a reliable source of energy; the sun shines consistently, making solar panels a dependable option in many regions. Additionally, solar power systems can be quite cost-effective, with installation costs decreasing significantly over the years. Solar panels are just one piece of the renewable energy puzzle. Other renewable resources like wind, geothermal, and hydropower all play a crucial role in transitioning away from fossil fuels. By combining these resources with energy storage solutions like batteries, we can create a resilient and sustainable energy grid. However, there are still some challenges to overcome. Solar panels require upfront investment and may not be suitable for all types of buildings. Additionally, their efficiency can be affected by factors like weather conditions. Despite these challenges, the future of solar energy looks bright. Technological advancements are constantly improving panel efficiency and reducing costs. As governments and businesses continue to invest in renewable energy, solar power is poised to become a major source of clean electricity for generations to come. So, the next time you see sunshine bathing your roof, remember – it's not just warmth you're experiencing, it's the potential for a cleaner and brighter future. Embrace solar energy and join the movement towards a sustainable world! 

