# tls_wrapper.py

# Ensures configuration consistency, backend HTTP request uses the same user
# agent, language header & TLS handshake style as the selenium browser

from async_tls_client import AsyncSession

async def create_tls_client(profile):
    client = AsyncSession(
        client_identifier=profile.tls_client_name
    )

    return client
