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
    return seconds


def get_mennekes_power():
    l1_data = [10, 15, 12, 14, 17, 16, 13]
    l2_data = [12, 14, 11, 13, 18, 15, 16]
    l3_data = [14, 16, 13, 12, 15, 11, 17]
    total_data = [sum(data) for data in zip(l1_data, l2_data, l3_data)]
    return l1_data, l2_data, l3_data, total_data

@app.route('/')
def index():
    l1_data, l2_data, l3_data, total_data = get_mennekes_power()
    return render_template('index.html',
                           mennekes_state = get_mennekes_state(),
                           mennekes_session_energy = round(mennekes.read_float(0x0B02), 2),
                           mennekes_session_duration = get_mennekes_session_duration(),
                           mennekes_l1_power = l1_data, mennekes_l2_power = l2_data, mennekes_l3_power = l3_data, total_data = total_data,
    )

if __name__ == '__main__':
    mennekes.serial.baudrate = 57600
    mennekes.serial.stopbits = 2
    mennekes.close_port_after_each_call = True
    mennekes.write_float(0x0302, 6.0)
    app.run(host='0.0.0.0', debug=True)
