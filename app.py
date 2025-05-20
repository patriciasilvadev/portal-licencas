from flask import Flask, request, jsonify, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
import uuid

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///licencas.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Modelo da tabela de licenças
class Licenca(db.Model):
    id = db.Column(db.String(12), primary_key=True)
    usuario = db.Column(db.String(100), nullable=False)
    hardware_id = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(10), default="ativo")
    data_criacao = db.Column(db.DateTime, default=db.func.current_timestamp())

with app.app_context():
    db.create_all()

# Página inicial
@app.route("/")
def index():
    return render_template("gerar_licenca.html")

# Geração de licença
@app.route("/gerar_licenca", methods=["GET", "POST"])
def gerar_licenca():
    if request.method == "POST":
        usuario = request.form.get("usuario")
        hardware_id = request.form.get("hardware_id")

        if not usuario or not hardware_id:
            return jsonify({"erro": "Dados incompletos"}), 400

        chave_licenca = uuid.uuid4().hex[:12].upper()
        nova_licenca = Licenca(id=chave_licenca, usuario=usuario, hardware_id=hardware_id)
        db.session.add(nova_licenca)
        db.session.commit()

        return render_template("licenca_gerada.html", usuario=usuario, hardware_id=hardware_id, licenca=chave_licenca)

    return render_template("gerar_licenca.html")

# Validação de licença
@app.route("/validar_licenca", methods=["POST"])
def validar_licenca():
    dados = request.get_json()
    chave_licenca = dados.get("licenca")

    licenca = Licenca.query.filter_by(id=chave_licenca).first()
    if licenca:
        return jsonify({"valido": licenca.status == "ativo"})

    return jsonify({"valido": False, "erro": "Licença não encontrada!"}), 404


# Painel administrativo
@app.route("/admin")
def admin_panel():
    licencas = Licenca.query.all()
    return render_template("admin_panel.html", licencas=licencas)

# Alteração de status da licença (Ativar/Bloquear)
@app.route("/alterar_status", methods=["POST"])
def alterar_status():
    licenca_id = request.form.get("licenca_id")
    novo_status = request.form.get("novo_status")

    licenca = Licenca.query.filter_by(id=licenca_id).first()
    if licenca:
        licenca.status = novo_status
        db.session.commit()

    return redirect("/admin")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
