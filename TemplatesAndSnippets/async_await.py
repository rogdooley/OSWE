import asyncio
import httpx

# Your async worker
async def do_work(client, item):
    response = await client.get(item)
    return response.status_code

# Main logic
async def main():
    items = ["https://example.com", "https://httpbin.org"]
    
    async with httpx.AsyncClient() as client:
        tasks = [do_work(client, item) for item in items]
        results = await asyncio.gather(*tasks)
        print(results)

# Entry point
if __name__ == "__main__":
    asyncio.run(main())