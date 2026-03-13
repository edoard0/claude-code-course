# Software Architecture Styles — Visual Reference

A self-contained HTML reference card for the 9 architecture styles covered in
*Fundamentals of Software Architecture* (Richards & Ford, Chapters 10–17).

## Viewing

Open the file directly in any browser:

```bash
open architecture-diagrams.html
```

No build step, no server, no install required. The only external dependency is
the Mermaid.js CDN for rendering diagrams (requires an internet connection on
first load; browsers cache it after that).

## What's Inside

| Chapter | Architecture Style |
|---------|-------------------|
| 10 | Layered |
| 11 | Pipeline (Pipes & Filters) |
| 12 | Microkernel |
| 13 | Service-Based |
| 14 | Event-Driven — Broker Topology |
| 14 | Event-Driven — Mediator Topology |
| 15 | Space-Based |
| 16 | Orchestration-Driven SOA |
| 17 | Microservices |

Each card shows:
- **Topology diagram** (Mermaid flowchart)
- **Pros** — key strengths
- **Cons** — key weaknesses
- **Best Fit** — example use cases where this style shines

## Running Tests

```bash
python3 -m pytest tests/ -v
# or without pytest:
python3 -m unittest discover tests -v
```

Tests are in `tests/test_diagrams.py` and use only the Python standard library.
