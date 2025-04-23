from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/consulta-fornecedor")
def consultar_fornecedor(cnpj: str = Query(..., description="CNPJ apenas com números")):
    url = "https://compras.dados.gov.br/fornecedores/v1/fornecedor_pj.json"
    params = {"cnpj": cnpj}
    response = requests.get(url, params=params)

    if response.status_code != 200:
        return {"erro": "Fornecedor não encontrado ou erro na API."}

    data = response.json().get("resultado", {})

    return {
        "nome": data.get("nome", "Desconhecido"),
        "cnpj": cnpj,
        "natureza_juridica": data.get("natureza_juridica", "N/D"),
        "atividade_principal": data.get("atividade_principal", "N/D")
    }
