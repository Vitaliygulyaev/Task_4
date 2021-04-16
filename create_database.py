import sqlite3

conn = sqlite3.connect('newsdb.db')
cur = conn.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS users(
    user_id INT PRIMARY KEY,
    FirstName TEXT,
    SecondName TEXT,
    UNIQUE(user_id));
    """
)
conn.commit()

cur.execute("""CREATE TABLE IF NOT EXISTS categories(
    category_id INT PRIMARY KEY,
    Category TEXT);
    """
)
conn.commit()
cur.execute("INSERT INTO categories(category_id, Category) VALUES(?, ?);", (1, "business"))
conn.commit()
cur.execute("INSERT INTO categories(category_id, Category) VALUES(?, ?);", (2, "general"))
conn.commit()
cur.execute("INSERT INTO categories(category_id, Category) VALUES(?, ?);", (3, "sports"))
conn.commit()
cur.execute("INSERT INTO categories(category_id, Category) VALUES(?, ?);", (4, "science"))
conn.commit()
cur.execute("INSERT INTO categories(category_id, Category) VALUES(?, ?);", (5, "entertainment"))
conn.commit()
cur.execute("INSERT INTO categories(category_id, Category) VALUES(?, ?);", (6, "health"))
conn.commit()
cur.execute("INSERT INTO categories(category_id, Category) VALUES(?, ?);", (7, "technology"))
conn.commit()

cur.execute("""CREATE TABLE IF NOT EXISTS users_categories(
    user_id INT,
    category_id INT,
    Category TEXT,
    UNIQUE(user_id, category_id, Category))
    """
)
conn.commit()

cur.execute("""CREATE TABLE IF NOT EXISTS keywords(
    Keyword TEXT,
    user_id INT);
    """
)
conn.commit()