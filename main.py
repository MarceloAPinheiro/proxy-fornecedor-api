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
from typing import Optional
from datetime import datetime

@app.get("/consulta-precos")
def consultar_precos(
    codigo_item_material: str,
    ano: int,
    uf_uasg: Optional[str] = None
):
    data_inicio = f"{ano}-01-01"
    data_fim = f"{ano}-12-31"
    
    base_url = "https://compras.dados.gov.br/licitacoes/v1/itens_preco_praticado.json"
    params = {
        "codigo_item_material": codigo_item_material,
        "data_publicacao_min": data_inicio,
        "data_publicacao_max": data_fim
    }
    if uf_uasg:
        params["uf_uasg"] = uf_uasg

    response = requests.get(base_url, params=params)

    if response.status_code != 200:
        return {"erro": "Erro ao consultar preços na API do Governo."}

    dados = response.json().get("resultado", [])
    if not dados:
        return {"erro": "Nenhum dado encontrado para os filtros informados."}

    valores = [item["valor_unitario"] for item in dados if item.get("valor_unitario")]
    fornecedores = list({item["cnpj_fornecedor"] for item in dados if item.get("cnpj_fornecedor")})
    orgaos = list({item["orgao"] for item in dados if item.get("orgao")})

    valor_medio = round(sum(valores) / len(valores), 2) if valores else None

    return {
        "codigo_item_material": codigo_item_material,
        "ano": ano,
        "uf_uasg": uf_uasg,
        "valor_unitario_medio": valor_medio,
        "quantidade_registros": len(valores),
        "fornecedores_encontrados": fornecedores,
        "orgaos_compradores": orgaos
    }
endpoint /consulta-precos
