#!/usr/bin/env python3
"""
Generate a minimal OpenAPI (v3) JSON file by introspecting the Flask app's routes.
This is intended for development only; run from project root or via `./api/scripts/build_swagger.sh`.

The output is written to `ui/dist/openapi.json` so the frontend/nginx can serve it.
"""
import json
import os
from pathlib import Path

import sys

# When this file lives in `api/scripts/`, parents[2] is the project root
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'api'))

from app import create_app


def short_summary(doc: str) -> str:
    if not doc:
        return ''
    return doc.strip().splitlines()[0]


def build_openapi(app):
    spec = {
        'openapi': '3.0.0',
        'info': {
            'title': 'Wheretf Inventory API',
            'version': os.environ.get('VERSION', 'dev'),
            'description': 'Auto-generated OpenAPI spec (development)'
        },
        'paths': {}
    }

    for rule in sorted(app.url_map.iter_rules(), key=lambda r: r.rule):
        # skip static endpoints and non-API routes
        if rule.endpoint == 'static':
            continue
        if not rule.rule.startswith('/api'):
            continue

        methods = sorted([m for m in rule.methods if m not in ('HEAD', 'OPTIONS')])
        view_fn = app.view_functions.get(rule.endpoint)
        doc = (view_fn.__doc__ or '').strip() if view_fn else ''

        path_item = spec['paths'].setdefault(rule.rule, {})
        for method in methods:
            op = {
                'summary': short_summary(doc),
                'description': doc,
                'responses': {
                    '200': {
                        'description': 'Successful response'
                    }
                }
            }
            path_item[method.lower()] = op

    return spec


def main():
    app = create_app()
    # create a testing request context to avoid issues when introspecting
    with app.test_request_context():
        spec = build_openapi(app)

    # write the generated spec into the backend's static folder so the
    # backend can serve it directly at /api/openapi.json
    out_dir = ROOT / 'api' / 'static'
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / 'openapi.json'

    with open(out_file, 'w') as f:
        json.dump(spec, f, indent=2)

    print(f'Wrote OpenAPI spec to: {out_file}')


if __name__ == '__main__':
    main()
