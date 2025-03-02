# tools/database.py
import os
from neo4j import GraphDatabase
from dotenv import load_dotenv
load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "neo4j")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def get_db():
    return driver.session()

def close_db():
    driver.close()

def init_db():
    """
    Neo4j 5.x için güncellenmiş constraint sözdizimi:
    CREATE CONSTRAINT constraint_name IF NOT EXISTS
    FOR (node:Label) REQUIRE node.property IS UNIQUE
    """
    session = get_db()
    try:
        # School için constraint
        session.run("""
        CREATE CONSTRAINT school_id_unique IF NOT EXISTS
        FOR (s:School)
        REQUIRE s.school_id IS UNIQUE
        """)
        # User için constraint (user_id)
        session.run("""
        CREATE CONSTRAINT user_id_unique IF NOT EXISTS
        FOR (u:User)
        REQUIRE u.user_id IS UNIQUE
        """)
        # User için ek: username benzersiz constraint
        session.run("""
        CREATE CONSTRAINT user_username_unique IF NOT EXISTS
        FOR (u:User)
        REQUIRE u.username IS UNIQUE
        """)
        # Question için constraint
        session.run("""
        CREATE CONSTRAINT question_id_unique IF NOT EXISTS
        FOR (q:Question)
        REQUIRE q.id IS UNIQUE
        """)
        # Choice için constraint
        session.run("""
        CREATE CONSTRAINT choice_id_unique IF NOT EXISTS
        FOR (c:Choice)
        REQUIRE c.id IS UNIQUE
        """)
        # Exam için constraint
        session.run("""
        CREATE CONSTRAINT exam_id_unique IF NOT EXISTS
        FOR (e:Exam)
        REQUIRE e.exam_id IS UNIQUE
        """)
        # ExamAnswer için constraint
        session.run("""
        CREATE CONSTRAINT examAnswer_id_unique IF NOT EXISTS
        FOR (ea:ExamAnswer)
        REQUIRE ea.id IS UNIQUE
        """)
        # Statistics için constraint
        session.run("""
        CREATE CONSTRAINT statistics_id_unique IF NOT EXISTS
        FOR (st:Statistics)
        REQUIRE st.id IS UNIQUE
        """)
        # Section için constraint
        session.run("""
        CREATE CONSTRAINT section_unique IF NOT EXISTS
        FOR (s:Section)
        REQUIRE s.section_number IS UNIQUE
        """)
        # Class için constraint
        session.run("""
        CREATE CONSTRAINT class_unique IF NOT EXISTS
        FOR (c:Class)
        REQUIRE c.name IS UNIQUE
        """)
    finally:
        session.close()
