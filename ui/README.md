# TidyLab UI

Modern React + Vite frontend for the TidyLab inventory system.

## Development

```bash
npm install
npm run dev
```


---
**This UI is part of TidyLab, a rebranded fork of [Wheretf](https://github.com/ndemarco/wheretf) by [ndemarco](https://github.com/ndemarco). Rebranded and maintained by Ruben Costa.**
---

## Build

```bash
npm run build
```

This generates static HTML/CSS/JS in `../frontend/dist` that can be served by the Flask backend.

## Integration with Backend

The built UI is served by Nginx from the `frontend/dist` directory. The Flask backend API at `/api/*` remains unchanged.

### Build Pipeline

1. React components are compiled to static HTML/JS
2. Tailwind CSS is processed and minified
3. Code is split into chunks for optimal loading
4. Output is placed in `frontend/dist` for Nginx to serve

All API calls should use `/api/` prefix and will be proxied to the Python backend.
