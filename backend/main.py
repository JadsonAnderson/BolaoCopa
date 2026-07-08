import requests
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import List

# ==================== CONFIGURAÇÃO DO BANCO DE DADOS ====================
DATABASE_URL = "sqlite:///./bolao.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ==================== MODELOS DO BANCO DE DADOS (SQLAlchemy) ====================
class PartidaModel(Base):
    __tablename__ = "partidas"
    id = Column(Integer, primary_key=True, index=True)
    time_a = Column(String, nullable=False)
    time_b = Column(String, nullable=False)
    bandeira_a = Column(String, nullable=False)
    bandeira_b = Column(String, nullable=False)
    data_jogo = Column(String, nullable=False)

class PalpiteModel(Base):
    __tablename__ = "palpites"
    partida_id = Column(Integer, primary_key=True, index=True) # 1 palpite por partida
    gols_a = Column(Integer, nullable=False)
    gols_b = Column(Integer, nullable=False)

# Criar as tabelas no arquivo bolao.db se elas não existirem
Base.metadata.create_all(bind=engine)

# ==================== ESQUEMAS DE DADOS (Pydantic para o JSON) ====================
class PalpiteSchema(BaseModel):
    partida_id: int
    gols_a: int
    gols_b: int

    class Config:
        from_attributes = True

# Dependency para abrir e fechar a conexão com o banco por requisição
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==================== INICIALIZAÇÃO DA API ====================
app = FastAPI()

# ==================== CONFIGURAÇÃO DA API EXTERNA DE ESPORTES ====================
API_URL = "https://v3.football.api-sports.io/fixtures"
API_HEADERS = {
    "x-rapidapi-host": "v3.football.api-sports.io",
    "x-rapidapi-key": "INSIRA_SUA_CHAVE_AQUI" # Se tiver chave da api-football, coloque aqui
}

def popular_banco_fallback(db: Session):
    """Injeta os confrontos reais e válidos do mata-mata atualizado caso a API falhe ou falte chave"""
    print("⚠️ Usando dados de contingência atualizados do mata-mata...")
    jogos = [
        PartidaModel(id=101, time_a="Brasil", time_b="Noruega", bandeira_a="https://flagcdn.com/w320/br.png", bandeira_b="https://flagcdn.com/w320/no.png", data_jogo="Oitavas de Final"),
        PartidaModel(id=102, time_a="México", time_b="Inglaterra", bandeira_a="https://flagcdn.com/w320/mx.png", bandeira_b="https://flagcdn.com/w320/gb-eng.png", data_jogo="Oitavas de Final"),
        PartidaModel(id=103, time_a="Portugal", time_b="Espanha", bandeira_a="https://flagcdn.com/w320/pt.png", bandeira_b="https://flagcdn.com/w320/es.png", data_jogo="Oitavas de Final"),
        PartidaModel(id=104, time_a="Estados Unidos", time_b="Bélgica", bandeira_a="https://flagcdn.com/w320/us.png", bandeira_b="https://flagcdn.com/w320/be.png", data_jogo="Oitavas de Final"),
        PartidaModel(id=105, time_a="Argentina", time_b="Egito", bandeira_a="https://flagcdn.com/w320/ar.png", bandeira_b="https://flagcdn.com/w320/eg.png", data_jogo="Oitavas de Final")
    ]
    db.add_all(jogos)
    db.commit()
    print("✅ Jogos de contingência inseridos com sucesso!")

# ==================== SINCRONIZAÇÃO DINÂMICA NO STARTUP ====================
@app.on_event("startup")
def sincronizar_jogos_reais_copa():
    db = SessionLocal()
    
    # Se o banco já possuir partidas cadastradas, pula para evitar duplicados
    if db.query(PartidaModel).count() > 0:
        db.close()
        return

    # Se você não alterou a chave da API, vai direto para o plano B (Fallback Realista)
    if API_HEADERS["x-rapidapi-key"] == "INSIRA_SUA_CHAVE_AQUI":
        popular_banco_fallback(db)
        db.close()
        return

    print("🔄 Conectando à API externa para capturar os confrontos em tempo real da Copa 2026...")
    params = {
        "league": "1",    # ID padrão da Copa do Mundo na API-Football
        "season": "2026"
    }

    try:
        response = requests.get(API_URL, headers=API_HEADERS, params=params, timeout=10)
        if response.status_code == 200:
            dados = response.json().get("response", [])
            jogos_para_salvar = []
            
            for item in dados:
                fixture = item.get("fixture", {})
                teams = item.get("teams", {})
                status = fixture.get("status", {}).get("short")
                
                # Sincroniza apenas partidas futuras ("Not Started") onde o palpite é permitido
                if status == "NS":
                    novo_jogo = PartidaModel(
                        id=fixture.get("id"),
                        time_a=teams.get("home", {}).get("name"),
                        time_b=teams.get("away", {}).get("name"),
                        bandeira_a=teams.get("home", {}).get("logo"),
                        bandeira_b=teams.get("away", {}).get("logo"),
                        data_jogo=fixture.get("date")[:10]  # Formato YYYY-MM-DD
                    )
                    jogos_para_salvar.append(novo_jogo)
            
            if jogos_para_salvar:
                db.add_all(jogos_para_salvar)
                db.commit()
                print(f"✅ {len(jogos_para_salvar)} jogos oficiais da Copa sincronizados dinamicamente!")
            else:
                print("⚠️ Nenhum jogo futuro pendente na API. Ativando contingência...")
                popular_banco_fallback(db)
        else:
            print(f"❌ Falha na API Externa (Status {response.status_code}). Ativando fallback...")
            popular_banco_fallback(db)
            
    except Exception as e:
        print(f"❌ Erro de conexão de rede: {str(e)}")
        popular_banco_fallback(db)
        
    db.close()

# ==================== ROTAS HTTP (ENDPOINTS) ====================

# GET: Listar partidas
@app.get("/partidas")
def listar_partidas(db: Session = Depends(get_db)):
    return db.query(PartidaModel).all()

# GET: Listar palpites salvos
@app.get("/palpites")
def listar_palpites(db: Session = Depends(get_db)):
    return db.query(PalpiteModel).all()

# POST: Criar palpite
@app.post("/palpites")
def criar_palpite(palpite: PalpiteSchema, db: Session = Depends(get_db)):
    db_palpite = db.query(PalpiteModel).filter(PalpiteModel.partida_id == palpite.partida_id).first()
    if db_palpite:
        raise HTTPException(status_code=400, detail="Palpite já existente. Use PUT para atualizar.")
    
    novo_palpite = PalpiteModel(partida_id=palpite.partida_id, gols_a=palpite.gols_a, gols_b=palpite.gols_b)
    db.add(novo_palpite)
    db.commit()
    return {"status": "Palpite gravado no banco SQLite!"}

# PUT: Atualizar palpite
@app.put("/palpites/{partida_id}")
def atualizar_palpite(partida_id: int, palpite_atualizado: PalpiteSchema, db: Session = Depends(get_db)):
    db_palpite = db.query(PalpiteModel).filter(PalpiteModel.partida_id == partida_id).first()
    if not db_palpite:
        raise HTTPException(status_code=404, detail="Palpite não encontrado.")
    
    db_palpite.gols_a = palpite_atualizado.gols_a
    db_palpite.gols_b = palpite_atualizado.gols_b
    db.commit()
    return {"status": "Palpite updated no banco!"}

# DELETE: Deletar palpite
@app.delete("/palpites/{partida_id}")
def deletar_palpite(partida_id: int, db: Session = Depends(get_db)):
    db_palpite = db.query(PalpiteModel).filter(PalpiteModel.partida_id == partida_id).first()
    if not db_palpite:
        raise HTTPException(status_code=404, detail="Palpite não encontrado.")
    
    db.delete(db_palpite)
    db.commit()
    return {"status": "Palpite removido do banco!"}