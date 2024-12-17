from flask import Flask, render_template, request, redirect, url_for, g, session, jsonify
import numpy as np
import joblib
import tensorflow as tf
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS  # Import Flask-CORS

app = Flask(__name__)
app.secret_key = 'your_secret_key'
CORS(app, resources={r"/*": {"origins": "*"}})  # Cho phép tất cả các domain truy cập

# Đường dẫn đến các cơ sở dữ liệu SQLite
DATABASE_HOUSE = r'C:\Users\xuant\OneDrive\Máy tính\LuanVanTotNghiep\House_Price.db'
DATABASE_ARTICLES = r'C:\Users\xuant\OneDrive\Máy tính\LuanVanTotNghiep\articles_data.db'
DATABASE_PRODUCTS = r'C:\Users\xuant\OneDrive\Máy tính\LuanVanTotNghiep\chitiet.db'
DATABASE_USERS = r'C:\Users\xuant\OneDrive\Máy tính\LuanVanTotNghiep\users.db'


# --- Database House_Price ---
def get_house_db():
    if 'house_db' not in g:
        g.house_db = sqlite3.connect(DATABASE_HOUSE)
        g.house_db.row_factory = sqlite3.Row
    return g.house_db

# --- Database articles_data ---
def get_articles_db():
    if 'articles_db' not in g:
        g.articles_db = sqlite3.connect(DATABASE_ARTICLES)
        g.articles_db.row_factory = sqlite3.Row
    return g.articles_db

# --- Database chitiet ---
def get_chitiet_db():
    if 'chitiet_db' not in g:
        g.chitiet_db = sqlite3.connect(DATABASE_PRODUCTS)
        g.chitiet_db.row_factory = sqlite3.Row
    return g.chitiet_db

# --- Database Users ---
def get_admin_db():
    if 'admin_db' not in g:
        g.admin_db = sqlite3.connect(DATABASE_USERS)
        g.admin_db.row_factory = sqlite3.Row
    return g.admin_db

def init_db():
    db = get_admin_db()
    with db:
        db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')

def add_user(email, password):
    db = get_admin_db()
    with db:
        hashed_password = generate_password_hash(password)
        db.execute('INSERT INTO users (email, password) VALUES (?, ?)', (email, hashed_password))

def get_user_by_email(email):
    db = get_admin_db()
    user = None
    with db:
        user = db.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    return user

@app.teardown_appcontext
def close_db(e=None):
    db_house = g.pop('house_db', None)
    if db_house is not None:
        db_house.close()
    db_articles = g.pop('articles_db', None)
    if db_articles is not None:
        db_articles.close()
    db_products = g.pop('chitiet_db', None)
    if db_products is not None:
        db_products.close()
    db_admin = g.pop('admin_db', None)
    if db_admin is not None:
        db_admin.close()

scaler_X = joblib.load('scaler_X.pkl')
scaler_y = joblib.load('scaler_y.pkl')
model = tf.keras.models.load_model('house_price_model.keras')

@app.route('/')
def index():
    db = get_chitiet_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM chitiet LIMIT 6 OFFSET 10")
    properties = cursor.fetchall()
    return render_template('index.html', properties=properties)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/services')
def services():
    return render_template('services.html')


@app.route('/properties')
def properties():
    db = get_house_db()
    per_page = 6
    page = request.args.get('page', 1, type=int)
    offset = (page - 1) * per_page

    properties = db.execute(
        'SELECT ID, Title, Address, Date_Posted, Number_of_Bedrooms, Number_of_Bathrooms, Area_m2, Price, Image_URL FROM House_Price LIMIT ? OFFSET ?',
        (per_page, offset)
    ).fetchall()

    total_properties = db.execute('SELECT COUNT(*) FROM House_Price').fetchone()[0]
    total_pages = (total_properties + per_page - 1) // per_page

    return render_template(
        'properties.html',
        properties=properties,
        page=page,
        total_pages=total_pages
    )

@app.route('/property/<int:id>')
def property_detail(id):
    db = get_chitiet_db()
    property_detail = db.execute('SELECT * FROM chitiet WHERE id = ?', (id,)).fetchone()
    if property_detail is None:
        return "Sản phẩm không tồn tại", 404
    return render_template('property_detail.html', property=property_detail)


@app.route('/agents')
def agents():
    db = get_articles_db()
    per_page = 12
    page = request.args.get('page', 1, type=int)
    offset = (page - 1) * per_page
    
    agents = db.execute(
        'SELECT title, image_url FROM articles LIMIT ? OFFSET ?', 
        (per_page, offset)
    ).fetchall()
    
    total_agents = db.execute('SELECT COUNT(*) FROM articles').fetchone()[0]
    total_pages = (total_agents + per_page - 1) // per_page
    
    start_page = max(1, page - 2)
    end_page = min(total_pages, page + 2)

    return render_template('agents.html', agents=agents, page=page, total_pages=total_pages, start_page=start_page, end_page=end_page)

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/service-details')
def service_details():
    return render_template('service-details.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = get_user_by_email(email)
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            return redirect(url_for('admin'))
        else:
            error = 'Invalid email or password'
    return render_template('login.html', error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if get_user_by_email(email):
            error = 'Email already registered'
        else:
            add_user(email, password)
            return redirect(url_for('login'))
    return render_template('register.html', error=error)

@app.route('/admin')
def admin():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('Dashboard.html')

# Hàm thêm bài viết vào database
def add_article_to_db(title, image_url):
    db = get_articles_db()
    with db:
      db.execute(
            'INSERT INTO articles (title, image_url) VALUES (?, ?)',
            (title, image_url)
        )

@app.route('/NewArticle', methods=['GET', 'POST'])
def NewArticle():
   if 'user_id' not in session:
        return redirect(url_for('login'))
   if request.method == 'POST':
        title = request.form['title']
        image_url = request.form['image_url']
        add_article_to_db(title, image_url)
        return redirect(url_for('admin'))
   return render_template('NewArticle.html')

@app.route('/list_articles') # Route list bài viết
def list_articles():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    db = get_articles_db()
    per_page = 10
    page = request.args.get('page', 1, type=int)
    offset = (page - 1) * per_page

    articles = db.execute(
        'SELECT id, title, image_url FROM articles LIMIT ? OFFSET ?',
        (per_page, offset)
    ).fetchall()

    total_articles = db.execute('SELECT COUNT(*) FROM articles').fetchone()[0]
    total_pages = (total_articles + per_page - 1) // per_page

    start_page = max(1, page - 2)
    end_page = min(total_pages, page + 2)

    return render_template(
        'list_articles.html',
        articles=articles,
        page=page,
        total_pages=total_pages,
        start_page=start_page,
        end_page=end_page
    )

def delete_article_from_db(id):
  db = get_articles_db()
  with db:
    db.execute('DELETE FROM articles WHERE id = ?', (id,))
    
@app.route('/delete_article/<int:id>', methods=['POST'])
def delete_article(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    delete_article_from_db(id)
    return redirect(url_for('list_articles'))


# Hàm thêm bất động sản
def add_property_to_db(image_url, title, price, address, date, description, usable_area, land_area, bedrooms, bathrooms, legal, posted_date):
  db = get_chitiet_db()
  with db:
    db.execute(
      'INSERT INTO chitiet ("Image URL", Title, Price, Address, Date, Description, Usable_Area, Land_Area, Bedrooms, Bathrooms, Legal, Posted_Date, Property_ID) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL)',
      (image_url, title, price, address, date, description, usable_area, land_area, bedrooms, bathrooms, legal, posted_date)
    )


@app.route('/add_property', methods=['GET', 'POST'])
def add_property():
  if 'user_id' not in session:
    return redirect(url_for('login'))
  if request.method == 'POST':
        image_url = request.form['image_url']
        title = request.form['title']
        price = request.form['price']
        address = request.form['address']
        date = request.form['date']
        description = request.form['description']
        usable_area = request.form['usable_area']
        land_area = request.form['land_area']
        bedrooms = request.form['bedrooms']
        bathrooms = request.form['bathrooms']
        legal = request.form['legal']
        posted_date = request.form['posted_date']

        
        add_property_to_db(image_url, title, price, address, date, description, usable_area, land_area, bedrooms, bathrooms, legal, posted_date)
        return redirect(url_for('admin'))
  return render_template('add_property.html')

# ... (phần import, database, route khác giữ nguyên)

@app.route('/list_properties')
def list_properties():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    db = get_house_db()
    per_page = 10
    page = request.args.get('page', 1, type=int)
    offset = (page - 1) * per_page

    properties = db.execute(
        'SELECT ID, Title, Address, Date_Posted, Number_of_Bedrooms, Number_of_Bathrooms, Area_m2, Price, Image_URL FROM House_Price LIMIT ? OFFSET ?',
        (per_page, offset)
    ).fetchall()

    total_properties = db.execute('SELECT COUNT(*) FROM House_Price').fetchone()[0]
    total_pages = (total_properties + per_page - 1) // per_page

    start_page = max(1, page - 2)
    end_page = min(total_pages, page + 2)

    return render_template(
        'list_properties.html',
        properties=properties,
        page=page,
        total_pages=total_pages,
        start_page=start_page,
        end_page=end_page
    )

# Hàm xóa bất động sản
def delete_property_from_db(id):
    db = get_house_db()
    with db:
        db.execute('DELETE FROM House_Price WHERE ID = ?', (id,))

@app.route('/delete_property/<int:id>', methods=['POST'])
def delete_property(id):
    if 'user_id' not in session:
      return redirect(url_for('login'))
    delete_property_from_db(id)
    return redirect(url_for('properties'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))


@app.route('/DuDoan', methods=['GET', 'POST'], endpoint='DuDoan')
def DuDoan():
    prediction = None
    if request.method == 'POST':
        # Lấy dữ liệu từ form
        area = float(request.form['area'])
        bedrooms = int(request.form['bedrooms'])
        bathrooms = int(request.form['bathrooms'])

        # Chuẩn bị dữ liệu đầu vào cho mô hình
        input_data = np.array([[area, bedrooms, bathrooms]])
        input_data_scaled = scaler_X.transform(input_data)

        # Dự đoán và đưa kết quả về dạng ban đầu
        prediction_scaled = model.predict(input_data_scaled)
        prediction = scaler_y.inverse_transform(prediction_scaled)[0][0]
        prediction = f"{prediction:,.0f} VND"  # Định dạng thành tiền

    return render_template('DuDoan.html', prediction=prediction)

@app.route('/api/dudoan', methods=['GET', 'POST'])
def api_dudoan():
    if request.method == 'POST':
        # Lấy dữ liệu từ request
        try:
            area = float(request.form['area'])
            bedrooms = int(request.form['bedrooms'])
            bathrooms = int(request.form['bathrooms'])
        except ValueError:
            return jsonify({'error': 'Invalid input'}), 400

        # Chuẩn bị dữ liệu đầu vào cho mô hình
        input_data = np.array([[area, bedrooms, bathrooms]])
        input_data_scaled = scaler_X.transform(input_data)

        # Dự đoán và đưa kết quả về dạng ban đầu
        prediction_scaled = model.predict(input_data_scaled)
        prediction = scaler_y.inverse_transform(prediction_scaled)[0][0]
        prediction = f"{prediction:,.0f} VND"  # Định dạng thành tiền

        return jsonify({'prediction': prediction})
    return jsonify({'error': 'Invalid request method'}), 400

@app.route('/api/properties')
def api_get_properties():
    db = get_chitiet_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM chitiet")
    properties = cursor.fetchall()

    result = []
    for row in properties:
       result.append(dict(row))
    return jsonify(result)



@app.route('/api/property/<int:id>')
def api_get_property(id):
   db = get_chitiet_db()
   cursor = db.cursor()
   cursor.execute("SELECT * FROM chitiet WHERE id = ?", (id,))
   property_detail = cursor.fetchone()
   
   if property_detail:
       return jsonify(dict(property_detail))
   else:
       return jsonify({'error': 'Property not found'}), 404

@app.route('/api/agents')
def api_get_agents():
    db = get_articles_db()
    agents = db.execute('SELECT title, image_url FROM articles').fetchall()
    result = []
    for row in agents:
      result.append(dict(row))
    return jsonify(result)


@app.route('/api/index')
def api_get_index():
    db = get_house_db()
    index = db.execute('SELECT title, image_url FROM articles').fetchall()
    result = []
    for row in index:
      result.append(dict(row))
    return jsonify(result)

# --- Run ---
if __name__ == '__main__':
    with app.app_context():
        init_db()
        if not get_user_by_email('test@example.com'):
            add_user('test@example.com', 'test1234')
    app.run(debug=True)