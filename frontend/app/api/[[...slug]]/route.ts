// File: frontend/app/api/[[...slug]]/route.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

// This catch‑all route intercepts any request under /api/*.
// It proxies to the backend if NEXT_PUBLIC_API_URL is defined.
// When no backend is reachable (e.g., Vercel preview without API service),
// it returns a minimal success response to avoid 500 crashes. Specific routes can be overridden by adding dedicated route files.

export async function GET(request: NextRequest) {
  return handle(request);
}
export async function POST(request: NextRequest) {
  return handle(request);
}
export async function PUT(request: NextRequest) {
  return handle(request);
}
export async function DELETE(request: NextRequest) {
  return handle(request);
}

async function handle(request: NextRequest) {
  const backendBase = process.env.NEXT_PUBLIC_API_URL;
  const { pathname, search } = new URL(request.url);
  // Extract the part after /api/
  const slug = pathname.replace(/^\/api\//, '');
  const targetUrl = backendBase ? `${backendBase}/${slug}${search}` : null;

  if (targetUrl) {
    try {
      const resp = await fetch(targetUrl, {
        method: request.method,
        headers: {
          'Content-Type': 'application/json',
          ...(Object.fromEntries(request.headers.entries()))
        },
        body: request.method !== 'GET' && request.method !== 'HEAD' ? await request.text() : undefined,
      });
      const data = await resp.json();
      return NextResponse.json(data, { status: resp.status });
    } catch (err) {
      console.warn('[JOBMUNI] Proxy API error, falling back to empty response:', err);
    }
  }
  // Generic fallback – return empty JSON object with 200 OK to keep UI stable.
  return NextResponse.json({ status: 'fallback', message: 'No backend reachable' }, { status: 200 });
}
