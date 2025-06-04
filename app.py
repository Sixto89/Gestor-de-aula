from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gestor.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Grupo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    alumnos = db.relationship('Alumno', backref='grupo', lazy=True)

class Alumno(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    grupo_id = db.Column(db.Integer, db.ForeignKey('grupo.id'), nullable=False)
    asistencias = db.relationship('Asistencia', backref='alumno', lazy=True)
    notas = db.relationship('Nota', backref='alumno', lazy=True)

class Asistencia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, default=datetime.utcnow)
    presente = db.Column(db.Boolean, default=False)
    alumno_id = db.Column(db.Integer, db.ForeignKey('alumno.id'), nullable=False)

class Nota(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    criterio = db.Column(db.String(100), nullable=False)
    instrumento = db.Column(db.String(100), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    alumno_id = db.Column(db.Integer, db.ForeignKey('alumno.id'), nullable=False)

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/')
def index():
    grupos = Grupo.query.all()
    return render_template('index.html', grupos=grupos)

@app.route('/grupo/nuevo', methods=['POST'])
def nuevo_grupo():
    nombre = request.form['nombre']
    db.session.add(Grupo(nombre=nombre))
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/grupo/<int:grupo_id>')
def ver_grupo(grupo_id):
    grupo = Grupo.query.get_or_404(grupo_id)
    return render_template('grupo.html', grupo=grupo)

@app.route('/grupo/<int:grupo_id>/alumno/nuevo', methods=['POST'])
def nuevo_alumno(grupo_id):
    nombre = request.form['nombre']
    db.session.add(Alumno(nombre=nombre, grupo_id=grupo_id))
    db.session.commit()
    return redirect(url_for('ver_grupo', grupo_id=grupo_id))

@app.route('/alumno/<int:alumno_id>/asistencia', methods=['POST'])
def pasar_asistencia(alumno_id):
    presente = 'presente' in request.form
    asistencia = Asistencia(alumno_id=alumno_id, presente=presente, fecha=datetime.utcnow())
    db.session.add(asistencia)
    db.session.commit()
    return redirect(url_for('ver_grupo', grupo_id=Alumno.query.get_or_404(alumno_id).grupo_id))

@app.route('/alumno/<int:alumno_id>/nota', methods=['POST'])
def agregar_nota(alumno_id):
    criterio = request.form['criterio']
    instrumento = request.form['instrumento']
    valor = float(request.form['valor'])
    db.session.add(Nota(criterio=criterio, instrumento=instrumento, valor=valor, alumno_id=alumno_id))
    db.session.commit()
    return redirect(url_for('ver_grupo', grupo_id=Alumno.query.get_or_404(alumno_id).grupo_id))

@app.route('/herramientas')
def herramientas():
    grupos = Grupo.query.all()
    return render_template('herramientas.html', grupos=grupos)

@app.route('/api/grupo/<int:grupo_id>/alumnos')
def api_alumnos(grupo_id):
    grupo = Grupo.query.get_or_404(grupo_id)
    return {
        'alumnos': [
            {'id': alumno.id, 'nombre': alumno.nombre} for alumno in grupo.alumnos
        ]
    }

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
