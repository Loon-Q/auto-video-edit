"""Use OpenMotion's native stdio MCP from an agent with terminal access."""
import json
import subprocess


def run_mcp(command, cwd, env, name=None, arguments=None):
    def send(message):
        process.stdin.write(json.dumps(message, ensure_ascii=False) + "\n")
        process.stdin.flush()

    def request(number, method, params):
        send({"jsonrpc": "2.0", "id": number, "method": method, "params": params})
        for line in process.stdout:
            reply = json.loads(line)
            if reply.get("id") == number:
                if "error" in reply:
                    raise RuntimeError(reply["error"])
                return reply["result"]
        raise RuntimeError("OpenMotion MCP 提前退出")

    with subprocess.Popen(
        command, cwd=cwd, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, encoding="utf-8"
    ) as process:
        try:
            request(1, "initialize", {
                "protocolVersion": "2025-03-26",
                "capabilities": {},
                "clientInfo": {"name": "product-video-edit", "version": "1.0.0"},
            })
            send({"jsonrpc": "2.0", "method": "notifications/initialized"})
            if name is None:
                return request(2, "tools/list", {})
            if not name.startswith("openmotion_"):
                name = "openmotion_" + name
            return request(2, "tools/call", {"name": name, "arguments": arguments})
        finally:
            process.stdin.close()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
