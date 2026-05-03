import ast, sqlite3, uuid
from typing import Annotated
from fastapi import FastAPI, Depends, Body, BackgroundTasks
import dspy
from pydantic import BaseModel
from database import setup_database
from tools import get_schema, execute_sql
from agent import create_agent

app = FastAPI(title='Logistics AI Assistant')

class AgentResponse(BaseModel):
    original_query: str
    sql_queries: list[str]
    agent_answer: str

class AgentAsyncStartResponse(BaseModel):
    query_id: uuid.UUID
    status: str = 'pending'

class AgentAsyncFinishResponse(AgentResponse):
    query_id: uuid.UUID
    status: str = 'finished'

def get_db_connection():
    return setup_database()

def get_db_schema(conn: Annotated[sqlite3.Connection, Depends(get_db_connection)]) -> str:
    return get_schema(conn)

def query_agent(agent, user_query, db_schema, query_history, track_query=False, query_id=None, db_conn=None):
    outputs = agent(question=user_query, initial_schema=db_schema)
    results = AgentResponse(original_query=user_query, sql_queries=list(query_history), agent_answer=outputs.answer)
    if track_query and query_id and db_conn:
        rj = results.model_dump_json().replace("'", "''")
        execute_sql(db_conn, f"UPDATE queries SET result='{rj}', status='finished' WHERE id='{query_id}';")
    return results

@app.post('/logistics/queries')
def query_logistics(db_schema: Annotated[str, Depends(get_db_schema)],
                    db_conn: Annotated[sqlite3.Connection, Depends(get_db_connection)],
                    user_query: str = Body(..., embed=True)) -> AgentResponse:
    local_history: list[str] = []
    agent = create_agent(db_conn, local_history)
    return query_agent(agent, user_query, db_schema, local_history)

@app.post('/logistics/async_queries')
def async_query_logistics(db_schema: Annotated[str, Depends(get_db_schema)],
                           background_tasks: BackgroundTasks,
                           db_conn: Annotated[sqlite3.Connection, Depends(get_db_connection)],
                           user_query: str = Body(..., embed=True)) -> AgentAsyncStartResponse:
    query_id = uuid.uuid4()
    local_history: list[str] = []
    agent = create_agent(db_conn, local_history)
    execute_sql(db_conn, f"INSERT INTO queries (id, status, result) VALUES ('{query_id}', 'pending', '')")
    background_tasks.add_task(query_agent, agent, user_query, db_schema, local_history, True, query_id, db_conn)
    return AgentAsyncStartResponse(query_id=query_id)

@app.get('/logistics/async_queries')
def get_async_query_result(db_conn: Annotated[sqlite3.Connection, Depends(get_db_connection)],
                            query_id: uuid.UUID) -> AgentAsyncStartResponse | AgentAsyncFinishResponse:
    result = execute_sql(db_conn, f"SELECT * FROM queries WHERE id = '{query_id}'")
    rows = ast.literal_eval(result)
    if not rows or not rows[0][2]:
        return AgentAsyncStartResponse(query_id=query_id, status='pending')
    response = AgentResponse.model_validate_json(rows[0][2])
    return AgentAsyncFinishResponse(**response.model_dump(), query_id=query_id)
