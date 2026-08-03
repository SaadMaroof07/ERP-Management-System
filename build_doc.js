const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell,
  WidthType, ShadingType, AlignmentType, LevelFormat, PageBreak, ImageRun,
} = require("docx");

const NUMBERING_REF = "bullets";

function bulletList(items) {
  return items.map((t) => new Paragraph({
    numbering: { reference: NUMBERING_REF, level: 0 },
    spacing: { after: 80 },
    children: [new TextRun(t)],
  }));
}

function numberedSteps(items) {
  return items.map((t, i) => new Paragraph({
    spacing: { after: 80 },
    children: [new TextRun({ text: `${i + 1}. `, bold: true }), new TextRun(t)],
  }));
}

function cell(text, opts = {}) {
  return new TableCell({
    width: { size: opts.width || 2000, type: WidthType.DXA },
    shading: opts.header ? { type: ShadingType.CLEAR, fill: "1e3a8a" } : undefined,
    children: [new Paragraph({ children: [new TextRun({
      text, bold: !!opts.header, color: opts.header ? "FFFFFF" : "000000", size: 19,
    })] })],
  });
}

function makeTable(headers, rows, colWidths) {
  const headerRow = new TableRow({
    tableHeader: true,
    children: headers.map((h, i) => cell(h, { header: true, width: colWidths[i] })),
  });
  const bodyRows = rows.map((r) => new TableRow({
    children: r.map((v, i) => cell(v, { width: colWidths[i] })),
  }));
  return new Table({
    columnWidths: colWidths,
    width: { size: colWidths.reduce((a, b) => a + b, 0), type: WidthType.DXA },
    rows: [headerRow, ...bodyRows],
  });
}

const diagramBuffer = fs.readFileSync(__dirname + "/architecture-diagram.png");

const doc = new Document({
  numbering: {
    config: [{
      reference: NUMBERING_REF,
      levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 720, hanging: 360 } } } }],
    }],
  },
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 } } },
    children: [
      // ---------------- Title page ----------------
      new Paragraph({ text: "APTURA TECH SOLUTIONS", heading: HeadingLevel.TITLE, alignment: AlignmentType.CENTER, spacing: { after: 200 } }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 100 },
        children: [new TextRun({ text: "1-Month Internship Program — Batch 02", bold: true, size: 28 })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 400 },
        children: [new TextRun({ text: "Week 03 Task — Full Stack Development", size: 26 })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 100 },
        children: [new TextRun({ text: "Task 01: Enterprise Resource Management (ERP) System", bold: true, size: 28, color: "1e3a8a" })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 600 },
        children: [new TextRun({ text: "Stack: Django REST Framework · Nuxt 3 (Vue) · PostgreSQL", italics: true, size: 22 })] }),
      new Paragraph({ children: [new PageBreak()] }),

      // ---------------- 1. Overview ----------------
      new Paragraph({ text: "1. Project Overview", heading: HeadingLevel.HEADING_1 }),
      new Paragraph({ spacing: { after: 200 }, children: [new TextRun(
        "This submission implements an ERP system covering Employee Management, Inventory Management, a Sales " +
        "module linked to Inventory, Reports, Role-Based Access Control (RBAC), Activity Logs, and a fully " +
        "documented REST API, built on Django REST Framework, Nuxt 3, and PostgreSQL."
      )] }),

      new Paragraph({ text: "1.1 Modules Implemented", heading: HeadingLevel.HEADING_2 }),
      ...bulletList([
        "Employee Management — departments and employees, full CRUD, search/filter/pagination",
        "Inventory Management — categories, products, and a full stock-movement ledger (in / out / adjustment) that is the audit trail behind every stock change",
        "Sales Module — checkout deducts inventory automatically inside one atomic transaction; cancelling a sale restocks every item the same way",
        "Reports — dashboard KPIs, sales, inventory, and employee summaries, restricted to admin/manager",
        "Role-Based Access Control — 5 roles (admin, manager, sales, inventory, employee) enforced by dedicated permission classes on every endpoint, not just hidden in the UI",
        "Activity Logs — every login and every create/update/delete anywhere in the system is written to an audit table with who, what, and when",
      ]),

      new Paragraph({ text: "1.2 Setup", heading: HeadingLevel.HEADING_2 }),
      new Paragraph({ spacing: { after: 100 }, children: [new TextRun(
        "Full instructions are in README.md and database/README.md. In short: create the PostgreSQL database, " +
        "pip install the backend and run migrate + seed_demo_data, then npm install (with --legacy-peer-deps) and " +
        "npm run dev the frontend."
      )] }),

      new Paragraph({ children: [new PageBreak()] }),

      // ---------------- 2. Question 1 ----------------
      new Paragraph({ text: "2. Question 1 — Architecture for 100,000 Concurrent Users", heading: HeadingLevel.HEADING_1 }),
      new Paragraph({ spacing: { after: 200 }, children: [new TextRun(
        "The current setup — a single Django process, a single Nuxt process, and a single PostgreSQL instance — is " +
        "deliberately simple and fine for development or a small pilot, but it has no redundancy and one database " +
        "connection ceiling. At 100,000 concurrent users, every layer needs to become horizontally scalable, and " +
        "the diagram below shows the target design; the sections after it explain each layer's role."
      )] }),

      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 100 },
        children: [new ImageRun({ data: diagramBuffer, transformation: { width: 580, height: 475 }, type: "png" })],
      }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 250 },
        children: [new TextRun({ text: "Figure 1 — High-availability architecture (also in docs/architecture-diagram.svg)", italics: true, size: 18 })] }),

      new Paragraph({ text: "2.1 Load Balancing & Server Scaling", heading: HeadingLevel.HEADING_2 }),
      new Paragraph({ spacing: { after: 150 }, children: [new TextRun(
        "Because authentication uses stateless JWTs rather than server-side sessions, the Django API can already " +
        "run as many identical, interchangeable instances as needed. A load balancer (Nginx, or a managed one like " +
        "AWS ALB) distributes requests round-robin across an auto-scaling group of app servers, with health checks " +
        "removing any instance that stops responding. The group scales out automatically based on CPU or request-" +
        "queue depth during peak hours and scales back in afterward, so capacity — and cost — matches real demand " +
        "instead of being sized for the worst case at all times."
      )] }),

      new Paragraph({ text: "2.2 Caching", heading: HeadingLevel.HEADING_2 }),
      ...bulletList([
        "A CDN/edge cache in front of everything serves static assets and any cacheable GET responses without the request ever reaching an app server.",
        "A Redis cluster caches frequently-read, rarely-changed data — category lists, dashboard report numbers, product lookups — with short TTLs and explicit invalidation on writes, so a large share of read traffic never touches PostgreSQL at all.",
        "Redis also backs the rate-limiter counters (login throttling) and, if session data were ever needed, a shared session store — so any app server can serve any request statelessly.",
      ]),

      new Paragraph({ text: "2.3 Database Optimization", heading: HeadingLevel.HEADING_2 }),
      ...bulletList([
        "PgBouncer connection pooling sits between the app servers and PostgreSQL: with dozens of app instances each potentially opening many connections, pooling keeps PostgreSQL's actual connection count bounded and predictable.",
        "A primary + read-replica topology sends writes (creating a sale, updating stock) to the primary and read-heavy queries (reports, employee/product listings) to replicas, since reads vastly outnumber writes in an ERP workload.",
        "The indexes already defined on the models (see database/schema.sql — e.g. product category+active, sale status+date, employee status/department) keep the most common filtered/sorted queries off full table scans as data grows.",
        "At very high sales volume, the sales_sale/sales_saleitem tables are natural candidates for time-based partitioning (e.g. monthly), so old partitions can be archived and hot queries only scan recent data.",
      ]),

      new Paragraph({ text: "2.4 Asynchronous Processing & Server Scaling", heading: HeadingLevel.HEADING_2 }),
      new Paragraph({ spacing: { after: 150 }, children: [new TextRun(
        "Anything that isn't needed for an immediate response — generating a large report export, sending a low-" +
        "stock notification email, a bulk product/employee import — is moved into a task queue (Celery + Redis/" +
        "RabbitMQ) and picked up by a separate pool of background workers. This keeps request-handling app servers " +
        "fast and responsive under load, and the worker pool can be scaled independently of the API tier since its " +
        "load profile is different (fewer, heavier jobs vs. many small requests)."
      )] }),

      new Paragraph({ text: "2.5 Reliability", heading: HeadingLevel.HEADING_2 }),
      ...bulletList([
        "Multi-availability-zone deployment for the app tier and the database, so a single zone outage doesn't take the system down.",
        "Automated failover on the PostgreSQL primary, with streaming replication already in place from 2.3.",
        "The CDN/edge layer absorbs sudden traffic spikes before they ever reach the origin infrastructure.",
      ]),

      new Paragraph({ children: [new PageBreak()] }),

      // ---------------- 3. Question 2 ----------------
      new Paragraph({ text: "3. Question 2 — Deployment Strategy", heading: HeadingLevel.HEADING_1 }),

      new Paragraph({ text: "3.1 Containerization with Docker", heading: HeadingLevel.HEADING_2 }),
      new Paragraph({ spacing: { after: 150 }, children: [new TextRun(
        "Each service gets its own image: a Django API image (gunicorn + the Django app), a Nuxt image (built, " +
        "served via node or as static output behind Nginx), and standard images for PostgreSQL and Redis in " +
        "development. A docker-compose.yml ties them together locally so 'it works on my machine' and 'it works in " +
        "production' are the same environment. In production, the same images are deployed to a container " +
        "orchestrator (Kubernetes, or a simpler managed option like AWS ECS) which handles restarts, scaling, and " +
        "rolling updates."
      )] }),

      new Paragraph({ text: "3.2 CI/CD Pipeline", heading: HeadingLevel.HEADING_2 }),
      new Paragraph({ spacing: { after: 100 }, children: [new TextRun(
        "A pipeline (GitHub Actions is a natural fit given the source is on GitHub) runs on every push/PR:"
      )] }),
      ...numberedSteps([
        "Lint + type-check both backend (flake8/ruff) and frontend (oxlint/eslint)",
        "Run the automated test suite (see 3.3) — the pipeline fails fast if tests fail, before anything is built",
        "Build the Docker images and push them to a container registry, tagged with the commit SHA",
        "Deploy to a staging environment automatically; deploy to production only after a manual approval gate or on merge to main",
        "Run a smoke test against the newly deployed environment (e.g. hit /api/reports/dashboard/ with a test token) before marking the deploy successful",
      ]),

      new Paragraph({ text: "3.3 Automated Testing", heading: HeadingLevel.HEADING_2 }),
      ...bulletList([
        "Unit tests for model logic — e.g. a stock movement can never take quantity_in_stock negative, a sale total always matches the sum of its line items.",
        "API/integration tests per endpoint — RBAC tests specifically (each role gets the expected 200/403 for each endpoint) since permission regressions are the highest-risk kind of bug in an ERP system.",
        "A transaction-safety test that simulates two concurrent checkouts on the last unit of a product, asserting exactly one succeeds and stock never goes negative — this directly tests the select_for_update() locking used in the Sales/Inventory checkout code.",
        "Frontend: component tests for the sale-checkout cart logic (quantity limits, total calculation) at minimum.",
      ]),

      new Paragraph({ text: "3.4 Environment Variables & Secrets", heading: HeadingLevel.HEADING_2 }),
      ...bulletList([
        "SECRET_KEY, database credentials, and CORS origins are all read from environment variables (see backend/.env.example), never hardcoded — the same Docker image is reused unchanged across dev/staging/production purely by changing env vars.",
        "In production, secrets are injected via the platform's secret manager (AWS Secrets Manager, Kubernetes Secrets, or the CI/CD platform's encrypted secrets) rather than committed .env files.",
        "DEBUG=False in every non-local environment, which also turns on the stricter security settings already wired up in settings.py (SECURE_SSL_REDIRECT, HSTS, secure cookies).",
      ]),

      new Paragraph({ text: "3.5 Backup Strategy", heading: HeadingLevel.HEADING_2 }),
      ...bulletList([
        "Automated nightly full backups of PostgreSQL plus continuous WAL archiving, enabling point-in-time recovery to any moment, not just the last nightly snapshot.",
        "Backups stored in a separate region/availability zone from the primary database, so a regional outage can't take out both the database and its backups.",
        "Scheduled restore drills (e.g. monthly) to an isolated environment — an untested backup is not a real backup.",
      ]),

      new Paragraph({ text: "3.6 Monitoring", heading: HeadingLevel.HEADING_2 }),
      ...bulletList([
        "Prometheus + Grafana for metrics: request latency, error rate, queue depth, DB connection pool usage, per-instance CPU/memory.",
        "Centralized log aggregation (ELK stack or Grafana Loki) so logs from every app server/worker are searchable in one place instead of per-instance.",
        "Alerting (PagerDuty, Slack webhook) on error-rate spikes, latency SLO breaches, and queue backlog growth, so problems are caught before users report them.",
        "The Activity Log feature built into the application itself (Section 1.1) complements infrastructure monitoring by answering a different question: not 'is the system healthy' but 'who did what, and when' — useful for both security review and debugging business-logic issues.",
      ]),

      new Paragraph({ children: [new PageBreak()] }),
      new Paragraph({ text: "4. Deliverables Checklist", heading: HeadingLevel.HEADING_1 }),
      ...bulletList([
        "Complete Source Code — backend/ (Django) and frontend/ (Nuxt)",
        "API Documentation — docs/API_DOCUMENTATION.md",
        "Database Design — database/schema.sql + database/README.md",
        "Architecture Diagram — docs/architecture-diagram.svg (also Figure 1 above)",
        "Technical Report — this document",
        "Demo Video — see docs/DEMO_VIDEO_SCRIPT.md for the recording script; screenshots list in docs/SCREENSHOTS.md",
      ]),
    ],
  }],
});

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync(__dirname + "/Aptura_ERP_Technical_Report.docx", buf);
  console.log("written");
});
