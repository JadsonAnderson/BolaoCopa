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
    "x-rapidapi-key": "INSIRA_SUA_CHAVE_AQUI" # A chave da api-football é colocada aqui
}

def popular_banco_fallback(db: Session):
    """Injeta os confrontos REAIS e oficiais das QUARTAS DE FINAL da Copa 2026"""
    print("⚠️ Usando os dados REAIS das Quartas de Final da Copa do Mundo 2026...")
    jogos = [
        PartidaModel(
            id=201, 
            time_a="França", 
            time_b="Marrocos", 
            bandeira_a="https://flagcdn.com/w320/fr.png", 
            bandeira_b="https://flagcdn.com/w320/ma.png", 
            data_jogo="Quartas de Final"
        ),
        PartidaModel(
            id=202, 
            time_a="Espanha", 
            time_b="Bélgica", 
            bandeira_a="https://flagcdn.com/w320/es.png", 
            bandeira_b="https://flagcdn.com/w320/be.png", 
            data_jogo="Quartas de Final"
        ),
        PartidaModel(
            id=203, 
            time_a="Noruega", 
            time_b="Inglaterra", 
            bandeira_a="https://flagcdn.com/w320/no.png", 
            bandeira_b="https://flagcdn.com/w320/gb-eng.png", 
            data_jogo="Quartas de Final"
        ),
        PartidaModel(
            id=204, 
            time_a="Argentina", 
            time_b="Suíça", 
            bandeira_a="https://flagcdn.com/w320/ar.png", 
            bandeira_b="https://flagcdn.com/w320/ch.png", 
            data_jogo="Quartas de Final"
        )
    ]
    db.add_all(jogos)
    db.commit()
    print("✅ Confrontos reais inseridos com sucesso!")

# ==================== SINCRONIZAÇÃO 100% AUTOMÁTICA NO STARTUP ====================
@app.on_event("startup")
def sincronizar_jogos_reais_copa():
    db = SessionLocal()
    
    chave_api = API_HEADERS["x-rapidapi-key"]
    if chave_api == "INSIRA_SUA_CHAVE_AQUI":
        # Se não houver chave real, força o uso do fallback atualizado com as Quartas de Final
        if db.query(PartidaModel).count() == 0:
            popular_banco_fallback(db)
        db.close()
        return

    print("🔄 Conectando à API externa para checar atualizações da Copa 2026...")
    params = {
        "league": "1",    
        "season": "2026"
    }

    try:
        response = requests.get(API_URL, headers=API_HEADERS, params=params, timeout=10)
        if response.status_code == 200:
            dados = response.json().get("response", [])
            
            if dados:
                # Estratégia de atualização automática: Limpa as partidas antigas para refletir a nova fase
                db.query(PartidaModel).delete()
                db.commit()
                
                jogos_para_salvar = []
                for item in dados:
                    fixture = item.get("fixture", {})
                    teams = item.get("teams", {})
                    status = fixture.get("status", {}).get("short")
                    league_data = item.get("league", {})
                    
                    # Filtra partidas pendentes (NS)
                    if status == "NS":
                        # Captura e traduz o nome da rodada fornecido dinamicamente pela API
                        rodada = league_data.get("round", "Copa do Mundo")
                        rodada = rodada.replace("Quarter-finals", "Quartas de Final")
                        rodada = rodada.replace("Semi-finals", "Semifinal")
                        rodada = rodada.replace("Final", "Grande Final")
                        rodada = rodada.replace("Round of 16", "Oitavas de Final")

                        novo_jogo = PartidaModel(
                            id=fixture.get("id"),
                            time_a=teams.get("home", {}).get("name"),
                            time_b=teams.get("away", {}).get("name"),
                            bandeira_a=teams.get("home", {}).get("logo"),
                            bandeira_b=teams.get("away", {}).get("logo"),
                            data_jogo=rodada
                        )
                        jogos_para_salvar.append(novo_jogo)
                
                if jogos_para_salvar:
                    db.add_all(jogos_para_salvar)
                    db.commit()
                    print(f"✅ Sucesso! {len(jogos_para_salvar)} jogos da fase atual da Copa sincronizados!")
                    db.close()
                    return
            
            print("⚠️ API externa não retornou novos jogos pendentes. Mantendo dados locais.")
        else:
            print(f"❌ Falha na API Externa (Status {response.status_code}).")
            
    except Exception as e:
        print(f"❌ Erro de conexão de rede: {str(e)}")
        
    # Fallback de segurança caso a tabela esteja limpa e ocorra falhas na requisição
    if db.query(PartidaModel).count() == 0:
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
    return {"status": "Palpite atualizado no banco!"}

# DELETE: Deletar palpite
@app.delete("/palpites/{partida_id}")
def deletar_palpite(partida_id: int, db: Session = Depends(get_db)):
    db_palpite = db.query(PalpiteModel).filter(PalpiteModel.partida_id == partida_id).first()
    if not db_palpite:
        raise HTTPException(status_code=404, detail="Palpite não encontrado.")
    
    db.delete(db_palpite)
    db.commit()
    return {"status": "Palpite removido do banco!"}