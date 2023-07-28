import json
import os
from flask import Flask, render_template, request, jsonify
from flask import send_from_directory

static_folder='__resources'

# get article.json from sub dir of 'data'
# traverse of static_folder and find the first article.json
jsonFilePath = ''
for root, dirs, files in os.walk(os.path.join(static_folder, 'data')):
    for file in files:
        if file.endswith('article.json'):
            jsonFilePath = os.path.join(root, file)
            break
if (jsonFilePath == ''):
    raise Exception('article.json not found')

# Read Json
with open(jsonFilePath) as jsonFilePath:
    json_data = json.load(jsonFilePath)
if (jsonFilePath == ''):
    raise Exception('article.json not found')

app = Flask(__name__, static_url_path=f'/resources', static_folder=static_folder)
@app.route('/', methods=['GET', 'POST'])
def display_and_handle_json():
    # if request.method == 'GET':
    #     image_path = request.path.replace('/images/', '')  # Extract image path from the URL
    #     return send_from_directory(app.static_folder, image_path)

    if request.method == 'POST':
        pass

    return render_template('index.html', json_data=json_data)

@app.route('/delete_image', methods=['POST'])
def delete_image():
    # Handle image delete request, remove image from JSON
    image_to_delete = request.json.get('image_to_delete')
    if image_to_delete:
        list_of_images = [json_data['intro']['images']]
        for main in json_data['main']:
            list_of_images.append(main['detail']['images'])
        list_of_images.append(json_data['conclusion']['images'])

        for images in list_of_images:
            if image_to_delete in images:
                images.remove(image_to_delete)
                # You can now save the updated JSON data back to the file if needed.
                # Here, we're just returning a JSON response.
                with open(jsonFilePath, 'w') as jsonFilePath:
                    json.dump(json_data, jsonFilePath, indent=4)
                return jsonify(success=True)  # Return a success response

    return jsonify(success=False, error='Image not found')  # Return an error response

if __name__ == '__main__':
    app.run(debug=True)


    
        

        # # Get the updated JSON data from the form input
        # updated_name = request.form.get('name')
        # updated_age = request.form.get('age')
        # updated_email = request.form.get('email')
        # updated_city = request.form.get('city')

        # # Update the JSON data
        # json_data['name'] = updated_name
        # json_data['age'] = int(updated_age)
        # json_data['email'] = updated_email
        # json_data['city'] = updated_city
