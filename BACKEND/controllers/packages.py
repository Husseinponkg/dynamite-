from models.packages import CreatePackages, UpdatePackages
from config.db import connection


class Packages:

    def __init__(self, data=None):
        self.data = data


    # =====================================================
    # CREATE PACKAGE
    # =====================================================

    async def packageCreation(self):

        conn = None

        try:

            conn = await connection()

            query = """
                INSERT INTO package (
                    package_name,
                    package_desc,
                    price,
                    validity_days,
                    validity_hours,
                    bandwidth_up,
                    bandwidth_down,
                    data_limit,
                    concurrent_logins,
                    status
                )
                VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s
                )
                RETURNING
                    id,
                    package_name,
                    package_desc,
                    price,
                    validity_days,
                    validity_hours,
                    bandwidth_up,
                    bandwidth_down,
                    data_limit,
                    concurrent_logins,
                    created_at,
                    status
            """

            values = (
                self.data.package_name,
                self.data.package_desc,
                self.data.price,
                self.data.validity_days,
                self.data.validity_hours,
                self.data.bandwidth_up,
                self.data.bandwidth_down,
                self.data.data_limit,
                self.data.concurrent_logins,
                self.data.status.value
            )

            async with conn.cursor() as cursor:

                await cursor.execute(
                    query,
                    values
                )

                package = await cursor.fetchone()

            await conn.commit()

            return self.format_package(package)


        except Exception as e:

            if conn:
                await conn.rollback()

            raise e


        finally:

            if conn:
                await conn.close()


    # =====================================================
    # GET ALL PACKAGES
    # =====================================================

    async def getAllPackages(self):

        conn = None

        try:

            conn = await connection()

            query = """
                SELECT
                    id,
                    package_name,
                    package_desc,
                    price,
                    validity_days,
                    validity_hours,
                    bandwidth_up,
                    bandwidth_down,
                    data_limit,
                    concurrent_logins,
                    created_at,
                    status
                FROM package
                ORDER BY id DESC
            """

            async with conn.cursor() as cursor:

                await cursor.execute(query)

                packages = await cursor.fetchall()

            return [
                self.format_package(package)
                for package in packages
            ]


        except Exception as e:

            raise e


        finally:

            if conn:
                await conn.close()


    # =====================================================
    # GET ONE PACKAGE
    # =====================================================

    async def getOnePackage(self, package_id: int):

        conn = None

        try:

            conn = await connection()

            query = """
                SELECT
                    id,
                    package_name,
                    package_desc,
                    price,
                    validity_days,
                    validity_hours,
                    bandwidth_up,
                    bandwidth_down,
                    data_limit,
                    concurrent_logins,
                    created_at,
                    status
                FROM package
                WHERE id = %s
            """

            async with conn.cursor() as cursor:

                await cursor.execute(
                    query,
                    (package_id,)
                )

                package = await cursor.fetchone()


            if not package:

                return {
                    "message": "Package not found"
                }


            return self.format_package(package)


        except Exception as e:

            raise e


        finally:

            if conn:
                await conn.close()


    # =====================================================
    # UPDATE PACKAGE
    # =====================================================

    async def updatePackage(self, package_id: int):

        conn = None

        try:

            conn = await connection()


            # Get only fields supplied by user

            update_data = self.data.model_dump(
                exclude_unset=True
            )


            if not update_data:

                return {
                    "message": "No data provided for update"
                }


            fields = []

            values = []


            for field, value in update_data.items():

                fields.append(
                    f"{field} = %s"
                )


                if hasattr(value, "value"):

                    value = value.value


                values.append(value)


            values.append(package_id)


            query = f"""
                UPDATE package
                SET {', '.join(fields)}
                WHERE id = %s
                RETURNING
                    id,
                    package_name,
                    package_desc,
                    price,
                    validity_days,
                    validity_hours,
                    bandwidth_up,
                    bandwidth_down,
                    data_limit,
                    concurrent_logins,
                    created_at,
                    status
            """


            async with conn.cursor() as cursor:

                await cursor.execute(
                    query,
                    tuple(values)
                )

                package = await cursor.fetchone()


            if not package:

                await conn.rollback()

                return {
                    "message": "Package not found"
                }


            await conn.commit()


            return {
                "message": "Package updated successfully",
                "package": self.format_package(package)
            }


        except Exception as e:

            if conn:
                await conn.rollback()

            raise e


        finally:

            if conn:
                await conn.close()


    # =====================================================
    # DELETE PACKAGE
    # =====================================================

    async def deletePackage(self, package_id: int):

        conn = None

        try:

            conn = await connection()


            query = """
                DELETE FROM package
                WHERE id = %s
                RETURNING id, package_name
            """


            async with conn.cursor() as cursor:

                await cursor.execute(
                    query,
                    (package_id,)
                )

                package = await cursor.fetchone()


            if not package:

                await conn.rollback()

                return {
                    "message": "Package not found"
                }


            await conn.commit()


            return {
                "message": "Package deleted successfully",

                "package": {
                    "id": package[0],
                    "package_name": package[1]
                }
            }


        except Exception as e:

            if conn:
                await conn.rollback()

            raise e


        finally:

            if conn:
                await conn.close()


    # =====================================================
    # FORMAT PACKAGE
    # =====================================================

    def format_package(self, package):

        return {

            "id": package[0],

            "package_name": package[1],

            "package_desc": package[2],

            "price": str(package[3]),

            "validity_days": package[4],

            "validity_hours": package[5],

            "bandwidth_up": package[6],

            "bandwidth_down": package[7],

            "data_limit": package[8],

            "concurrent_logins": package[9],

            "created_at": package[10],

            "status": package[11]
        }