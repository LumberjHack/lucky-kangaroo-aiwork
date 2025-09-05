\# 🧠 Mindmap architecture Lucky Kangaroo



```mermaid

graph TD;

&nbsp; UI\[Frontend (React)]

&nbsp; Mobile\[Mobile App (React Native)]:::todo

&nbsp; API\[Backend (Flask)]

&nbsp; DB\[(PostgreSQL + PostGIS)]

&nbsp; Redis\[Redis (cache / queue)]

&nbsp; Celery\[Celery Worker]:::todo

&nbsp; SocketIO\[WebSockets (chat)]

&nbsp; Nginx\[Nginx Reverse Proxy]

&nbsp; Storage\[Upload (local)]



&nbsp; UI -->|REST / Axios| API

&nbsp; UI -->|WebSocket| SocketIO

&nbsp; API --> DB

&nbsp; API --> Redis

&nbsp; API --> Storage

&nbsp; SocketIO --> Redis

&nbsp; Celery --> Redis

&nbsp; API --> Celery

&nbsp; Nginx --> UI

&nbsp; Nginx --> API



&nbsp; classDef todo fill:#ffdede,stroke:#ff4e4e;



