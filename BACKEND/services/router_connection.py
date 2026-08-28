from netmiko import ConnectHandler


def connect_ssh(router):

    device = {
        "device_type": "mikrotik_routeros",
        "host": router.router_ip,
        "port": router.router_port,
        "username": router.username,
        "password": router.password,
        "timeout": 10,
        "conn_timeout": 10
    }

    connection = ConnectHandler(**device)

    return connection


def test_router_connection(router):

    connection_type = router.connection_type.lower()

    if connection_type == "ssh":

        connection = connect_ssh(router)

        try:

            return {
                "connected": True,
                "message": "SSH connection successful"
            }

        finally:

            connection.disconnect()

    elif connection_type == "telnet":

        raise NotImplementedError(
            "Telnet connector has not been implemented yet"
        )

    elif connection_type == "api":

        raise NotImplementedError(
            "Generic API connector has not been implemented yet"
        )

    elif connection_type == "rest_api":

        raise NotImplementedError(
            "REST API connector has not been implemented yet"
        )

    else:

        raise ValueError(
            f"Unsupported connection type: "
            f"{router.connection_type}"
        )
