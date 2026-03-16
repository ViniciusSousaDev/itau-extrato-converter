from flask import Flask, render_template, request, send_file
import pandas as pd
import pdfplumber
import re
from io import BytesIO

app = Flask(__name__)

def extrair_lancamentos(pdf_file):
    linhas = []

    with pdfplumber.open(pdf_file) as pdf:
        texto = ""
        for page in pdf.pages:
            texto += page.extract_text() + "\n"

    pattern = r'(\d{2}/\d{2}/\d{4}).*?(-?\d+\.\d{3},\d{2}|-?\d+,\d{2})'

    for line in texto.split("\n"):
        match = re.search(pattern, line)
        if match:
            data = match.group(1)
            valor = match.group(2)

            valor = valor.replace(".", "").replace(",", ".")
            valor = float(valor)

            descricao = line.replace(data, "").replace(match.group(2), "").strip()

            linhas.append({
                "A": data,
                "B": "",
                "C": "",
                "D": valor,
                "E": descricao
            })

    df = pd.DataFrame(linhas)

    return df


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":

        file = request.files["file"]
        formato = request.form["format"]

        df = extrair_lancamentos(file)

        buffer = BytesIO()

        if formato == "csv":
            df.to_csv(buffer, index=False, header=False)
            buffer.seek(0)
            return send_file(buffer, download_name="extrato.csv", as_attachment=True)

        if formato == "xlsx":
            df.to_excel(buffer, index=False, header=False)
            buffer.seek(0)
            return send_file(buffer, download_name="extrato.xlsx", as_attachment=True)

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)