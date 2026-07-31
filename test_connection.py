#!/usr/bin/env python3
"""
Script de teste rápido de conexão com PostgreSQL.
Use: python test_connection.py
"""

import os
import sys
from pathlib import Path

# Carregar .env
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / "config" / ".env", override=False)

import psycopg2

def test_connection():
    """Testa conexão com o banco PostgreSQL."""
    
    # Ler credenciais do .env
    host = os.getenv("PG_HOST")
    port = os.getenv("PG_PORT")
    user = os.getenv("PG_USER")
    password = os.getenv("PG_PASSWORD")
    database = os.getenv("PG_DATABASE")
    
    print("=" * 60)
    print("🔍 TESTE DE CONEXÃO - PostgreSQL")
    print("=" * 60)
    print(f"\nCredenciais:")
    print(f"  Host:     {host}")
    print(f"  Porta:    {port}")
    print(f"  Usuário:  {user}")
    print(f"  Banco:    {database}")
    print()
    
    try:
        print("📡 Conectando ao banco...")
        conn = psycopg2.connect(
            host=host,
            port=int(port),
            user=user,
            password=password,
            database=database,
            connect_timeout=10,
        )
        print("✅ Conexão estabelecida com sucesso!\n")
        
        # Testar query simples
        with conn.cursor() as cur:
            cur.execute("SELECT 1 AS test, now() AS timestamp")
            result = cur.fetchone()
            print(f"✅ Query executada: SELECT 1")
            print(f"   Resultado: {result[0]}")
            print(f"   Timestamp: {result[1]}\n")
        
        # Listar bancos
        with conn.cursor() as cur:
            cur.execute(
                "SELECT datname FROM pg_database WHERE datistemplate=false ORDER BY datname"
            )
            databases = cur.fetchall()
            print(f"✅ Bancos disponíveis ({len(databases)}):")
            for db in databases:
                print(f"   - {db[0]}")
            print()
        
        # Versão do PostgreSQL
        with conn.cursor() as cur:
            cur.execute("SELECT version()")
            version = cur.fetchone()[0]
            print(f"✅ PostgreSQL Info:")
            print(f"   {version}\n")
        
        conn.close()
        print("=" * 60)
        print("✨ TUDO OK! Pronto para usar.")
        print("=" * 60)
        return True
        
    except psycopg2.OperationalError as e:
        print(f"\n❌ ERRO DE CONEXÃO:")
        print(f"   {e}\n")
        print("Verifique:")
        print("  • Host e porta corretos")
        print("  • Usuário e senha corretos")
        print("  • PostgreSQL está rodando")
        print("  • Firewall permite acesso\n")
        return False
    except Exception as e:
        print(f"\n❌ ERRO INESPERADO:")
        print(f"   {e}\n")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
