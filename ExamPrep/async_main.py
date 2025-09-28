#!/usr/bin/env python3
import argparse
import asyncio
import json
from pathlib import Path
from typing import Any, Dict, Optional
import aiofiles

from poctools.async_http import AsyncRequester
from common.offsec_logger import OffsecLogger
from common.IdentityGenerator.identity_generator import IdentityGenerator

ARTIFACT_DIR = Path("artifacts")
ARTIFACT_DIR.mkdir(exist_ok=True)


def parse_args():
    parser = argparse.ArgumentParser(
        description="OSWE Application Exploit (async template)."
    )

    # Target options
    parser.add_argument("--target-ip", required=True, help="Target server IP address")
    parser.add_argument(
        "--target-port", type=int, default=80, help="Target web frontend port"
    )
    parser.add_argument(
        "--target-api-port", type=int, default=5000, help="Target API port"
    )

    # Attacker options
    parser.add_argument(
        "--listening-ip", default="127.0.0.1", help="IP to listen on for reverse shell"
    )
    parser.add_argument(
        "--listening-port",
        type=int,
        default=9001,
        help="Port to listen for reverse shell",
    )

    # Exploit options
    parser.add_argument(
        "--delay",
        type=int,
        default=3,
        help="Response delay in seconds for timing inference",
    )

    # Identity options
    parser.add_argument(
        "--user-file", default="user.json", help="Path to existing exploit user JSON"
    )
    parser.add_argument(
        "--save-identity", help="Path to save newly generated identity JSON"
    )
    parser.add_argument(
        "--register",
        action="store_true",
        help="Register the generated identity against the target",
    )
    parser.add_argument(
        "--complexity", choices=["low", "medium", "high"], help="Password complexity"
    )
    parser.add_argument(
        "--include-address", action="store_true", help="Include street address"
    )
    parser.add_argument(
        "--include-phone", action="store_true", help="Include phone number"
    )

    # Optional
    parser.add_argument("--charset", default="alnum", help="Charset to use")
    parser.add_argument(
        "--proxy", default=None, help="Proxy URL e.g. http://127.0.0.1:8080"
    )
    parser.add_argument(
        "--concurrency", type=int, default=5, help="Concurrency for registrations"
    )

    return parser.parse_args()


async def save_identity_async(identity: Dict[str, Any], path: Path):
    async with aiofiles.open(path, "w") as f:
        await f.write(json.dumps(identity, indent=2))


async def register_identity(
    ctx: Dict[str, Any],
    identity: Dict[str, Any],
    requester: AsyncRequester,
    logger: OffsecLogger,
) -> Optional[Dict[str, Any]]:
    # Placeholder registration flow. Adapt to target API.
    url = f"http://{ctx['target_ip']}:{ctx['api_port']}/api/register"
    logger.info(f"Registering {identity['username']} -> {url}")
    payload = {
        "username": identity["username"],
        "email": identity["email"],
        "password": identity["password"],
    }
    resp = await requester.post(url, json=payload)
    logger.debug(f"Registration status: {resp.status_code}")
    if resp.status_code == 200:
        try:
            return resp.json()
        except Exception:
            return {"status": "ok"}
    else:
        logger.error(f"Registration failed: {resp.status_code} {resp.text}")
        return None


async def main_async(args):
    logger = OffsecLogger(logfile=ARTIFACT_DIR / "oswe_prep.log", debug=True)

    ctx = {
        "target_ip": args.target_ip,
        "target_port": args.target_port,
        "api_port": args.target_api_port,
    }

    generator = IdentityGenerator()
    identity = generator.generate_identity(None)

    if args.save_identity:
        await save_identity_async(identity, ARTIFACT_DIR / args.save_identity)
        logger.info(f"Saved identity to {ARTIFACT_DIR / args.save_identity}")
    else:
        print(generator.as_json(identity))

    proxies = None
    if args.proxy:
        proxies = {"http://": args.proxy, "https://": args.proxy}

    async with AsyncRequester(proxies=proxies) as requester:
        if args.register:
            sem = asyncio.Semaphore(args.concurrency)

            async def _reg():
                async with sem:
                    return await register_identity(ctx, identity, requester, logger)

            result = await _reg()
            logger.info(f"Register result: {result}")

    context_path = ARTIFACT_DIR / "exploit_context.json"
    async with aiofiles.open(context_path, "w") as f:
        await f.write(
            json.dumps(
                {"target": args.target_ip, "api_port": args.target_api_port}, indent=2
            )
        )
    logger.info(f"Saved context to {context_path}")


def main():
    args = parse_args()
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
