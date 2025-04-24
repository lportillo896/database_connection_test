from flask import Flask

from approutes.getroutes import app as get_routes_app
from db_utils import Base, engine, os

app = Flask(__name__)
app.register_blueprint(get_routes_app)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{os.getenv("MYSQL_USER", "root")}:{os.getenv("MYSQL_PASSWORD", "Liberty10")}@{os.getenv("MYSQL_HOST", "mysql")}:{3306}/{os.getenv("MYSQL_DATABASE", "Plague_Rat_Character")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

@app.route("/")
def welcome():
    return "<p>Welcome to the Plague Rats API!</p>"

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    app.run(debug=True, host="0.0.0.0", port=5000)