import asyncio  # for async/await
from ollama import AsyncClient, Client
from contextlib import AsyncExitStack
from typing import Optional
from mcp import ClientSession, StdioServerParameters  # for MCP client
from mcp.client.stdio import stdio_client


class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = (
            None  # This will hold the connection to your MCP server. Right now it's empty (None) — it gets filled later when you actually connect to the server.
        )
        # Optional just means it can be either a ClientSession object OR None.
        self.exit_stack = (
            AsyncExitStack()
        )  # AsyncExitStack exits everything like say bye then awaits response from server then closes
        self.ollama = AsyncClient()

    async def connect_to_server(self):
        # step 1 - define server params
        server_params = StdioServerParameters(
            command="npx",
            args=[
                "-y",
                "@modelcontextprotocol/server-filesystem",
                "C:/Users/saira/Documents",
            ],
            env=None,
        )

        # step 2 - start STDIO connection
        # use exit_stack to enter stdio_client
        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        self.stdio, self.write = (
            stdio_transport  # splits the connection into two parts: 1.stdio = for reading responses from server 2.write = for writing messages to server
        )

        # step 3 - create session
        # use exit_stack to enter ClientSession
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(self.stdio, self.write)
        )

        # step 4 - initialize session
        await self.session.initialize()

        # step 5 - list and print tools
        response = await self.session.list_tools()
        tools = response.tools

        print("\nConnected to server with tools:", [tool.name for tool in tools])

    async def process_query(self, query):
        # step 1 - prepare messages
        messages = [{"role": "user", "content": query}]
        # step 2 - get available tools
        response = await self.session.list_tools()
        available_tools = [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema,
            }
            for tool in response.tools
        ]
        print("i am here")
        # step 3 - send to ollama
        response = await self.ollama.chat(
            model="llama3.1", messages=messages, tools=available_tools
        )

        # step 4 - process response
        if response.message.tool_calls:
            tool_call = response.message.tool_calls[0]
            tool_name = tool_call.function.name
            tool_args = tool_call.function.arguments
            print("i am here before printing ollama called")
            # printing which tool ollama wants to use and with what arguments (human-in-loop (HIL))
            print(f"ollama called {tool_name}")
            print(f"With arguments: {tool_args}")
            answer = input("Allow or deny? (allow/deny): ")
            if answer == "allow":
                result = await self.session.call_tool(tool_name, tool_args)
                messages.append({"role": "tool", "content": str(result.content)})

                final_response = await self.ollama.chat(
                    model="llama3.1", messages=messages
                )
                return final_response.message.content
            else:
                return response.message.content

    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")

        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() == "quit":
                    break

                response = await self.process_query(query)
                print("\n" + response)

            except Exception as e:
                print(f"\nError: {str(e)}")

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()


async def main():
    client = MCPClient()
    try:
        await client.connect_to_server()
        await client.chat_loop()
    finally:
        await client.exit_stack.aclose()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (RuntimeError, BaseExceptionGroup):
        pass  # suppress noisy anyio/mcp shutdown errors
