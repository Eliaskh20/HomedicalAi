from flask import Flask, render_template, request, jsonify
import numpy as np
import pandas as pd
import joblib
import pickle
import warnings


warnings.filterwarnings("ignore", message="X does not have valid feature names")

app = Flask(__name__)

# Elias Alkharma
blood_glucose_model = joblib.load('BloodGlucose_model.pkl')
blood_glucose_scaler = joblib.load('scalerBloodGlucose.pkl')
blood_glucose_selector = joblib.load('selectorBloodGlucose.pkl')


# Nayaz
heart_disease_model = pickle.load(open('heart_disease_pred.sav', 'rb'))


# Amaar
with open('Parkinsson_model.pkl', 'rb') as file:
    parkinsson_model = pickle.load(file)


# Ayman
with open('thyroid_disease_detection.sav', 'rb') as file:
    thyroid_model = joblib.load(file)


# Maha
Hypertension_model = joblib.load('Hypertension_model.pkl')



# Load the LightGBM model
Deepression_model = joblib.load('Deepression_model.pkl')
Deepression_scaler = joblib.load('Deepression_scaler.pkl')




@app.route('/')
def index():
    return render_template('index.html')

def validate_input(data):
    required_fields = [
        'Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness',
        'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age'
    ]
    for field in required_fields:
        if field not in data:
            return False, f'Missing field: {field}'
        if not isinstance(data[field], (int, float)):
            return False, f'Invalid type for field: {field}'
    return True, ''

@app.route('/page1', methods=['GET', 'POST'])
def page1():
    if request.method == 'POST':
        data = request.json
        is_valid, error_message = validate_input(data)
        if not is_valid:
            return jsonify({'error': error_message}), 400
        try:
            input_features = np.array([[
                data['Pregnancies'],
                data['Glucose'],
                data['BloodPressure'],
                data['SkinThickness'],
                data['Insulin'],
                data['BMI'],
                data['DiabetesPedigreeFunction'],
                data['Age']
            ]])
            scaled_features = blood_glucose_scaler.transform(input_features)
            selected_features = blood_glucose_selector.transform(scaled_features)
            blood_glucose_prediction = blood_glucose_model.predict(selected_features)[0]

            return jsonify({
                'blood_glucose_prediction': int(blood_glucose_prediction)
            })

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return render_template('page1.html')


@app.route('/page2', methods=['GET', 'POST'])
def page2():
    if request.method == 'POST':
        data = request.json
        try:
            input_data = [
                int(data.get('Age', 0)),
                int(data.get('Sex', 0)),
                int(data.get('ChestPainType', 0)),
                int(data.get('RestingBP', 0)),
                int(data.get('Cholesterol', 0)),
                int(data.get('FastingBS', 0)),
                int(data.get('RestingECG', 0)),
                int(data.get('MaxHR', 0)),
                int(data.get('ExerciseAngina', 0)),
                float(data.get('Oldpeak', 0.0)),
                int(data.get('ST_Slope', 0))
            ]

            input_data_as_numpy_array = np.asarray(input_data)
            input_data_reshaped = input_data_as_numpy_array.reshape(1, -1)
            prediction = heart_disease_model.predict(input_data_reshaped)

            if prediction[0] == 0:
                diagnosis = 'Low Risk Detected'
            else:
                diagnosis = 'High Risk Detected'

            return jsonify({'diagnosis': diagnosis})

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return render_template('page2.html')

@app.route('/page3', methods=['GET', 'POST'])
def page3():
    if request.method == 'POST':
        data = request.json
        input_data = [
            int(data.get('MDVP:Fo(Hz)', 0)),
            int(data.get('MDVP:Fhi(Hz)', 0)),
            int(data.get('MDVP:Flo(Hz)', 0)),
            float(data.get('MDVP:Jitter(%)', 0.00)),
            float(data.get('Jitter:DDP', 0.00)),
            float(data.get('Shimmer:APQ5', 0.00)),
            int(data.get('HNR', 0)),
            float(data.get('spread1', 0.00)),
            float(data.get('spread2', 0.00)),
            float(data.get('PPE', 0.00)),
        ]
        input_data_as_numpy_array = np.asarray(input_data)
        input_data_reshaped = input_data_as_numpy_array.reshape(1, -1)
        prediction = parkinsson_model.predict(input_data_reshaped)
        if prediction == 1:
            result = 'Have Parkinson'
        elif prediction == 0:
            result = 'Do Not Have Parkinson'
        else:
            result = 'An error occurred: ' + prediction

        return jsonify({'Parkinson': result})

    return render_template('page3.html')

@app.route('/page4', methods=['GET', 'POST'])
def page4():
    if request.method == 'POST':
        data = request.json
        try:
            input_features = pd.DataFrame({
                'age': [int(data.get('age', 0))],
                'sex': [int(data.get('sex', 0))],
                'TT4': [float(data.get('TT4', 0.0))],
                'T3': [float(data.get('T3', 0.0))],
                'T4U': [float(data.get('T4U', 0.0))],
                'FTI': [float(data.get('FTI', 0.0))],
                'TSH': [float(data.get('TSH', 0.0))],
                'pregnant': [int(data.get('pregnant', 0))]
            })

            input_data_as_numpy_array2 = np.asarray(input_features)
            input_data_reshaped2 = input_data_as_numpy_array2.reshape(1, -1)
            prediction = thyroid_model.predict(input_features)[0]

            if prediction == 1:
                resul = 'Hypothyroidism'
            elif prediction == 2:
                resul = 'normal condition and does not suffer from any thyroid problems.'
            else:
                resul = 'Hyperthyroidism.'

            return jsonify({'diagnosis': resul})

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return render_template('page4.html')


@app.route('/page5', methods=['GET', 'POST'])
def page5():
    if request.method == 'POST':
        try:
            # Extract JSON data from the request
            data = request.json

            # Extract features and convert to integers
            features = [
                int(data.get('age', 0)),
                int(data.get('sex', 0)),
                int(data.get('cp', 0)),
                int(data.get('trestbps', 0)),
                int(data.get('chol', 0)),
                int(data.get('fbs', 0)),
                int(data.get('restecg', 0)),
                int(data.get('thalach', 0)),
                int(data.get('exang', 0)),
                int(data.get('oldpeak', 0)),
                int(data.get('slope', 0)),
                int(data.get('ca', 0)),
                int(data.get('thal', 0)),

            ]

            # Convert features to numpy array and reshape for the model
            features_array = np.array([features])
            print(features_array)

            # Make prediction
            prediction = Hypertension_model.predict(features_array)[0]

            # Return prediction as JSON
            return jsonify({'knn_prediction': int(prediction)})

        except Exception as e:
            # Return error message as JSON
            return jsonify({'error': str(e)}), 500

    # Render the HTML page for GET requests
    return render_template('page5.html')


@app.route('/page6', methods=['GET', 'POST'])
def page6():
    if request.method == 'POST':
        try:
            # Extract JSON data from the request
            data = request.json

            # Extract features and convert to integers
            features = [
                int(data.get('angry', 0)),
                int(data.get('fear', 0)),
                int(data.get('disgust', 0)),
                int(data.get('happy', 0)),
                int(data.get('neutral', 0)),
                int(data.get('sad', 0)),
                int(data.get('surprise', 0)),
            ]

            # Convert features to numpy array and reshape for the model
            features_array = np.array([features])

            # Scale the data
            scaled_data = Deepression_scaler.transform(features_array)

            # Make prediction
            prediction = Deepression_model.predict(scaled_data)[0]

            # Return prediction as JSON
            return jsonify({'Deepression': int(prediction)})

        except Exception as e:
            # Return error message as JSON
            return jsonify({'error': str(e)}), 500

    # Render the HTML page for GET requests
    return render_template('page6.html')


if __name__ == '__main__':
    app.run(debug=True)
