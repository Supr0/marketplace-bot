import asyncio
import json
import pathlib

from parser.parser import parse_olx_endpoint, close_session


async def main() -> None:
    olx_json = await parse_olx_endpoint("iphone", 0)
    path = pathlib.Path("tests/fixtures/olx_fixture.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as file:
        json.dump(olx_json, file)
    await close_session()

if __name__ == "__main__":
    asyncio.run(main())