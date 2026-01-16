import sqlite3, asyncio, json

db = sqlite3.connect("economy.db", check_same_thread=False)
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    wallet INTEGER DEFAULT 0,
    bank INTEGER DEFAULT 0,
    inventory TEXT DEFAULT '{}'
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS shop (
    item TEXT PRIMARY KEY,
    price INTEGER
)
""")

db.commit()
lock = asyncio.Lock()

def get_user(uid):
    cursor.execute("SELECT wallet, bank, inventory FROM users WHERE user_id=?", (uid,))
    r = cursor.fetchone()
    if not r:
        cursor.execute("INSERT INTO users VALUES (?,0,0,'{}')", (uid,))
        db.commit()
        return 0, 0, {}
    return r[0], r[1], json.loads(r[2])

def update_user(uid, wallet=None, bank=None, inv=None):
    w, b, i = get_user(uid)
    cursor.execute(
        "UPDATE users SET wallet=?, bank=?, inventory=? WHERE user_id=?",
        (wallet if wallet is not None else w,
         bank if bank is not None else b,
         json.dumps(inv if inv is not None else i),
         uid)
    )
    db.commit()
