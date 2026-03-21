# Arquitectura de componentes y flujo de la aplicación

Documento visual del **AI Support Co-Pilot** (mesa de ayuda inteligente). Los diagramas usan [Mermaid](https://mermaid.js.org/) y se pueden ver en GitHub, GitLab, VS Code o cualquier visor compatible.

---

## 1. Diagrama de componentes (vista lógica)

Relación entre capas, tecnologías y servicios externos. Incluye alcance **actual (Sem I)** y **previsto (Sem II–III)**.

```mermaid
flowchart TB
    subgraph usuarios["Usuarios"]
        C[("Cliente")]
        A[("Agente")]
        AD[("Admin")]
    end

    subgraph fe["Frontend — React 18 · Vite · Tailwind · Framer Motion"]
        SPA[SPA / Dashboard]
    end

    subgraph be["Backend — FastAPI · Pydantic · Uvicorn"]
        API[API REST]
        REGLAS["Motor de reglas<br/>(Python)"]
        WEBHOOK["Webhook / eventos"]
    end

    subgraph supa["Supabase"]
        AUTH["Auth (JWT)"]
        PG[("PostgreSQL + RLS")]
        RT["Realtime<br/>(Sem II)"]
    end

    subgraph auto["Automatización — Sem II"]
        N8N["n8n"]
        TG["Telegram / Email"]
    end

    subgraph ia["IA — Sem III"]
        LLM["Llama 3.1<br/>HF / vLLM"]
    end

    C & A & AD --> SPA
    SPA <-->|"HTTPS · JSON"| API
    SPA <-->|"Sesión / tokens"| AUTH
    SPA -.->|"Suscripciones"| RT
    API <-->|"Consultas · RLS"| PG
    API --> REGLAS
    API --> WEBHOOK
    WEBHOOK --> N8N
    N8N --> TG
    API -.->|"Clasificación IA"| LLM
    LLM -.->|"Fallback"| REGLAS
    PG -.-> RT
```

---

## 2. Flujo principal de la aplicación (peticiones)

Flujo simplificado desde el navegador hasta persistencia y reglas.

```mermaid
flowchart LR
    subgraph capa1["Navegador"]
        BR[React SPA]
    end

    subgraph capa2["API"]
        FAPI[FastAPI]
    end

    subgraph capa3["Datos y seguridad"]
        SB[(Supabase)]
    end

    BR -->|"1. Login / registro"| SB
    BR -->|"2. REST + Bearer JWT"| FAPI
    FAPI -->|"3. Validación / RLS"| SB
    FAPI -->|"4. Clasificación por palabras clave"| REGLAS2[Motor reglas]
    REGLAS2 --> FAPI
```

| Paso | Tecnología | Rol |
|------|------------|-----|
| 1 | Supabase Auth | Registro, login, roles (Cliente / Agente / Admin) |
| 2 | FastAPI + JWT | Endpoints de tickets, perfiles, dashboard |
| 3 | PostgreSQL + RLS | Datos aislados por rol |
| 4 | Python (reglas) | Categoría baseline antes del LLM (Sem III) |

---

## 3. Secuencia: creación de un ticket (cliente)

```mermaid
sequenceDiagram
    autonumber
    actor U as Cliente
    participant R as React
    participant F as FastAPI
    participant S as Supabase Auth
    participant DB as PostgreSQL RLS
    participant MR as Motor reglas

    U->>R: Formulario ticket
    R->>S: Token JWT válido
    R->>F: POST /tickets + JWT
    F->>MR: Clasificar título/descripción
    MR-->>F: Categoría (reglas)
    F->>DB: INSERT ticket + categoría
    DB-->>F: OK
    F-->>R: 201 + ticket
    R-->>U: Confirmación UI
```

---

## 4. Secuencia: visión futura (webhook + n8n + LLM)

```mermaid
sequenceDiagram
    autonumber
    participant F as FastAPI
    participant DB as Supabase
    participant N as n8n
    participant T as Telegram
    participant L as LLM

    F->>DB: Ticket creado / actualizado
    F->>N: Webhook (evento)
    N->>T: Notificación
    F->>L: Inferencia categoría / sentimiento
    L-->>F: JSON estructurado
    alt LLM falla
        F->>F: Motor de reglas (fallback)
    end
    F->>DB: Persistir resultado
```

---

## 5. Despliegue local (referencia)

```mermaid
flowchart TB
    subgraph dev["Entorno desarrollo"]
        DC["Docker Compose"]
        FE["frontend · Vite dev"]
        BE["python-api · Uvicorn"]
    end

    subgraph cloud["Servicios gestionados"]
        SUPA["Supabase Cloud"]
    end

    FE <-->|HTTP| BE
    BE <-->|SSL| SUPA
    DC -.-> FE
    DC -.-> BE
```

---

## Referencias

- Detalle de stack y diagramas previos: [`Entrega I/2. arquitectura_stack.md`](./Entrega%20I/2.%20arquitectura_stack.md)
- Procesos de negocio: [`Entrega I/3.modelado_de_procesos.md`](./Entrega%20I/3.modelado_de_procesos.md)
