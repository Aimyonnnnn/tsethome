from flask import Flask, request, jsonify, render_template, session, redirect, send_file
from flask_cors import CORS
import sqlite3
from datetime import datetime
from admin_auth import admin_required
import pandas as pd
from io import BytesIO

app = Flask(__name__)
CORS(app)
app.secret_key = 'your-secret-key'

def init_db():
   conn = sqlite3.connect('phone_consultations.db')
   c = conn.cursor()
   c.execute('''
       CREATE TABLE IF NOT EXISTS consultations (
           id INTEGER PRIMARY KEY AUTOINCREMENT,
           current_carrier TEXT NOT NULL,
           desired_carrier TEXT NOT NULL,
           desired_phone TEXT,
           contact TEXT NOT NULL,
           additional_notes TEXT,
           created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
       )
   ''')
   conn.commit()
   conn.close()

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
   conn = sqlite3.connect('phone_consultations.db')
   cursor = conn.cursor()
   cursor.execute('SELECT * FROM consultations ORDER BY created_at DESC')
   consultations = cursor.fetchall()
   conn.close()
   return render_template('admin_dashboard.html', consultations=consultations)

@app.route('/admin/logout')
def admin_logout():
   session.pop('admin', None)
   return redirect('/admin/login')

@app.route('/api/submit-consultation', methods=['POST'])
def submit_consultation():
   try:
       data = request.json
       print("Received data:", data)
       
       required_fields = ['current_carrier', 'desired_carrier', 'contact']
       for field in required_fields:
           if not data.get(field):
               return jsonify({'error': f'{field} is required'}), 400
               
       conn = sqlite3.connect('phone_consultations.db')
       c = conn.cursor()
       
       c.execute('''
           INSERT INTO consultations 
           (current_carrier, desired_carrier, desired_phone, contact, additional_notes)
           VALUES (?, ?, ?, ?, ?)
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
       conn = sqlite3.connect('phone_consultations.db')
       cursor = conn.cursor()
       cursor.execute('DELETE FROM consultations WHERE id IN ({})'.format(','.join('?' * len(ids))), ids)
       conn.commit()
       conn.close()
       return jsonify({'success': True})
   except Exception as e:
       return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/export-excel')
@admin_required
def export_excel():
   try:
       conn = sqlite3.connect('phone_consultations.db')
       query = 'SELECT * FROM consultations'
       
       ids = request.args.get('ids')
       if ids:
           id_list = ids.split(',')
           query += ' WHERE id IN ({})'.format(','.join('?' * len(id_list)))
           df = pd.read_sql_query(query, conn, params=id_list)
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

if __name__ == '__main__':
   init_db()
   app.run(debug=True)