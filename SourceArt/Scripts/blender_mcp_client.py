"""Recover a closed host transport using the installed Blender MCP server.
This is a stdio MCP client, not a standalone bpy runner or a socket bypass.
Usage: server-python blender_mcp_client.py get_addon_status
       server-python blender_mcp_client.py execute_blender_code request.json
The JSON file contains normal tool arguments, including the user's prompt.
"""
import asyncio
import json
import os
import sys
import base64
from pathlib import Path
from datetime import timedelta
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    tool = sys.argv[1]
    args = json.load(open(sys.argv[2], encoding='utf-8')) if len(sys.argv) > 2 else {'user_prompt': 'modelar todos los modelos restantes'}
    env = dict(os.environ, BLENDER_MCP_DISABLE_TELEMETRY='1')
    server = StdioServerParameters(command='C:/Users/HP/.local/bin/mcp-for-blender.exe', env=env)
    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write, read_timeout_seconds=timedelta(seconds=45 if tool != 'execute_blender_code' else 300)) as session:
            await session.initialize()
            result = await session.call_tool(tool, args)
            for item in result.content:
                if item.type == 'image':
                    path = Path('SourceArt/_evidence/EX-13/recovery_viewport.png')
                    path.write_bytes(base64.b64decode(item.data))
                    print(str(path.resolve()), flush=True)
                elif item.type == 'text':
                    print(item.text, flush=True)
            if result.isError or any(item.type=='text' and item.text.startswith('Error executing code:') for item in result.content):
                raise RuntimeError('Blender MCP reported a tool error')


if __name__ == '__main__':
    asyncio.run(main())
