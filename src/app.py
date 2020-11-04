from flask import Flask, render_template
from calendars.events import Events

app = Flask(__name__)

events = Events()


@app.route('/')
def index():
    """Function calls the website landing page."""

    next_events = events.next_3_events_information()

    return render_template("landing-page.html", next_events=next_events)


if __name__ == '__main__':
    app.run(debug=True)
