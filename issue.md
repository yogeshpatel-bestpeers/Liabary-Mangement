Problem:
When running async tests with pytest-asyncio and SQLAlchemy’s async engine, the error
RuntimeError: Task got Future attached to a different loop occurs.

Cause:
This happens because the SQLAlchemy async engine was created outside of the async test fixture, binding it to the default event loop at import time. Meanwhile, pytest-asyncio runs each test inside its own fresh event loop. This mismatch causes the engine’s async operations to attempt running on a different event loop than the test’s coroutine, leading to the runtime error.

How to Fix

    Create the async engine inside an async fixture so that it is bound to the same event loop that the test runs on.

    Pass the dynamically created engine/session within fixtures to ensure consistent event loop context.

    Avoid sharing async resources bound to an event loop across tests globally.

  “I ran into an AttributeError: 'FastAPI' object has no attribute '__aenter__', which told me that I was mistakenly treating the FastAPI app as an async context manager — which it’s not.

  The root of the issue was trying to use async with test_app, but FastAPI doesn't implement __aenter__/__aexit__. Instead, for testing, the correct approach is to use httpx.AsyncClient with ASGITransport, which allows me to send HTTP requests to the app in-memory, without spinning up a server.

  So the fix was to create an ASGITransport using the app, and pass that to the AsyncClient. That way, I can simulate real HTTP requests and get full request/response behavior in tests, while avoiding misuse of the app object.”




httpx.AsyncClient: An HTTP client for making async requests, similar to requests but async.

ASGITransport: A special transport for httpx that allows requests to be made in memory directly to an ASGI app (like FastAPI), without needing to spin up an actual server

In tests, I use ASGITransport(app=...) from httpx to simulate HTTP requests directly to the FastAPI app without running a real server.
This allows me to write async integration tests that are faster, safer, and don't rely on network setup.
It hooks into FastAPI's ASGI interface, enabling true end-to-end behavior while staying fully in memory.
When paired with AsyncClient, this setup gives me a real request/response cycle — great for testing routes, middleware, and auth flows.

AsyncClient is an async HTTP client from httpx.

Since it uses ASGITransport, it doesn't make network calls — it routes directly to the FastAPI app.

A network call is any request that goes over a network connection (like HTTP) from a client (browser, Postman, or code) to a server.