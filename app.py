from flask import Flask, request, jsonify, render_template, session, redirect, send_file
from flask_cors import CORS
import psycopg2
from datetime import datetime
from admin_auth import admin_required
import pandas as pd
from io import BytesIO
import os
from werkzeug.utils import secure_filename
import boto3
from botocore.exceptions import ClientError
import logging
from urllib.parse import quote
import base64




logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# AWS S3 설정
S3_BUCKET = os.environ.get('AWS_BUCKET_NAME')
s3_client = boto3.client(
   's3',
   aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
   aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
)

# 파일 업로드 설정
UPLOAD_FOLDER = 'static/img'  
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg'}

if not os.path.exists(UPLOAD_FOLDER):
   os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
  return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app = Flask(__name__, 
  static_url_path='',  
  static_folder='.',   
  template_folder='templates'
)

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

CORS(app, resources={
  r"/api/*": {
      "origins": "*",
      "methods": ["POST", "GET", "OPTIONS"],
      "allow_headers": ["Content-Type"]
  }
})

# Heroku 환경에서 SECRET_KEY 및 DATABASE_URL 가져오기
app.secret_key = os.environ.get('SECRET_KEY', 'fallback-secret-key')
DATABASE_URL = os.environ.get('DATABASE_URL')

# PostgreSQL 연결 및 테이블 생성
def init_db():
   conn = psycopg2.connect(DATABASE_URL, sslmode='require')
   c = conn.cursor()
   
   # consultations 테이블 생성
   c.execute('''
       CREATE TABLE IF NOT EXISTS consultations (
           id SERIAL PRIMARY KEY,
           current_carrier TEXT NOT NULL,
           desired_carrier TEXT NOT NULL,
           desired_phone TEXT,
           contact TEXT NOT NULL,
           additional_notes TEXT,
           created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
       )
   ''')
   
   # 테이블 존재 여부 확인
   c.execute('''
       SELECT EXISTS (
           SELECT FROM information_schema.tables 
           WHERE table_name = 'images'
       )
   ''')
   table_exists = c.fetchone()[0]
   
   if not table_exists:
       c.execute('''
           CREATE TABLE images (
               id SERIAL PRIMARY KEY,
               image_name TEXT NOT NULL,
               image_path TEXT NOT NULL,
               updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
           )
       ''')
       
       # 초기 데이터 삽입
       c.execute('''
           INSERT INTO images (image_name, image_path) 
           VALUES 
           ('메인 슬라이더 1', '/img/main1.png'),
           ('메인 슬라이더 2', '/img/main2.png'),
           ('메인 슬라이더 3', '/img/main3.png'),
           ('프로모션 카드 1', '/img/promo1.png'),
           ('프로모션 카드 2', '/img/promo2.png'),
           ('프로모션 카드 3', '/img/promo3.png')
       ''')
   
   conn.commit()
   conn.close()

@app.route('/')
def home():
  return send_file('index.html')

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store'  # 캐시 비활성화
    return response

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
  if request.method == 'POST':
      username = request.form['username']
      password = request.form['password']

      if username == 'admin' and password == 'password':
          session['admin'] = True
          return redirect('/admin/dashboard')
      else:
          return '로그인 실패'

  return render_template('admin_login.html')

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
   try:
       response = s3_client.list_objects_v2(
           Bucket=S3_BUCKET,
           Prefix='img/'
       )
       
       images = []
       if 'Contents' in response:
           for item in response['Contents']:
               if not item['Key'].endswith('/'):
                   obj = s3_client.head_object(Bucket=S3_BUCKET, Key=item['Key'])
                   encoded_name = obj.get('Metadata', {}).get('image_name')
                   try:
                       # base64로 인코딩된 이름을 디코딩 시도
                       image_name = base64.b64decode(encoded_name).decode('utf-8') if encoded_name else item['Key'].split('/')[-1]
                   except:
                       # 디코딩 실패시 파일명 사용
                       image_name = item['Key'].split('/')[-1]
                   
                   images.append({
                       'name': image_name,
                       'path': f'/{item["Key"]}',
                       'filename': item['Key'].split('/')[-1]
                   })
       
       conn = psycopg2.connect(DATABASE_URL, sslmode='require')
       cursor = conn.cursor()
       cursor.execute('SELECT * FROM consultations ORDER BY created_at DESC')
       consultations = cursor.fetchall()
       conn.close()
       
       return render_template('admin_dashboard.html', 
                            consultations=consultations,
                            images=images,
                            config={'S3_BUCKET': S3_BUCKET})
   except Exception as e:
       print(f"Dashboard error: {str(e)}")
       return f"데이터베이스 연결 오류: {str(e)}", 500


@app.route('/admin/logout')
def admin_logout():
  session.pop('admin', None)
  return redirect('/admin/login')

@app.route('/init-db')
def initialize_database():
  try:
      init_db()
      return "Database initialized successfully!"
  except Exception as e:
      return f"Error initializing database: {str(e)}"

@app.route('/api/submit-consultation', methods=['POST'])
def submit_consultation():
  try:
      data = request.json
      print("Received data:", data)

      required_fields = ['current_carrier', 'desired_carrier', 'contact']
      for field in required_fields:
          if not data.get(field):
              return jsonify({'error': f'{field} is required'}), 400

      conn = psycopg2.connect(DATABASE_URL, sslmode='require')
      c = conn.cursor()
      c.execute('''
          INSERT INTO consultations 
          (current_carrier, desired_carrier, desired_phone, contact, additional_notes)
          VALUES (%s, %s, %s, %s, %s)
      ''', (
          data['current_carrier'],
          data['desired_carrier'],
          data.get('desired_phone', ''),
          data['contact'],
          data.get('additional_notes', '')
      ))
      conn.commit()
      conn.close()

      return jsonify({'message': 'Consultation request submitted successfully'}), 201

  except Exception as e:
      return jsonify({'error': str(e)}), 500

@app.route('/admin/delete-consultations', methods=['POST'])
@admin_required
def delete_consultations():
    try:
        ids = request.json.get('ids', [])
        # 문자열을 정수로 변환
        ids = [int(id) for id in ids]
        logger.info(f"Attempting to delete IDs: {ids}")
        
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cursor = conn.cursor()
        query = 'DELETE FROM consultations WHERE id = ANY(%s)'
        
        cursor.execute(query, (ids,))
        logger.info(f"Query executed: {cursor.statusmessage}")
        
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Delete error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/upload-image', methods=['POST'])
@admin_required
def upload_image():
    try:
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': 'No file part'})
            
        file = request.files['image']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No selected file'})
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            try:
                s3_client.upload_fileobj(
                    file,
                    S3_BUCKET,
                    f'img/{filename}',
                    ExtraArgs={
                        'ContentType': file.content_type,
                        'CacheControl': 'no-cache'
                    }
                )
                
                return jsonify({
                    'success': True,
                    'url': f'https://society-images-storage.s3.amazonaws.com/img/{filename}'
                })
                
            except ClientError as e:
                return jsonify({'success': False, 'error': str(e)})
                
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/update-image-name/<path:filename>', methods=['POST'])
@admin_required
def update_image_name(filename):
    try:
        data = request.json
        new_name = data.get('name')
        
        # 한글 이름을 base64로 인코딩
        encoded_name = base64.b64encode(new_name.encode('utf-8')).decode('ascii')
        
        s3_client.copy_object(
            Bucket=S3_BUCKET,
            CopySource={'Bucket': S3_BUCKET, 'Key': f'img/{filename}'},
            Key=f'img/{filename}',
            Metadata={'image_name': encoded_name},
            MetadataDirective='REPLACE'
        )
        
        return jsonify({'success': True})
    except Exception as e:
        print(f"Name update error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/export-excel')
@admin_required
def export_excel():
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        query = 'SELECT * FROM consultations'

        ids = request.args.get('ids')
        if ids:
            id_list = [int(id) for id in ids.split(',')]  # 문자열을 정수로 변환
            query += ' WHERE id = ANY(%s)'
            df = pd.read_sql_query(query, conn, params=(id_list,))
        else:
            df = pd.read_sql_query(query, conn)

        conn.close()

        df.columns = ['ID', '현재 통신사', '희망 통신사', '희망 기종', '연락처', '요청사항', '신청일시']

        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='상담신청목록')
        output.seek(0)

        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='consultations.xlsx'
        )
    except Exception as e:
        return str(e)
  
@app.route('/<path:filename>')
def serve_html(filename):
    if filename.endswith('.html'):
        return render_template(filename, 
            S3_BUCKET=S3_BUCKET,
            timestamp=datetime.now().timestamp()
        )
    return send_file(filename)  

@app.route('/admin/update-image/<filename>', methods=['POST'])
@admin_required
def update_image(filename):
    try:
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': 'No file part'})
            
        file = request.files['image']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No selected file'})
            
        if file and allowed_file(file.filename):
            try:
                # 기존 객체의 메타데이터 가져오기
                obj = s3_client.head_object(Bucket=S3_BUCKET, Key=f'img/{filename}')
                metadata = obj.get('Metadata', {})
                
                s3_client.upload_fileobj(
                    file,
                    S3_BUCKET,
                    f'img/{filename}',
                    ExtraArgs={
                        'ContentType': file.content_type,
                        'CacheControl': 'no-cache, no-store, must-revalidate',
                        'Metadata': metadata  # 기존 메타데이터 유지
                    }
                )
                
                return jsonify({
                    'success': True,
                    'url': f'https://society-images-storage.s3.amazonaws.com/img/{filename}'
                })
                
            except ClientError as e:
                return jsonify({'success': False, 'error': str(e)})
                
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    
@app.route('/admin/create-image', methods=['POST'])
@admin_required
def create_image():
    try:
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': 'No file part'})
            
        file = request.files['image']
        name = request.form.get('name')
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No selected file'})
            
        if file and allowed_file(file.filename):
            # 한글 파일명 처리
            filename = secure_filename(file.filename)
            # 한글 이름을 base64로 인코딩
            encoded_name = base64.b64encode(name.encode('utf-8')).decode('ascii') if name else filename
            
            try:
                s3_client.upload_fileobj(
                    file,
                    S3_BUCKET,
                    f'img/{filename}',
                    ExtraArgs={
                        'ContentType': file.content_type,
                        'CacheControl': 'no-cache, no-store, must-revalidate',
                        'Metadata': {'image_name': encoded_name}
                    }
                )
                
                return jsonify({
                    'success': True,
                    'url': f'https://society-images-storage.s3.amazonaws.com/img/{filename}'
                })
                
            except ClientError as e:
                return jsonify({'success': False, 'error': str(e)})
                
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/delete-image/<path:filename>', methods=['POST'])
@admin_required
def delete_image(filename):
    try:
        s3_client.delete_object(
            Bucket=S3_BUCKET,
            Key=f'img/{filename}'
        )
        return jsonify({'success': True})
    except Exception as e:
        print(f"Delete error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})