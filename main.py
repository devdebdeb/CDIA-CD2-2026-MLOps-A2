from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from datetime import datetime

app = FastAPI(
    title="Bella Tavola API",
    description="API do restaurante Bella Tavola",
    version="1.0.1"
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            'erro': 'Dados Inválidos'
            ,'detalhes': exc.errors
            ,'path': str(request.url)
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code
        ,content={
            'erro': exc.detail
            ,'status': exc.status_code
            ,'path': str(request.url)
        }
)

class PratoInput(BaseModel):
    nome: str = Field(min_length=3,max_length=100)
    categoria: str = Field(pattern="^(pizza|massa|sobremesa|entrada|salada)$")
    preco: float = Field(gt=0)
    descricao: Optional[str] = Field(default=None, max_length=500)
    disponivel: bool = True
    preco_promocional: Optional[float] = None

    @field_validator("preco_promocional")
    @classmethod
    def preco_promocional_menor_que_preco(cls, v, info):
        if "preco" in info.data and v >= info.data['preco']:
            raise ValueError("Preço promocional deve ser menor que o preço original")
        if "preco" in info.data and v/info.data['preco'] >= 2:
            raise ValueError("O desconto não pode ser maior que 50 porcento do preço original")
        return v
    
class PratoOutput(BaseModel):
    id: int
    nome: str
    categoria: str
    preco: float 
    descricao: Optional[str]
    disponivel: bool
    criado_em: str

class BebidaInput(BaseModel):
    nome: str = Field(min_length=3, max_length=100)
    tipo: str = Field(pattern="^(vinho|agua|refrigerante|suco|cerveja)$")
    preco: float = Field(gt=0)
    alcoolica: bool
    volume_ml: int = Field(ge=50, le=2000)

class BebidaOutput(BaseModel):
    id: int
    nome: str
    tipo: str
    preco: float
    alcoolica: bool
    volume_ml: int
    criado_em: str

@app.get("/")
async def root():
    return {
        "restaurante": "Bella Tavola",
        "mensagem": "Bem-vindo à nossa API"
    }

pratos = [
    {"id": 1, "nome": "Margherita", "categoria": "pizza", "preco": 45.0, "disponivel": True},
    {"id": 2, "nome": "Carbonara", "categoria": "massa", "preco": 52.0, "disponivel": True},
    {"id": 3, "nome": "Lasanha Bolonhesa", "categoria": "massa", "preco": 58.0, "disponivel": False},
    {"id": 4, "nome": "Tiramisù", "categoria": "sobremesa", "preco": 28.0, "disponivel": True},
    {"id": 5, "nome": "Quattro Stagioni", "categoria": "pizza", "preco": 49.0, "disponivel": True},
    {"id": 6, "nome": "Panna Cotta", "categoria": "sobremesa", "preco": 24.0, "disponivel": False},
]

@app.get("/pratos")
async def listar_pratos(
    categoria: Optional[str] = None,
    preco_maximo: Optional[float] = None,
    apenas_disponiveis: bool = False
):
    resultado = pratos
    if categoria:
        resultado = [p for p in resultado if p["categoria"] == categoria]
    if preco_maximo:
        resultado = [p for p in resultado if p["preco"] <= preco_maximo]
    if apenas_disponiveis:
        resultado = [p for p in resultado if p["disponivel"]]
    return resultado

@app.get("/pratos/{prato_id}")
async def buscar_prato(prato_id: int):
    for prato in pratos:
        if prato["id"] == prato_id:
            return prato
    raise HTTPException(
            status_code=404,
            detail=f"Prato com id {prato_id} não encontrado"
    )

@app.post("/pratos", response_model=PratoOutput)
async def criar_prato(prato: PratoInput):
    novo_id = max(p["id"] for p in pratos) + 1
    novo_prato = {
        "id": novo_id,
        "criado_em": datetime.now().isoformat(),
        **prato.model_dump()
    }
    pratos.append(novo_prato)
    return novo_prato

bebidas = [
    {"id": 1, "nome": "Água Mineral", "tipo": "agua", "preco": 8.0, "alcoolica": False, "volume_ml": 500, "criado_em": "2024-01-01T00:00:00"},
    {"id": 2, "nome": "Chianti Classico", "tipo": "vinho", "preco": 120.0, "alcoolica": True, "volume_ml": 750, "criado_em": "2024-01-01T00:00:00"},
    {"id": 3, "nome": "San Pellegrino", "tipo": "agua", "preco": 15.0, "alcoolica": False, "volume_ml": 750, "criado_em": "2024-01-01T00:00:00"},
    {"id": 4, "nome": "Suco de Laranja", "tipo": "suco", "preco": 18.0, "alcoolica": False, "volume_ml": 300, "criado_em": "2024-01-01T00:00:00"},
    {"id": 5, "nome": "Prosecco", "tipo": "vinho", "preco": 95.0, "alcoolica": True, "volume_ml": 750, "criado_em": "2024-01-01T00:00:00"},
]

@app.get("/bebidas")
async def listar_bebidas(
    tipo: Optional[str] = None,
    alcoolica: Optional[bool] = None
):
    resultado = bebidas
    if tipo:
        resultado = [p for p in resultado if p["tipo"] == tipo]
    if alcoolica:
        resultado = [p for p in resultado if p["alcoolica"]]
    return resultado

@app.get("/bebidas/{bebida_id}")
async def buscar_bebida(bebida_id: int):
    for bebida in bebidas:
        if bebida['id'] == bebida_id:
            return bebida
    raise HTTPException(
       status_code=404,
       detail=f"Prato com id {bebida_id} não encontrado"
   )

@app.post("/bebidas", response_model=BebidaOutput)
async def criar_bebida(bebida: BebidaInput):
    novo_id = max(b["id"] for b in bebidas) + 1
    nova_bebida = {
        "id": novo_id,
        "criado_em": datetime.now().isoformat(),
        **bebida.model_dump()
    }
    bebidas.append(nova_bebida)
    return nova_bebida

@app.put("/pratos/{prato_id}/disponibilidade")
async def update_disponibilidade(prato_id: int):
    prato = next((p for p in pratos if p["id"] == prato_id), None)
    if not prato:
        raise HTTPException(status_code=404, detail="Prato não encontrado")
    if not prato['disponivel']:
        raise HTTPException(status_code=400, detail="Prato já está indisponível")
    prato['disponivel'] = False
    return prato

pedidos = []

class PedidoInput(BaseModel):
    prato_id: int
    quantidade: int = Field(ge=1)
    observacao: Optional[str] = None

class PedidoOutput(BaseModel):
    id: int
    prato_id: int
    nome_prato: str
    quantidade: int
    valor_total: float
    observacao: Optional[str]

@app.post("/pedidos", response_model=PedidoOutput)
async def criar_pedido(pedido: PedidoInput):
    prato = next((p for p in pratos if p['id'] == pedido.prato_id), None)
    if not prato:
        raise HTTPException(status_code=404, detail="Prato não encontrado")
    if not prato["disponivel"]:
        raise HTTPException(
            status_code=400,
            detail=f"O prato '{prato['nome']}' não está disponível no momento"
        )
    
    novo_id = len(pedidos) + 1
    novo_pedido = {
        'id': novo_id,
        'prato_id': pedido.prato_id,
        'nome_prato': prato['nome'],
        'quantidade':pedido.quantidade,
        'valor_total': prato['preco'] * pedido.quantidade,
        'observacao': pedido.observacao
    }
    pedidos.append(novo_pedido)
    return novo_pedido