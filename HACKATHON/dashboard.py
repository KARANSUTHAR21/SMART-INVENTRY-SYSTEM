from flask import Flask , request , render_template


app = Flask(__name__)


@app.route('/dashboard')
def dashboard():
    return "DASHBOARD"

@app.route('/dashboard/stock')
def stock():
    return "STOCK"

@app.route('/dashboard/operation')
def operation():
    return "OPERATION"

@app.route('/dashboard/history')
def history():
    return "HISTORY"


@app.route('/dashboard/setting')
def setting():
    return "SETTING"

@app.route('/dashboard/setting/warehouse', methods=['GET', 'POST'])
def warehouse():
    return "WAREHOUSE"

@app.route('/dashboard/setting/location', methods=['GET', 'POST'])
def location():
    return "LOCATION"

if __name__ == '__main__':
    app.run(debug=True)