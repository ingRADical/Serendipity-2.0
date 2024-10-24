from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'  
DATABASE = 'serendipity1.db'

# Connection to database
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row 
    return conn

@app.route('/')
def index():
    return render_template('index.html')

# Calling all the correct information from the database to use in the Menu code
@app.route('/menu')
def menu():
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('SELECT id, milk_tea, temperature, image_path FROM Milk_Tea')
    milk_tea = cursor.fetchall()
    
    cursor.execute('SELECT id, smoothie, image_path FROM Smoothie')
    smoothies = cursor.fetchall()
    
    cursor.execute('SELECT id, brewed_tea, image_path, temperature FROM Brewed_Tea')
    brewed_tea = cursor.fetchall()
    
    cursor.execute('SELECT id, desserts, image_path, price FROM Food')
    desserts = cursor.fetchall()
    
    cursor.execute('SELECT id, toppings, image_path, price FROM Toppings')
    toppings = cursor.fetchall()
    
    return render_template('menu.html', milk_tea=milk_tea, smoothies=smoothies, brewed_tea=brewed_tea, desserts=desserts, toppings=toppings)

# Calling all the correct information from the database to use
@app.route('/order', methods=['GET', 'POST'])
def order():
    db = get_db()
    cursor = db.cursor()

    cursor.execute('SELECT id, size, price FROM Sizes')
    sizes = cursor.fetchall()

    cursor.execute('SELECT id, milk_tea, temperature FROM Milk_Tea')
    milk_teas = cursor.fetchall()

    cursor.execute('SELECT id, brewed_tea, temperature FROM Brewed_Tea')
    brewed_teas = cursor.fetchall()

    cursor.execute('SELECT id, smoothie FROM Smoothie')
    smoothies = cursor.fetchall()

    cursor.execute('SELECT id, toppings FROM Toppings')
    toppings = cursor.fetchall()

    cursor.execute('SELECT id, desserts FROM Food')
    foods = cursor.fetchall()

    if request.method == 'POST':
        size_type = request.form.get('size_type')
        drink_id = request.form.get('drink_id')
        topping_id = request.form.get('topping_id')
        food_id = request.form.get('food_id')
        quantity = request.form.get('quantity', type=int, default=1)

        cursor.execute('SELECT price FROM Sizes WHERE id = ?', (size_type,))
        size_price = cursor.fetchone()['price']

        cursor.execute('SELECT price FROM Toppings WHERE id = ?', (topping_id,))
        topping_price = cursor.fetchone()['price']

        total_price = (size_price + topping_price) * quantity

        cursor.execute('INSERT INTO Orders (drink, topping, quantity, size, total_price) VALUES (?, ?, ?, ?, ?)', 
               (drink_id, topping_id, quantity, size_type, total_price))

        db.commit()

        order_id= cursor.lastrowid
        return redirect(url_for('checkout', order_id=order_id))

    return render_template('order.html', sizes=sizes, milk_teas=milk_teas, brewed_teas=brewed_teas, smoothies=smoothies, toppings=toppings)


# Allows checkout to recite order back to customer
@app.route('/checkout/<int:order_id>')
def checkout(order_id):
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('''
        SELECT Orders.quantity, Orders.total_price, 
               CASE 
                   WHEN Milk_Tea.milk_tea IS NOT NULL THEN Milk_Tea.milk_tea
                   WHEN Brewed_Tea.brewed_tea IS NOT NULL THEN Brewed_Tea.brewed_tea
                   WHEN Smoothie.smoothie IS NOT NULL THEN Smoothie.smoothie
               END AS drink_name,
               Toppings.toppings AS topping_name,
               Sizes.size AS size_name
        FROM Orders
        LEFT JOIN Milk_Tea ON Orders.drink = Milk_Tea.id
        LEFT JOIN Brewed_Tea ON Orders.drink = Brewed_Tea.id
        LEFT JOIN Smoothie ON Orders.drink = Smoothie.id
        JOIN Toppings ON Orders.topping = Toppings.id
        JOIN Sizes ON Orders.size = Sizes.id
        WHERE Orders.id = ?
    ''', (order_id,))
    
    order = cursor.fetchone()

    return render_template('checkout.html', order=order)

if __name__ == '__main__':
    app.run(debug=True)