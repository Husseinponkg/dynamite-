from datetime import datetime
from config.db import connection


class Sessions:
    def __init__(self, data=None):
        self.data = data

    def _fmt(self, row):
        if not row:
            return None
        return {
            "id": row[0],
            "user_id": row[1],
            "router_id": row[2],
            "session_id": row[3],
            "ip_address": row[4],
            "mac_address": row[5],
            "bandwidth_up_used": row[6] or 0,
            "bandwidth_down_used": row[7] or 0,
            "total_usage": row[8] or 0,
            "start_time": row[9].isoformat() if row[9] else None,
            "last_update": row[10].isoformat() if row[10] else None,
            "end_time": row[11].isoformat() if row[11] else None,
            "status": row[12],
            "username": row[13] if len(row) > 13 else None,
            "router_name": row[14] if len(row) > 14 else None,
        }

    async def list_sessions(self, status: str = "active", router_id: int = None, limit: int = 100):
        conn = None
        try:
            conn = await connection()
            conditions = ["1=1"]
            params = []
            if status:
                conditions.append("s.status = %s")
                params.append(status)
            if router_id:
                conditions.append("s.router_id = %s")
                params.append(router_id)
            where = " AND ".join(conditions)
            params.append(limit)
            async with conn.cursor() as cur:
                await cur.execute(
                    f"""
                    SELECT s.id, s.user_id, s.router_id, s.session_id, s.ip_address, s.mac_address,
                           s.bandwidth_up_used, s.bandwidth_down_used, s.total_usage,
                           s.start_time, s.last_update, s.end_time, s.status,
                           u.username, r.router_name
                    FROM active_sessions s
                    LEFT JOIN users u ON u.id = s.user_id
                    LEFT JOIN routers r ON r.id = s.router_id
                    WHERE {where}
                    ORDER BY s.start_time DESC
                    LIMIT %s
                    """,
                    params,
                )
                rows = await cur.fetchall()
                await cur.execute(
                    f"SELECT COUNT(*) FROM active_sessions s WHERE {where}",
                    params[:-1],
                )
                total = (await cur.fetchone())[0]
            return {"success": True, "total": total, "sessions": [self._fmt(r) for r in rows]}
        finally:
            if conn:
                await conn.close()

    async def stats(self):
        conn = None
        try:
            conn = await connection()
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    SELECT
                        COUNT(*) FILTER (WHERE status = 'active') as active_now,
                        COUNT(*) FILTER (WHERE start_time::date = CURRENT_DATE) as today,
                        COALESCE(SUM(total_usage) FILTER (WHERE status = 'active'), 0) as active_usage,
                        COALESCE(SUM(total_usage), 0) as all_usage
                    FROM active_sessions
                    """
                )
                row = await cur.fetchone()
            return {
                "success": True,
                "stats": {
                    "active_now": row[0] or 0,
                    "today": row[1] or 0,
                    "active_usage_bytes": int(row[2] or 0),
                    "total_usage_bytes": int(row[3] or 0),
                    "active_usage_mb": round((row[2] or 0) / 1024 / 1024, 2),
                    "total_usage_mb": round((row[3] or 0) / 1024 / 1024, 2),
                },
            }
        finally:
            if conn:
                await conn.close()

    async def create(self):
        conn = None
        try:
            conn = await connection()
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    INSERT INTO active_sessions (
                        user_id, router_id, session_id, ip_address, mac_address, status
                    ) VALUES (%s, %s, %s, %s, %s, 'active')
                    ON CONFLICT (session_id) DO UPDATE SET
                        last_update = CURRENT_TIMESTAMP, status = 'active'
                    RETURNING id, user_id, router_id, session_id, ip_address, mac_address,
                              bandwidth_up_used, bandwidth_down_used, total_usage,
                              start_time, last_update, end_time, status
                    """,
                    (
                        self.data.user_id,
                        self.data.router_id,
                        self.data.session_id,
                        self.data.ip_address,
                        self.data.mac_address,
                    ),
                )
                row = await cur.fetchone()
                await conn.commit()
            return {"success": True, "session": self._fmt(row)}
        except Exception as e:
            if conn:
                await conn.rollback()
            raise e
        finally:
            if conn:
                await conn.close()

    async def end(self, session_id: str, up: int = 0, down: int = 0):
        conn = None
        try:
            conn = await connection()
            total = (up or 0) + (down or 0)
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    UPDATE active_sessions SET
                        status = 'terminated',
                        end_time = CURRENT_TIMESTAMP,
                        bandwidth_up_used = %s,
                        bandwidth_down_used = %s,
                        total_usage = %s,
                        last_update = CURRENT_TIMESTAMP
                    WHERE session_id = %s AND status = 'active'
                    RETURNING id
                    """,
                    (up, down, total, session_id),
                )
                row = await cur.fetchone()
                await conn.commit()
            if not row:
                return {"success": False, "message": "Active session not found"}
            return {"success": True, "message": "Session ended"}
        except Exception as e:
            if conn:
                await conn.rollback()
            raise e
        finally:
            if conn:
                await conn.close()
