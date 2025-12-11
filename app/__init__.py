from flask import Flask

# Create Flask app
app = Flask(
    __name__,
    static_folder="../static",      # path to your /static folder
    template_folder="../templates"  # path to your /templates folder
)

# Import routes *after* creating the app
from app import routes
