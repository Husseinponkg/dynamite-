import bcrypt
from config.db import connection


class AdminMgmt:
    def __init__(self, data=None):
        self.data = data

    def _hash(self, password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def _fmt_admin(self, row):
        if not row:
            return None
        return {
            "id": row[0],
            "username": row[1],
            "email": row[2],
            "full_name": row[3],
            "role": row[4],
            "status": row[5],
            "created_at": row[6].isoformat() if row[6] else None,
            "last_login": row[7].isoformat() if row[7] else None,
        }

    async def list_admins(self):
        conn = None
        try:
            conn = await connection()
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    SELECT id, username, email, full_name, role, status, created_at, last_login
                    FROM admin ORDER BY id
                    """
                )
                rows = await cur.fetchall()
            return {"success": True, "admins": [self._fmt_admin(r) for r in rows]}
        finally:
            if conn:
                await conn.close()

    async def create_admin(self):
        conn = None
        try:
            conn = await connection()
            hashed = self._hash(self.data.password)
            role = self.data.role.value if hasattr(self.data.role, "value") else self.data.role
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    INSERT INTO admin (username, email, password, full_name, role)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id, username, email, full_name, role, status, created_at, last_login
                    """,
                    (self.data.username, self.data.email, hashed, self.data.full_name, role),
                )
                row = await cur.fetchone()
                await conn.commit()
            return {"success": True, "message": "Admin created", "admin": self._fmt_admin(row)}
        except Exception as e:
            if conn:
                await conn.rollback()
            if "unique" in str(e).lower():
                return {"success": False, "message": "Username or email already exists"}
            raise e
        finally:
            if conn:
                await conn.close()

    async def update_admin(self, admin_id: int):
        conn = None
        try:
            conn = await connection()
            fields = []
            values = []
            d = self.data
            if d.username is not None:
                fields.append("username = %s")
                values.append(d.username)
            if d.email is not None:
                fields.append("email = %s")
                values.append(d.email)
            if d.full_name is not None:
                fields.append("full_name = %s")
                values.append(d.full_name)
            if d.role is not None:
                fields.append("role = %s")
                values.append(d.role.value if hasattr(d.role, "value") else d.role)
            if d.status is not None:
                fields.append("status = %s")
                values.append(d.status)
            if d.password is not None:
                fields.append("password = %s")
                values.append(self._hash(d.password))
            if not fields:
                return {"success": False, "message": "Nothing to update"}
            values.append(admin_id)
            async with conn.cursor() as cur:
                await cur.execute(
                    f"""
                    UPDATE admin SET {', '.join(fields)}
                    WHERE id = %s
                    RETURNING id, username, email, full_name, role, status, created_at, last_login
                    """,
                    values,
                )
                row = await cur.fetchone()
                await conn.commit()
            if not row:
                return {"success": False, "message": "Admin not found"}
            return {"success": True, "admin": self._fmt_admin(row)}
        except Exception as e:
            if conn:
                await conn.rollback()
            raise e
        finally:
            if conn:
                await conn.close()

    async def delete_admin(self, admin_id: int):
        conn = None
        try:
            conn = await connection()
            async with conn.cursor() as cur:
                await cur.execute("DELETE FROM admin WHERE id = %s RETURNING id", (admin_id,))
                row = await cur.fetchone()
                await conn.commit()
            if not row:
                return {"success": False, "message": "Admin not found"}
            return {"success": True, "message": "Admin deleted"}
        except Exception as e:
            if conn:
                await conn.rollback()
            raise e
        finally:
            if conn:
                await conn.close()

    async def list_users(self, limit: int = 100):
        conn = None
        try:
            conn = await connection()
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    SELECT id, username, email, phone, full_name, status, created_at
                    FROM users ORDER BY created_at DESC LIMIT %s
                    """,
                    (limit,),
                )
                rows = await cur.fetchall()
            users = [
                {
                    "id": r[0],
                    "username": r[1],
                    "email": r[2],
                    "phone": r[3],
                    "full_name": r[4],
                    "status": r[5],
                    "created_at": r[6].isoformat() if r[6] else None,
                }
                for r in rows
            ]
            return {"success": True, "users": users}
        finally:
            if conn:
                await conn.close()

    async def list_branches(self):
        conn = None
        try:
            conn = await connection()
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT id, name, location, manager_name, phone, status, created_at FROM branches ORDER BY id"
                )
                rows = await cur.fetchall()
            return {
                "success": True,
                "branches": [
                    {
                        "id": r[0],
                        "name": r[1],
                        "location": r[2],
                        "manager_name": r[3],
                        "phone": r[4],
                        "status": r[5],
                        "created_at": r[6].isoformat() if r[6] else None,
                    }
                    for r in rows
                ],
            }
        except Exception as e:
            if "does not exist" in str(e).lower():
                return {"success": True, "branches": []}
            raise e
        finally:
            if conn:
                await conn.close()

    async def create_branch(self):
        conn = None
        try:
            conn = await connection()
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    INSERT INTO branches (name, location, manager_name, phone, status)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id, name, location, manager_name, phone, status, created_at
                    """,
                    (
                        self.data.name,
                        self.data.location,
                        self.data.manager_name,
                        self.data.phone,
                        self.data.status,
                    ),
                )
                r = await cur.fetchone()
                await conn.commit()
            return {
                "success": True,
                "branch": {
                    "id": r[0],
                    "name": r[1],
                    "location": r[2],
                    "manager_name": r[3],
                    "phone": r[4],
                    "status": r[5],
                    "created_at": r[6].isoformat() if r[6] else None,
                },
            }
        except Exception as e:
            if conn:
                await conn.rollback()
            if "does not exist" in str(e).lower():
                return {"success": False, "message": "Run migrate_add_billing_tables.sql first"}
            raise e
        finally:
            if conn:
                await conn.close()
