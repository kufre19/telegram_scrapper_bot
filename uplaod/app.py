from flask import Flask, render_template, request, jsonify
import subprocess
import threading
import subprocess
import json
from flask import Flask, render_template, request, session, redirect, url_for
from flask_session import Session  # You might need to install this with 'pip install Flask-Session'

app = Flask(__name__)



app.secret_key = 'your_secret_key'  # Set a secret key for session management
# Configure and initialize the session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Step 1: Start the Process
@app.route('/', methods=['GET', 'POST'])
def index():
    
    return render_template('index.html')




from flask import jsonify



@app.route('/start_scraper', methods=['GET'])
def start_scraper():
    process = subprocess.Popen(['python3', 'scraper.py','-l'], 
                               stdout=subprocess.PIPE, 
                               text=True)

    output, _ = process.communicate()
    
    # return output
    
    if "Enter the code" in output:
        # Handle the scenario where the script is asking for an access code
        # Redirect to a different route or display a form for entering the access code
        return render_template('enter_code.html')

    # return output
    try:
        groups = json.loads(output)
        return render_template('select_group.html', groups=groups)
    except json.JSONDecodeError:
        return f"Failed to decode JSON: {output}"

    return "Unexpected error occurred"





@app.route('/select_group', methods=['GET', 'POST'])
def select_group():
    if request.method == 'POST':
        selected_group_index = request.form['group_number']
        scrape_admins = '-a' if 'scrape_admins' in request.form else ''
        
        input_data = f"{selected_group_index}\n"
        
        # Run scraper.py with the selected group index
        process = subprocess.Popen(['python3', 'scraper.py',scrape_admins], 
                                    text=True,
                                    stdin=subprocess.PIPE, 
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                   
                                   )

        output, _ = process.communicate(input=input_data)

        # Handle the output of scraper.py here
        # For example, you might want to show a confirmation message or the results of scraping
        if "Members scraped successfully" in output:
            return render_template('results.html', result="false")
        
        return render_template('results.html', result=output)

    # Retrieve and display available groups
    process = subprocess.Popen(['python3', 'scraper.py'], 
                               stdout=subprocess.PIPE, 
                               text=True)

    output, _ = process.communicate()
    try:
        groups = json.loads(output)
        return render_template('select_group.html', groups=groups)
    except json.JSONDecodeError:
        return f"Failed to decode JSON: {output}"

    return "Unexpected error occurred"




# @app.route('/update_credentials', methods=['GET', 'POST'])
# def update_credentials():
#     if request.method == 'POST':
#         # Store credentials in session
#         session['api_id'] = request.form['api_id']
#         session['api_hash'] = request.form['api_hash']
#         session['phone'] = request.form['phone']

#         # Run the setup script with initial credentials
#         process = subprocess.Popen(['python3', 'setup.py', '-c'],
#                                    stdin=subprocess.PIPE, 
#                                    stdout=subprocess.PIPE,
#                                    stderr=subprocess.PIPE, 
#                                    text=True)

#         # Send the credentials to the script
#         credentials_input = f"{session['api_id']}\n{session['api_hash']}\n{session['phone']}\n"

#         return output  # or render a template with the output
#     return render_template('update_credentials.html')


@app.route('/update_credentials', methods=['GET', 'POST'])
def update_credentials():
    if request.method == 'POST':
        api_id = request.form['api_id']
        api_hash = request.form['api_hash']
        phone = request.form['phone']
        
        # Prepare the input string as expected by the script
        input_data = f"{api_id}\n{api_hash}\n{phone}\n"
        result = subprocess.run(['python3', 'setup.py', '-c'], 
                                input=input_data, 
                                text=True, 
                                stdout=subprocess.PIPE, 
                                stderr=subprocess.PIPE)
        
        # Capture output and errors
        output = result.stdout
        error = result.stderr

        if error:
            return f'Error: {error}'
        return redirect(url_for('index'))

    
    return render_template('update_credentials.html')


@app.route('/enter_passcode', methods=['POST'])
def enter_passcode():
    passcode = request.form['passcode']

    process = subprocess.Popen(['python3', 'scraper.py','-l','-s'], 
                               stdin=subprocess.PIPE, 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE, 
                               text=True)

    # Send the passcode to scraper.py
    output, _ = process.communicate(input=passcode)

    try:
        # Try to parse the output as JSON and extract groups
        groups = json.loads(output)
        return render_template('select_group.html', groups=groups)
    except json.JSONDecodeError:
        # If JSON decoding fails, return the raw output
        return f"Failed to decode JSON: {output}"

    return "Unexpected error occurred"

@app.route('/add_members', methods=['GET'])
def add_members():
    process = subprocess.Popen(['python3', 'scraper.py', '-l'], 
                               stdout=subprocess.PIPE, 
                               text=True)

    output, _ = process.communicate()

    try:
        groups = json.loads(output)
        return render_template('add_members.html', groups=groups)
    except json.JSONDecodeError:
        return f"Failed to decode JSON: {output}"

    return "Unexpected error occurred"

@app.route('/perform_add_members', methods=['POST'])
def perform_add_members():
    selected_group_id = request.form['selected_group']
    input_data = f"{selected_group_id}\n"
    
    
    
    # Here you will need to call add2group.py with the selected group ID
    # Ensure add2group.py is capable of handling this ID as an argument
    process = subprocess.Popen(['python3', 'add2group.py', "members.csv"], 
                               stdout=subprocess.PIPE,
                               stdin=subprocess.PIPE, 
                               text=True)

    output, _ = process.communicate(input=input_data)

    # Handle the output from add2group.py here
    return render_template('add_members_result.html', result=output)






if __name__ == '__main__':
    app.run(debug=True)
