import os
import secrets
import asyncio
import logging
import ssl

from datetime import datetime, timedelta
from pathlib import Path

import bcrypt
import httpx

from dotenv import load_dotenv

from config.db import connection

from models.models import (
    BrevoConfig
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

logger = logging.getLogger("otp")


# =====================================================
# HTTP / SSL HELPERS
# =====================================================

def _create_brevo_ssl_context() -> ssl.SSLContext:

    context = ssl.create_default_context()

    context.minimum_version = ssl.TLSVersion.TLSv1_2

    context.set_ciphers(
        "ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!eNULL:!MD5:!DSS"
    )

    return context


def _build_brevo_client_kwargs() -> dict:

    return {
        "timeout": 20.0,
        "verify": _create_brevo_ssl_context(),
    }


# =====================================================
# LOAD ENVIRONMENT VARIABLES
# =====================================================

load_dotenv(
    Path(__file__).parent.parent / ".env"
)


# =====================================================
# BREVO CONFIGURATION
# =====================================================

BREVO_API_KEY = os.getenv(
    "BREVO_API_KEY"
)

BREVO_ENDPOINT = os.getenv(
    "BREVO_ENDPOINT",
    "https://api.brevo.com/v3/smtp/email"
)

SENDER_ID = os.getenv(
    "SENDER_ID"
)

SENDER_NAME = os.getenv(
    "SENDER_NAME",
    "Dynamite Networks"
)

BREVO_RETRY_ATTEMPTS = int(
    os.getenv("BREVO_RETRY_ATTEMPTS", "3")
)


# =====================================================
# OTP GENERATOR
# =====================================================

def generate_numeric_otp(length: int = 6) -> str:

    return "".join(
        secrets.choice("0123456789")
        for _ in range(length)
    )


# =====================================================
# SEND OTP EMAIL USING BREVO API
# =====================================================

async def send_otp_email(
    user_email: str,
    otp_code: str
):

    if not BREVO_API_KEY:

        print(
            "[OTP] BREVO_API_KEY is not configured."
        )

        return {
            "success": False,
            "error": "BREVO_API_KEY is not configured"
        }

    if not SENDER_ID:

        print(
            "[OTP] SENDER_ID is not configured."
        )

        return {
            "success": False,
            "error": "SENDER_ID is not configured"
        }

    try:

        headers = {
            "accept": "application/json",
            "api-key": BREVO_API_KEY,
            "content-type": "application/json"
        }

        payload = {

            "sender": {
                "name": SENDER_NAME,
                "email": SENDER_ID
            },

            "to": [
                {
                    "email": user_email
                }
            ],

            "subject": (
                "Verify Your Dynamite Networks Account"
            ),

            "htmlContent": f"""
                <!DOCTYPE html>

                <html>

                <head>

                    <meta charset="UTF-8">

                    <title>
                        Verify Your Account
                    </title>

                </head>

                <body
                    style="
                        margin:0;
                        padding:0;
                        background:#f3f4f6;
                        font-family:Arial,sans-serif;
                    "
                >

                    <div
                        style="
                            max-width:600px;
                            margin:40px auto;
                            background:white;
                            padding:40px;
                            border-radius:12px;
                            box-shadow:
                                0 4px 15px
                                rgba(0,0,0,0.08);
                        "
                    >

                        <h2
                            style="
                                color:#2563eb;
                                margin-bottom:20px;
                            "
                        >
                            Welcome to Dynamite Networks
                        </h2>

                        <p>
                            Thank you for creating
                            your account.
                        </p>

                        <p>
                            Use the verification code
                            below to verify your account:
                        </p>

                        <div
                            style="
                                margin:30px 0;
                                padding:20px;
                                text-align:center;
                                background:#f3f4f6;
                                border-radius:10px;
                            "
                        >

                            <h1
                                style="
                                    margin:0;
                                    color:#2563eb;
                                    letter-spacing:10px;
                                "
                            >
                                {otp_code}
                            </h1>

                        </div>

                        <p>
                            This OTP will expire in
                            <strong>5 minutes</strong>.
                        </p>

                        <p>
                            If you did not request this
                            verification code, please
                            ignore this email.
                        </p>

                        <hr
                            style="
                                border:none;
                                border-top:
                                    1px solid #e5e7eb;
                                margin:30px 0;
                            "
                        >

                        <p
                            style="
                                color:#6b7280;
                                font-size:13px;
                            "
                        >
                            Dynamite Networks
                        </p>

                    </div>

                </body>

                </html>
            """
        }

        last_exception = None

        for attempt in range(1, BREVO_RETRY_ATTEMPTS + 1):

            try:

                client_kwargs = _build_brevo_client_kwargs()

                if attempt > 1:

                    client_kwargs["verify"] = False

                    logger.warning(
                        "[OTP] Attempt %s: retrying Brevo with SSL verification disabled",
                        attempt,
                    )

                async with httpx.AsyncClient(
                    **client_kwargs
                ) as client:

                    response = await client.post(
                        BREVO_ENDPOINT,
                        headers=headers,
                        json=payload
                    )

                break

            except ssl.SSLError as exc:

                last_exception = exc

                logger.warning(
                    "[OTP] SSL error on attempt %s/%s for %s: %s",
                    attempt,
                    BREVO_RETRY_ATTEMPTS,
                    user_email,
                    exc,
                )

                if attempt < BREVO_RETRY_ATTEMPTS:

                    await asyncio.sleep(min(2 ** attempt, 10))

            except (httpx.ConnectError, httpx.TimeoutException, OSError) as exc:

                last_exception = exc

                logger.warning(
                    "[OTP] Brevo send attempt %s/%s failed for %s: %s",
                    attempt,
                    BREVO_RETRY_ATTEMPTS,
                    user_email,
                    exc,
                )

                if attempt < BREVO_RETRY_ATTEMPTS:

                    await asyncio.sleep(min(2 ** attempt, 10))

        else:

            error_message = str(last_exception)

            if isinstance(last_exception, ssl.SSLError):

                error_message = (
                    "TLS/SSL error while contacting Brevo after "
                    f"{BREVO_RETRY_ATTEMPTS} attempts: {last_exception}. "
                    "This often indicates a TLS version/cipher mismatch, "
                    "SSL interception by a proxy/antivirus, or outdated "
                    "system SSL libraries. Try: "
                    "1) Update Windows/OpenSSL, "
                    "2) Check proxy/antivirus HTTPS scanning, "
                    "3) Ensure outbound 443 to api.brevo.com is unfiltered."
                )

            elif isinstance(last_exception, OSError):

                error_message = (
                    "Network/DNS error while contacting Brevo after "
                    f"{BREVO_RETRY_ATTEMPTS} attempts. "
                    "Check internet connectivity, DNS resolution for "
                    "api.brevo.com, and firewall/proxy settings."
                )

            return {

                "success": False,

                "error": error_message

            }

        if response.status_code in (200, 201):

            response_data = response.json()

            logger.info(
                "[OTP] Email sent successfully to %s",
                user_email,
            )

            return {
                "success": True,
                "message": "Email sent successfully",
                "message_id": response_data.get(
                    "messageId"
                )
            }

        logger.error(
            "[OTP] Brevo email failed: %s %s",
            response.status_code,
            response.text,
        )

        return {
            "success": False,
            "status_code": response.status_code,
            "error": response.text
        }

    except Exception as e:

        logger.exception(
            "[OTP] Failed to send email to %s after %s attempts: %s",
            user_email,
            BREVO_RETRY_ATTEMPTS,
            e,
        )

        error_message = str(e)

        if isinstance(e, OSError):
            error_message = (
                "Network/DNS error while contacting Brevo. "
                "Check internet connectivity, DNS resolution for "
                "api.brevo.com, and firewall/proxy settings."
            )

        return {
            "success": False,
            "error": error_message
        }


# =====================================================
# AUTHENTICATION
# =====================================================

class Authentication:

    def __init__(self, data=None):

        self.data = data


    # =================================================
    # REGISTER USER
    # =================================================

    async def registeruser(self):

        conn = await connection()

        try:

            # -----------------------------------------
            # CHECK EXISTING EMAIL
            # -----------------------------------------

            check_query = """
                SELECT id
                FROM users
                WHERE email = %s
            """

            async with conn.cursor() as cursor:

                await cursor.execute(
                    check_query,
                    (self.data.email,)
                )

                existing_user = (
                    await cursor.fetchone()
                )

            if existing_user:

                return {
                    "success": False,
                    "message": (
                        "Email already registered"
                    )
                }


            # -----------------------------------------
            # GENERATE OTP
            # -----------------------------------------

            new_otp = generate_numeric_otp()

            otp_expires_at = (
                datetime.now()
                + timedelta(minutes=5)
            )


            # -----------------------------------------
            # HASH PASSWORD
            # -----------------------------------------

            hashed_password = bcrypt.hashpw(
                self.data.password.encode("utf-8"),
                bcrypt.gensalt()
            ).decode("utf-8")


            # -----------------------------------------
            # INSERT USER
            # -----------------------------------------

            query = """

                INSERT INTO users (

                    username,
                    email,
                    password,
                    phone,
                    otp,
                    otp_expires_at,
                    full_name,
                    address,
                    created_at,
                    updated_at,
                    status

                )

                VALUES (

                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s

                )

                RETURNING

                    id,
                    username,
                    email,
                    phone,
                    full_name,
                    address,
                    status

            """

            now = datetime.now()

            values = (

                self.data.username,
                self.data.email,
                hashed_password,
                self.data.phone,
                new_otp,
                otp_expires_at,
                self.data.full_name,
                self.data.address,
                now,
                now,
                "pending"

            )

            async with conn.cursor() as cursor:

                await cursor.execute(
                    query,
                    values
                )

                user = await cursor.fetchone()


            await conn.commit()


            # -----------------------------------------
            # SEND OTP
            # -----------------------------------------

            email_result = await send_otp_email(
                self.data.email,
                new_otp
            )


            if not email_result["success"]:

                return {

                    "success": True,

                    "message": (
                        "Registration successful, "
                        "but OTP email could not be "
                        "sent. Please use resend OTP."
                    ),

                    "email_error": (
                        email_result.get("error")
                    ),

                    "user": user

                }


            return {

                "success": True,

                "message": (
                    "Registration successful. "
                    "OTP has been sent to your email."
                ),

                "user": user

            }


        except Exception:

            await conn.rollback()

            raise


        finally:

            await conn.close()


    # =================================================
    # VERIFY OTP
    # =================================================

    async def verifyotp(self):

        conn = await connection()

        try:

            query = """

                SELECT
                    id,
                    otp,
                    otp_expires_at,
                    status

                FROM users

                WHERE email = %s

            """

            async with conn.cursor() as cursor:

                await cursor.execute(
                    query,
                    (self.data.email,)
                )

                user = await cursor.fetchone()


            if user is None:

                return {

                    "success": False,

                    "message": "User not found"

                }


            (
                user_id,
                stored_otp,
                otp_expires_at,
                status
            ) = user


            # -----------------------------------------
            # ALREADY VERIFIED
            # -----------------------------------------

            if status == "verified":

                return {

                    "success": False,

                    "message": (
                        "Account already verified"
                    )

                }


            # -----------------------------------------
            # CHECK OTP
            # -----------------------------------------

            if stored_otp != self.data.otp:

                return {

                    "success": False,

                    "message": "Invalid OTP"

                }


            # -----------------------------------------
            # CHECK EXPIRATION
            # -----------------------------------------

            if (
                otp_expires_at is None
                or datetime.now() > otp_expires_at
            ):

                return {

                    "success": False,

                    "message": "OTP has expired"

                }


            # -----------------------------------------
            # VERIFY USER
            # -----------------------------------------

            update_query = """

                UPDATE users

                SET

                    status = 'verified',
                    otp = NULL,
                    otp_expires_at = NULL,
                    updated_at = CURRENT_TIMESTAMP

                WHERE id = %s

            """

            async with conn.cursor() as cursor:

                await cursor.execute(
                    update_query,
                    (user_id,)
                )


            await conn.commit()


            return {

                "success": True,

                "message": (
                    "Account verified successfully"
                )

            }


        except Exception:

            await conn.rollback()

            raise


        finally:

            await conn.close()


    # =================================================
    # LOGIN
    # =================================================

    async def loginuser(self):

        conn = await connection()

        try:

            query = """

                SELECT

                    id,
                    username,
                    email,
                    password,
                    status

                FROM users

                WHERE email = %s

            """

            async with conn.cursor() as cursor:

                await cursor.execute(
                    query,
                    (self.data.email,)
                )

                user = await cursor.fetchone()


            if user is None:

                return {

                    "success": False,

                    "message": (
                        "Invalid email or password"
                    )

                }


            (
                user_id,
                username,
                email,
                stored_password,
                status
            ) = user


            # -----------------------------------------
            # ACCOUNT VERIFICATION
            # -----------------------------------------

            if status != "verified":

                return {

                    "success": False,

                    "message": (
                        "Please verify your account first"
                    )

                }


            # -----------------------------------------
            # PASSWORD
            # -----------------------------------------

            password_valid = bcrypt.checkpw(

                self.data.password.encode("utf-8"),

                stored_password.encode("utf-8")

            )


            if not password_valid:

                return {

                    "success": False,

                    "message": (
                        "Invalid email or password"
                    )

                }


            return {

                "success": True,

                "user": {

                    "id": user_id,

                    "username": username,

                    "email": email

                }

            }


        finally:

            await conn.close()


    # =================================================
    # UPDATE USER
    # =================================================

    async def updateuser(
        self,
        current_user_id: int
    ):

        conn = await connection()

        try:

            # -----------------------------------------
            # ALLOWED FIELDS
            # -----------------------------------------

            allowed_fields = {

                "username",
                "phone",
                "full_name",
                "address"

            }


            update_fields = []

            values = []


            data = self.data.model_dump(
                exclude_unset=True
            )


            for field, value in data.items():

                if field not in allowed_fields:

                    continue

                if value is None:

                    continue


                update_fields.append(
                    f"{field} = %s"
                )

                values.append(value)


            if not update_fields:

                return {

                    "success": False,

                    "message": (
                        "No modification "
                        "parameters provided"
                    )

                }


            # -----------------------------------------
            # UPDATE ONLY JWT USER
            # -----------------------------------------

            query = f"""

                UPDATE users

                SET

                    {", ".join(update_fields)},
                    updated_at = CURRENT_TIMESTAMP

                WHERE id = %s

            """


            values.append(
                current_user_id
            )


            async with conn.cursor() as cursor:

                await cursor.execute(
                    query,
                    tuple(values)
                )

                affected_rows = cursor.rowcount


            await conn.commit()


            if affected_rows == 0:

                return {

                    "success": False,

                    "message": "User not found"

                }


            return {

                "success": True,

                "message": (
                    "Profile updated successfully"
                )

            }


        except Exception:

            await conn.rollback()

            raise


        finally:

            await conn.close()


    # =================================================
    # DELETE USER
    # =================================================

    async def deleteuser(
        self,
        current_user_id: int
    ):

        conn = await connection()

        try:

            query = """

                DELETE FROM users

                WHERE id = %s

            """


            async with conn.cursor() as cursor:

                await cursor.execute(
                    query,
                    (current_user_id,)
                )

                affected_rows = cursor.rowcount


            await conn.commit()


            if affected_rows == 0:

                return {

                    "success": False,

                    "message": "User not found"

                }


            return {

                "success": True,

                "message": (
                    "Account completely deleted"
                )

            }


        except Exception:

            await conn.rollback()

            raise


        finally:

            await conn.close()


    # =================================================
    # GET ALL USERS
    # =================================================

    async def getallusers(self):

        conn = await connection()

        try:

            query = """

                SELECT

                    id,
                    username,
                    email,
                    phone,
                    full_name,
                    address,
                    created_at,
                    updated_at,
                    status

                FROM users

                ORDER BY id DESC

            """


            async with conn.cursor() as cursor:

                await cursor.execute(query)

                users = await cursor.fetchall()

                columns = [
                    description[0]
                    for description
                    in cursor.description
                ]

                users = [

                    dict(
                        zip(columns, row)
                    )

                    for row in users

                ]


            return users


        finally:

            await conn.close()


    # =================================================
    # GET ONE USER
    # =================================================

    async def getuser(
        self,
        user_id: int
    ):

        conn = await connection()

        try:

            query = """

                SELECT

                    id,
                    username,
                    email,
                    phone,
                    full_name,
                    address,
                    created_at,
                    updated_at,
                    status

                FROM users

                WHERE id = %s

            """


            async with conn.cursor() as cursor:

                await cursor.execute(
                    query,
                    (user_id,)
                )

                user = await cursor.fetchone()


            if user is None:

                return {

                    "success": False,

                    "message": "User not found"

                }


            return {

                "success": True,

                "user": user

            }


        finally:

            await conn.close()


    # =================================================
    # RESEND OTP
    # =================================================

    async def resendotp(self):

        conn = await connection()

        try:

            query = """

                SELECT
                    id,
                    status

                FROM users

                WHERE email = %s

            """


            async with conn.cursor() as cursor:

                await cursor.execute(
                    query,
                    (self.data.email,)
                )

                user = await cursor.fetchone()


            if user is None:

                return {

                    "success": False,

                    "message": "User not found"

                }


            if user[1] == "verified":

                return {

                    "success": False,

                    "message": (
                        "Account already verified"
                    )

                }


            # -----------------------------------------
            # NEW OTP
            # -----------------------------------------

            new_otp = generate_numeric_otp()

            expires = (
                datetime.now()
                + timedelta(minutes=5)
            )


            update_query = """

                UPDATE users

                SET

                    otp = %s,
                    otp_expires_at = %s,
                    updated_at = CURRENT_TIMESTAMP

                WHERE email = %s

            """


            async with conn.cursor() as cursor:

                await cursor.execute(

                    update_query,

                    (
                        new_otp,
                        expires,
                        self.data.email
                    )

                )


            await conn.commit()


            # -----------------------------------------
            # SEND EMAIL
            # -----------------------------------------

            email_result = await send_otp_email(

                self.data.email,

                new_otp

            )


            if not email_result["success"]:

                return {

                    "success": False,

                    "message": (
                        "OTP generated but "
                        "email could not be sent"
                    ),

                    "error": email_result.get(
                        "error"
                    )

                }


            return {

                "success": True,

                "message": (
                    "New OTP sent successfully"
                )

            }


        except Exception:

            await conn.rollback()

            raise


        finally:

            await conn.close()


    # =================================================
    # SEND OTP
    # =================================================

    async def send_otp(self):

        conn = await connection()

        try:

            query = """

                SELECT
                    id,
                    status

                FROM users

                WHERE email = %s

            """


            async with conn.cursor() as cursor:

                await cursor.execute(
                    query,
                    (self.data.email,)
                )

                user = await cursor.fetchone()


            if user is None:

                return {

                    "success": False,

                    "message": "User not found"

                }


            if user[1] == "verified":

                return {

                    "success": False,

                    "message": (
                        "Account already verified"
                    )

                }


            new_otp = generate_numeric_otp()

            expires = (
                datetime.now()
                + timedelta(minutes=5)
            )


            update_query = """

                UPDATE users

                SET

                    otp = %s,
                    otp_expires_at = %s,
                    updated_at = CURRENT_TIMESTAMP

                WHERE email = %s

            """


            async with conn.cursor() as cursor:

                await cursor.execute(

                    update_query,

                    (
                        new_otp,
                        expires,
                        self.data.email
                    )

                )


            await conn.commit()


            email_result = await send_otp_email(

                self.data.email,

                new_otp

            )


            if not email_result["success"]:

                return {

                    "success": False,

                    "message": (
                        "OTP generated but "
                        "email could not be sent"
                    ),

                    "error": email_result.get(
                        "error"
                    )

                }


            return {

                "success": True,

                "message": (
                    "OTP sent successfully"
                )

            }


        except Exception:

            await conn.rollback()

            raise


        finally:

            await conn.close()


    # =================================================
    # FORGOT PASSWORD
    # =================================================

    async def forgotpassword(self):

        conn = await connection()

        try:

            query = """

                SELECT
                    id,
                    status

                FROM users

                WHERE email = %s

            """


            async with conn.cursor() as cursor:

                await cursor.execute(
                    query,
                    (self.data.email,)
                )

                user = await cursor.fetchone()


            if user is None:

                return {

                    "success": False,

                    "message": "User not found"

                }


            new_otp = generate_numeric_otp()

            expires = (
                datetime.now()
                + timedelta(minutes=15)
            )


            update_query = """

                UPDATE users

                SET

                    otp = %s,
                    otp_expires_at = %s,
                    updated_at = CURRENT_TIMESTAMP

                WHERE email = %s

            """


            async with conn.cursor() as cursor:

                await cursor.execute(

                    update_query,

                    (
                        new_otp,
                        expires,
                        self.data.email
                    )

                )


            await conn.commit()


            email_result = await send_otp_email(

                self.data.email,

                new_otp

            )


            if not email_result["success"]:

                return {

                    "success": False,

                    "message": (
                        "Password reset OTP "
                        "could not be sent"
                    ),

                    "error": email_result.get(
                        "error"
                    )

                }


            return {

                "success": True,

                "message": (
                    "Password reset OTP sent "
                    "to your email"
                )

            }


        except Exception:

            await conn.rollback()

            raise


        finally:

            await conn.close()


    # =================================================
    # RESET PASSWORD
    # =================================================

    async def resetpassword(self):

        conn = await connection()

        try:

            query = """

                SELECT

                    id,
                    otp,
                    otp_expires_at,
                    status

                FROM users

                WHERE email = %s

            """


            async with conn.cursor() as cursor:

                await cursor.execute(

                    query,

                    (self.data.email,)

                )

                user = await cursor.fetchone()


            if user is None:

                return {

                    "success": False,

                    "message": "User not found"

                }


            (
                user_id,
                stored_otp,
                otp_expires_at,
                status
            ) = user


            # -----------------------------------------
            # OTP
            # -----------------------------------------

            if stored_otp != self.data.otp:

                return {

                    "success": False,

                    "message": "Invalid OTP"

                }


            # -----------------------------------------
            # EXPIRATION
            # -----------------------------------------

            if (

                otp_expires_at is None

                or datetime.now()
                > otp_expires_at

            ):

                return {

                    "success": False,

                    "message": "OTP has expired"

                }


            # -----------------------------------------
            # HASH NEW PASSWORD
            # -----------------------------------------

            hashed_password = bcrypt.hashpw(

                self.data.new_password.encode(
                    "utf-8"
                ),

                bcrypt.gensalt()

            ).decode("utf-8")


            # -----------------------------------------
            # UPDATE PASSWORD
            # -----------------------------------------

            update_query = """

                UPDATE users

                SET

                    password = %s,
                    otp = NULL,
                    otp_expires_at = NULL,
                    updated_at = CURRENT_TIMESTAMP

                WHERE id = %s

            """


            async with conn.cursor() as cursor:

                await cursor.execute(

                    update_query,

                    (
                        hashed_password,
                        user_id
                    )

                )


            await conn.commit()


            return {

                "success": True,

                "message": (
                    "Password reset successful"
                )

            }


        except Exception:

            await conn.rollback()

            raise


        finally:

            await conn.close()


    # =================================================
    # BREVO CONNECTION STATUS
    # =================================================

    def brevo_status(self):

        if not BREVO_API_KEY:

            return {

                "success": False,

                "message": (
                    "BREVO_API_KEY not configured"
                ),

                "config": BrevoConfig(

                    smtp_server=BREVO_ENDPOINT,

                    smtp_port=443,

                    smtp_login=SENDER_ID or "",

                    smtp_key=""

                ).model_dump()

            }


        return {

            "success": True,

            "message": (
                "Brevo API credentials configured"
            ),

            "config": BrevoConfig(

                smtp_server=BREVO_ENDPOINT,

                smtp_port=443,

                smtp_login=SENDER_ID or "",

                smtp_key="***"

            ).model_dump()

        }


    # =================================================
    # SEND OTP TO ALL USERS
    # =================================================

    async def send_otp_email_to_all(self):

        conn = await connection()

        try:

            query = """

                SELECT
                    id,
                    email

                FROM users

            """


            async with conn.cursor() as cursor:

                await cursor.execute(query)

                users = await cursor.fetchall()


            results = []


            for user in users:

                user_id, email = user

                new_otp = generate_numeric_otp()

                expires = (
                    datetime.now()
                    + timedelta(minutes=5)
                )


                update_query = """

                    UPDATE users

                    SET

                        otp = %s,
                        otp_expires_at = %s,
                        updated_at = CURRENT_TIMESTAMP

                    WHERE id = %s

                """


                async with conn.cursor() as cursor:

                    await cursor.execute(

                        update_query,

                        (
                            new_otp,
                            expires,
                            user_id
                        )

                    )


                results.append({

                    "id": user_id,

                    "email": email,

                    "otp": new_otp

                })


            await conn.commit()


            # -----------------------------------------
            # SEND EMAILS
            # -----------------------------------------

            tasks = [

                send_otp_email(

                    item["email"],

                    item["otp"]

                )

                for item in results

            ]


            email_results = await asyncio.gather(
                *tasks
            )


            successful = 0
            failed = 0


            for result in email_results:

                if result.get("success"):

                    successful += 1

                else:

                    failed += 1


            return {

                "success": True,

                "message": (
                    "OTP email processing completed"
                ),

                "total_users": len(results),

                "successful": successful,

                "failed": failed

            }


        except Exception:

            await conn.rollback()

            raise


        finally:

            await conn.close()