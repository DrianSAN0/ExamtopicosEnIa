import dspy, sqlite3
from dotenv import load_dotenv
from tools import execute_sql, get_schema, export_shipping_manifest

class LogisticsAgentSignature(dspy.Signature):
    '''
    Eres un asistente logistico para gestion de inventarios en almacenes.
    SIEMPRE verifica el campo status antes de confirmar disponibilidad.
    Solo status=AVAILABLE significa disponible. status=DAMAGED no esta disponible.
    Usa get_schema antes de ejecutar SQL. Solo ejecuta SELECT. Responde en espanol.
    '''
    question = dspy.InputField(desc='Pregunta sobre inventario o almacenes.')
    initial_schema = dspy.InputField(desc='Esquema de la base de datos logistica.')
    answer = dspy.OutputField(desc='Respuesta al operario.')

class LogisticsAgent(dspy.Module):
    def __init__(self, tools):
        super().__init__()
        self.agent = dspy.ReAct(LogisticsAgentSignature, tools=tools, max_iters=7)
    def forward(self, question, initial_schema):
        return self.agent(question=question, initial_schema=initial_schema)

def configure_llm():
    load_dotenv()
    lm = dspy.LM(model='openai/gpt-4o-mini', max_tokens=4000)
    dspy.settings.configure(lm=lm)

def create_agent(conn: sqlite3.Connection, query_history=None):
    configure_llm()
    tools = [
        dspy.Tool(name='execute_sql',
            desc='Ejecuta SELECT sobre la BD logistica. No permite escritura.',
            func=lambda query: execute_sql(conn, query, query_history)),
        dspy.Tool(name='get_schema',
            desc='Devuelve esquema de tablas. Sin argumento lista todas las tablas. Con nombre de tabla, devuelve sus columnas.',
            func=lambda table_name='': get_schema(conn, table_name or None)),
        dspy.Tool(name='export_shipping_manifest',
            desc='Exporta lista de productos (SKU, nombre, cantidad) a CSV. Recibe data:list y filename:str.',
            func=export_shipping_manifest),
    ]
    return LogisticsAgent(tools=tools)
