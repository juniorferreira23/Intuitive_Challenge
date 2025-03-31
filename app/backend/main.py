from config import DB_USER, DB_PASSWORD, DB_NAME, DB_HOST
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import databases
from pydantic import BaseModel

app = FastAPI()

origins = [
    "http://localhost:5173", 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"], 
)

DATABASE_URL = f"mysql+aiomysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

db = databases.Database(DATABASE_URL)


class Search(BaseModel):
    registro_ans: str | None = None
    cnpj: str | None = None
    razao_social: str | None = None
    cidade: str | None = None


def build_query(registro_ans=None, cnpj=None, razao_social=None, cidade=None):
    base_query = "SELECT * FROM operadoras"
    conditions = []
    params = {}

    if registro_ans:
        conditions.append("registro_ans = :registro_ans")
        params["registro_ans"] = registro_ans

    if cnpj:
        conditions.append("cnpj = :cnpj")
        params["cnpj"] = cnpj

    if razao_social:
        conditions.append("razao_social LIKE :razao_social")
        params["razao_social"] = f"%{razao_social}%"  

    if cidade:
        conditions.append("cidade LIKE :cidade")
        params["cidade"] = f"%{cidade}%"

    if conditions:
        base_query += " WHERE " + " AND ".join(conditions)

    base_query += " ORDER BY data_registro_ans DESC LIMIT 10"

    return base_query, params


@app.on_event("startup")
async def startup():
    """Conecta ao banco de dados quando a API inicia"""
    try:
        await db.connect()
        print("✅ Conexão bem-sucedida!")

        query = "SELECT * FROM operadoras LIMIT 1;"
        result = await db.fetch_one(query)
        print("Teste de consulta:", result)

    except Exception as e:
        print("❌ Erro na conexão:", str(e))


@app.on_event("shutdown")
async def shutdown():
    """Desconecta do banco de dados ao desligar a API"""
    await db.disconnect()
    print("🔌 Conexão com o banco encerrada.")


@app.get("/")
def read_root():
    return {"message": "Hello, world!"}


@app.post("/search")
async def search(search: Search):
    """Retorna os primeiros 10 registros da tabela operadoras"""

    query, params = build_query(
        registro_ans=search.registro_ans,
        cnpj=search.cnpj,
        razao_social=search.razao_social,
        cidade=search.cidade,
    )

    if not query:
        return {"message": "fail"}

    result = await db.fetch_all(query=query, values=params)
    return {"message": result}
