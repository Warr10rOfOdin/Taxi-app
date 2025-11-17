"""
Ultra-minimal test handler
This should work with ZERO dependencies
"""

def handler(event, context):
    """AWS Lambda / Vercel handler"""
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': '{"status":"ok","message":"Minimal handler works!","test":"direct_lambda_handler"}'
    }

# Also support ASGI
async def app(scope, receive, send):
    """Minimal ASGI app"""
    if scope['type'] == 'http':
        await send({
            'type': 'http.response.start',
            'status': 200,
            'headers': [[b'content-type', b'application/json']],
        })
        await send({
            'type': 'http.response.body',
            'body': b'{"status":"ok","message":"Minimal ASGI works!"}',
        })
