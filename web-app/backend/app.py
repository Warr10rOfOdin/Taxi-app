"""
Vercel FastAPI entrypoint for the Voss Taxi backend.

We reuse the existing application defined in api/index.py so we don't
have to touch any of the routing or business logic there.
"""

from api.index import app  # FastAPI instance

# Nothing else needed. Vercel's FastAPI runtime will look for `app`
# here and run it as a single Function.
