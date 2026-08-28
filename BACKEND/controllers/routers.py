from models.routmodels import createrouting,statusview
from config.db import connection

from utils.router_security import encrypt_value

from services.router_connection import (
    test_router_connection
)


class Routers:

    def __init__(self, routers):
        self.routers = routers

    async def createRouter(self):

        conn = None

        try:

            encrypted_password = encrypt_value(
                self.routers.password
            )

            encrypted_api_password = encrypt_value(
                self.routers.api_password
            )

            encrypted_api_key = encrypt_value(
                self.routers.api_key
            )

            encrypted_api_token = encrypt_value(
                self.routers.api_token
            )

            router_status = "offline"

            connection_message = (
                "Router connection was not tested"
            )

            try:

                result = test_router_connection(
                    self.routers
                )

                if result["connected"]:

                    router_status = "online"

                    connection_message = (
                        result["message"]
                    )

            except NotImplementedError as e:

                connection_message = str(e)

            except Exception as router_error:

                router_status = "offline"

                connection_message = (
                    f"Router connection failed: "
                    f"{str(router_error)}"
                )

            conn = await connection()

            async with conn.cursor() as cursor:

                query = """
                    INSERT INTO routers (
                        router_name,
                        router_ip,
                        router_port,
                        username,
                        password_encrypted,
                        connection_type,
                        api_type,
                        api_url,
                        api_username,
                        api_password_encrypted,
                        api_key_encrypted,
                        api_token_encrypted,
                        location,
                        max_users,
                        status
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id, router_name, router_ip, router_port,
                              connection_type, api_type, location, max_users, status, created_at
                """

                values = (
                    self.routers.router_name,
                    self.routers.router_ip,
                    self.routers.router_port,
                    self.routers.username,
                    encrypted_password,
                    self.routers.connection_type,
                    self.routers.api_type,
                    self.routers.api_url,
                    self.routers.api_username,
                    encrypted_api_password,
                    encrypted_api_key,
                    encrypted_api_token,
                    self.routers.location,
                    self.routers.max_users,
                    router_status
                )

                await cursor.execute(query, values)

                router = await cursor.fetchone()

                await conn.commit()

                return {
                    "message": "Router saved successfully",
                    "connection": connection_message,
                    "router_connected": router_status == "online",
                    "router": {
                        "id": router[0],
                        "router_name": router[1],
                        "router_ip": router[2],
                        "router_port": router[3],
                        "connection_type": router[4],
                        "api_type": router[5],
                        "location": router[6],
                        "max_users": router[7],
                        "status": router[8],
                        "created_at": router[9]
                    }
                }

        except Exception as e:

            if conn:
                await conn.rollback()

            raise e

        finally:

            if conn:

                await conn.close()

    async def view_status(self,router_id: int):

        conn = None

        try:
            conn = await connection()

            async with conn.cursor() as cursor:

                query = """
                    SELECT status
                    FROM routers
                    WHERE id = %s
                """

                await cursor.execute(
                    query,
                    (router_id,)
                )

                result = await cursor.fetchone()

                if not result:
                    return {
                        "message": "Router not found"
                    }

                return {
                    "router_id": router_id,
                    "status": result[0]
                }

        finally:

            if conn:
                await conn.close()