import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "database.db"


def criar_banco():
    conexao = sqlite3.connect(DATABASE_PATH)

    cursor = conexao.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
                                             id INTEGER PRIMARY KEY AUTOINCREMENT,
                                             username TEXT NOT NULL UNIQUE,
                                             password TEXT NOT NULL
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS predictions (
                                                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                   texto TEXT NOT NULL,
                                                   intencao TEXT NOT NULL,
                                                   owner_id INTEGER NOT NULL,
                                                   FOREIGN KEY (owner_id) REFERENCES users (id)
            )
        """
    )

    cursor.execute(
        """
        INSERT OR IGNORE INTO users (id, username, password)
        VALUES (1, 'admin', 'infnet')
        """
    )

    cursor.execute(
        """
        INSERT OR IGNORE INTO users (id, username, password)
        VALUES (2, 'usuario2', 'teste123')
        """
    )

    cursor.execute(
        """
        INSERT OR IGNORE INTO predictions (
            id,
            texto,
            intencao,
            owner_id
        )
        VALUES (
            1,
            'Quero meu dinheiro de volta',
            'Refund request',
            1
        )
        """
    )

    cursor.execute(
        """
        INSERT OR IGNORE INTO predictions (
            id,
            texto,
            intencao,
            owner_id
        )
        VALUES (
            2,
            'Meu produto ainda não chegou',
            'Delivery issue',
            2
        )
        """
    )

    conexao.commit()
    conexao.close()

    print("Banco database.db criado e populado com sucesso.")


if __name__ == "__main__":
    criar_banco()