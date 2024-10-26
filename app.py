from flask import Flask, render_template, request, redirect, url_for, flash, session
from firebase_admin import credentials, firestore, initialize_app

app = Flask(__name__)
app.secret_key = 'ROA@1234'  # Change this to a more secure key

# Initialize Firebase Admin
cred = credentials.Certificate('D:/omkar study/projects/ad/admin_website/static/serviceAccountKey.json')
initialize_app(cred)

db = firestore.client()

@app.route('/')
def home():
    return render_template('login.html')  # Render the login page

@app.route('/admin_login', methods=['POST'])
def admin_login():
    username = request.form['username']
    password = request.form['password']

    if username == 'admin' and password == 'ROA1234':
        session['logged_in'] = True
        return redirect(url_for('all_ngos'))
    else:
        flash('Invalid username or password.')
        return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash("You have successfully logged out.")
    return redirect(url_for('home'))

@app.route('/ngo_requests')
def ngo_requests():
    if not session.get('logged_in'):
        return redirect(url_for('home'))

    ngo_ref = db.collection('NGOs')
    ngos = ngo_ref.stream()
    ngo_list = [{**ngo.to_dict(), 'id': ngo.id} for ngo in ngos]
    return render_template('ngo_requests.html', ngos=ngo_list)

@app.route('/accept_ngos/<ngo_id>', methods=['POST'])
def accept_ngos(ngo_id):
    if not session.get('logged_in'):
        return redirect(url_for('home'))

    # Reference to the NGO document
    ngo_ref = db.collection('NGOs').document(ngo_id)

    # Update the NGO's verified status
    ngo_ref.update({'Verified': 'verify'})  # Change to True for accepted NGOs

    flash("NGO accepted successfully.")
    return redirect(url_for('pending_ngos'))  # Redirect back to pending NGOs page

@app.route('/reject_ngos/<ngo_id>', methods=['POST'])
def reject_ngos(ngo_id):
    if not session.get('logged_in'):
        return redirect(url_for('home'))

    # Reference to the NGO document
    ngo_ref = db.collection('NGOs').document(ngo_id)

    # Optionally delete or mark as rejected, example: 
    ngo_ref.delete()  # This will remove the NGO from the collection (be cautious)

    flash("NGO rejected successfully.")
    return redirect(url_for('pending_ngos'))  # Redirect back to pending NGOs page


@app.route('/all_ngos')
def all_ngos():
    if not session.get('logged_in'):
        return redirect(url_for('home'))

    ngo_ref = db.collection('NGOs')
    ngos = ngo_ref.stream()
    ngo_list = [{**ngo.to_dict(), 'id': ngo.id} for ngo in ngos]
    return render_template('all_ngos.html', ngos=ngo_list)

@app.route('/accepted_ngos')
def accepted_ngos():
    if not session.get('logged_in'):
        return redirect(url_for('home'))

    ngo_ref = db.collection('NGOs')
    ngos = ngo_ref.where('Verified', '==', 'verify').stream()
    ngo_list = [{**ngo.to_dict(), 'id': ngo.id} for ngo in ngos]
    return render_template('accepted_ngos.html', ngos=ngo_list)

@app.route('/pending_ngos')
def pending_ngos():
    if not session.get('logged_in'):
        return redirect(url_for('home'))

    ngo_ref = db.collection('NGOs')
    ngos = ngo_ref.where('Verified', '==', 'uvs').stream()
    ngo_list = [{**ngo.to_dict(), 'id': ngo.id} for ngo in ngos]
    return render_template('pending_ngos.html', ngos=ngo_list)

@app.route('/delete_donor/<donor_id>', methods=['POST'])
def delete_donor(donor_id):
    if not session.get('logged_in'):
        return redirect(url_for('home'))

    # Delete the donor from the Firestore collection
    donor_ref = db.collection('donors').document(donor_id)
    donor_ref.delete()

    # Flash a message and redirect back to the all donors page
    flash('Donor deleted successfully!', 'success')
    return redirect(url_for('all_donors'))


@app.route('/all_donors')
def all_donors():
    if not session.get('logged_in'):
        return redirect(url_for('home'))

    # Fetch all donors from Firestore
    donor_ref = db.collection('donors')
    all_donors = donor_ref.stream()

    # Convert donor documents to a list
    donor_list = [{**donor.to_dict(), 'id': donor.id} for donor in all_donors]
    return render_template('all_donors.html', donors=donor_list)

if __name__ == '__main__':
    app.run(debug=True)
