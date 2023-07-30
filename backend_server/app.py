import sys
sys.path.append("./diginomard_toolkit")
sys.path.append("../diginomard_toolkit")

import json
import os
from flask import Flask, render_template, request, jsonify
from flask import send_from_directory

try:
    from diginomard_toolkit.image_search import ImageSearch
except ImportError:  # Python 3
    from image_search import ImageSearch

# get current folder from file
dir = os.path.dirname(os.path.abspath(__file__))
static_folder='__resources'
folderPath = os.path.join(dir, static_folder)

def loadJsonData():
    # get article.json from sub dir of 'data'
    # traverse of static_folder and find the first article.json
    jsonFilePath = ''
    # print cur path
    for root, dirs, files in os.walk(os.path.join(folderPath, 'data')):
        for file in files:
            if file.endswith('article.json'):
                jsonFilePath = os.path.join(root, file)
                break
    if (jsonFilePath == ''):
        raise Exception('article.json not found')
    print(jsonFilePath)

    # Read json file as dict
    with open(jsonFilePath, 'r', encoding='utf8') as file:
        json_data = json.load(file)
    
    if (json_data == ''):
        raise Exception('json_data not found')
    return jsonFilePath, json_data

jsonFilePath, json_data = loadJsonData()
app = Flask(__name__, static_url_path=f'/resources', static_folder=folderPath)
@app.route('/', methods=['GET', 'POST'])
def display_and_handle_json():
    # if request.method == 'GET':
    #     image_path = request.path.replace('/images/', '')  # Extract image path from the URL
    #     return send_from_directory(app.static_folder, image_path)

    if request.method == 'POST':
        pass

    return render_template('index.html', json_data=json_data)

@app.route('/get_images', methods=['POST'])
def get_images():
    global jsonFilePath, json_data
    keyword = request.json.get('keyword')
    index = request.json.get('index')
    if keyword and index >= 0:
        imageSearch = ImageSearch()
        images = imageSearch.getImageFromBingSearch(f'{keyword}', 10)
        print(images)
        if index == 0:
            json_data['intro']['images'] = images
        elif index - 1 < len(json_data['main']):
            json_data['main'][index - 1]['detail']['images'] = images
        else:
            json_data['conclusion']['images'] = images
        with open(jsonFilePath, 'w') as jsonFilePath:
            json.dump(json_data, jsonFilePath)
        return jsonify(success=True)  # Return a success response
    
    return jsonify(success=False, error='Image not found')  # Return an error response


@app.route('/delete_image', methods=['POST'])
def delete_image():
    global jsonFilePath, json_data
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

                print(jsonFilePath)
                print(type(json_data))
                # save dict to file
                with open(jsonFilePath, 'w') as file:
                    json.dump(json_data, file)
                
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
