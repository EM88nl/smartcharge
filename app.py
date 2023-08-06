from flask import Flask, render_template
from flask_bootstrap import Bootstrap

import minimalmodbus

app = Flask(__name__)
bootstrap = Bootstrap(app)

mennekes = minimalmodbus.Instrument('/dev/ttyUSB0', 50)

def get_mennekes_state():
    raw_data = mennekes.read_register(0x0100)
    status_map = {
        0: 'Not Initialized',
        1: 'Idle',
        2: 'Connected',
        3: 'Precondition Valid',
        4: 'Ready to Charge',
        5: 'Charging',
        6: 'Error',
        7: 'Service Mode'
    }

    return status_map.get(raw_data, 'Unknown Status')


def get_mennekes_session_duration():
    seconds = mennekes.read_long(0x0B04)
    if seconds == 0:
        return '00:00'
    hours = seconds // 3600
    remaining_seconds = seconds % 3600
    minutes = remaining_seconds // 60
    time_str = f"{hours:02d}:{minutes:02d}"

@app.route('/')
def index():
    return render_template('index.html',
                           mennekes_state = get_mennekes_state(),
                           mennekes_session_energy = mennekes.read_float(0x0B02),
                           mennekes_session_duration = get_mennekes_session_duration()
    )

if __name__ == '__main__':
    mennekes.serial.baudrate = 57600
    mennekes.serial.stopbits = 2
    mennekes.close_port_after_each_call = True
    app.run(host='0.0.0.0', debug=True)
