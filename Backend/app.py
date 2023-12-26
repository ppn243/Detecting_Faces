from flask import Flask, request, jsonify

app = Flask(__name__)

# Lưu trữ dữ liệu đã nhận diện thành công
detected_data = [
    {'result': 'PersonA'},
    {'result': 'PersonB'},
    {'result': 'PersonC'},
]


@app.route('/send_result', methods=['POST'])
def send_result():
    result = request.json.get('result')  # Nhận kết quả từ formhome

    # Xử lý kết quả
    print("Received result from formhome:", result)

    # Lưu trữ kết quả vào biến detected_data
    detected_data.append({'result': result})

    return jsonify({'status': 'success', 'result': result})

@app.route('/send_data', methods=['POST'])
def send_data():
    data = request.json  # Nhận dữ liệu từ frontend

    # Xử lý dữ liệu
    print("Received data from detection:", data)

    # Lưu trữ dữ liệu vào biến detected_data
    detected_data.append(data)

    return jsonify({'data': data})

# Endpoint để frontend có thể lấy dữ liệu đã nhận diện


@app.route('/get_detected_data', methods=['GET'])
def get_detected_data():
    return jsonify({'detected_data': detected_data})


if __name__ == '__main__':
    app.run(debug=True)
