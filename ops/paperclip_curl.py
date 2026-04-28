from __future__ import annotations

import json
import os
import subprocess
from typing import Any
from urllib.parse import urlparse
from urllib.request import Request, urlopen


DEFAULT_API_BASE = 'http://127.0.0.1:3100'


class PaperclipCurlError(RuntimeError):
    def __init__(self, status_code: int, body: str):
        self.status_code = status_code
        self.body = body
        super().__init__(f'paperclip curl request failed with status {status_code}: {body[:500]}')



def resolve_api_base(base_url: str | None = None) -> str:
    candidate = base_url or os.getenv('PAPERCLIP_API_URL') or DEFAULT_API_BASE
    return candidate.rstrip('/')



def build_api_url(path: str, base_url: str | None = None) -> str:
    if path.startswith('http://') or path.startswith('https://'):
        return path
    base = resolve_api_base(base_url)
    normalized = path if path.startswith('/') else f'/{path}'
    if base.endswith('/api'):
        if not normalized.startswith('/api/'):
            if normalized == '/api':
                return f'{base}'
            normalized = f'/api{normalized}'
    else:
        if not normalized.startswith('/api/'):
            if normalized == '/api':
                return f'{base}/api'
            normalized = f'/api{normalized}'
    return f'{base}{normalized}'



def is_local_trusted_mode(url: str) -> bool:
    parsed = urlparse(url)
    host = (parsed.hostname or '').strip().lower()
    if host not in {'127.0.0.1', 'localhost', '::1'}:
        return False

    base = f'{parsed.scheme}://{parsed.netloc}'
    health_url = build_api_url('/api/health', base_url=base)
    try:
        request = Request(health_url, headers={'Accept': 'application/json'})
        with urlopen(request, timeout=5) as response:
            payload = json.loads(response.read().decode('utf-8'))
    except Exception:
        return False
    return payload.get('deploymentMode') == 'local_trusted'



def build_curl_command(method: str, url: str, payload: dict[str, Any] | None = None) -> list[str]:
    command = [
        'curl',
        '-sS',
        '-X',
        method.upper(),
        url,
    ]

    api_key = os.getenv('PAPERCLIP_API_KEY', '').strip()
    if api_key:
        command.extend([
            '-H',
            f'Authorization: Bearer {api_key}',
        ])
    elif not is_local_trusted_mode(url):
        raise RuntimeError('PAPERCLIP_API_KEY is required unless Paperclip is running in local_trusted mode on loopback')

    if payload is not None:
        command.extend([
            '-H',
            'Content-Type: application/json',
            '--data-binary',
            json.dumps(payload, ensure_ascii=False),
        ])
    return command



def curl_json(method: str, path: str, payload: dict[str, Any] | None = None, base_url: str | None = None) -> Any:
    url = build_api_url(path, base_url=base_url)
    command = build_curl_command(method=method, url=url, payload=payload)
    command.extend(['-w', '\n%{http_code}'])
    completed = subprocess.run(command, capture_output=True, text=True, timeout=120)
    if completed.returncode != 0:
        stderr = completed.stderr.strip() or completed.stdout.strip()
        raise RuntimeError(f'curl request failed: {stderr}')
    raw_output = completed.stdout
    body, _, status_text = raw_output.rpartition('\n')
    status_code = int(status_text.strip()) if status_text.strip().isdigit() else 0
    if status_code >= 400:
        raise PaperclipCurlError(status_code, body.strip())
    payload_text = body.strip()
    return json.loads(payload_text) if payload_text else {}
