import { API_BASE_URL } from "./api";
import { logout } from "./auth";

type BackendConfig = {
  origin: string;
  pathPrefix: string;
};

class UnauthorizedError extends Error {
  constructor(message = "Unauthorized") {
    super(message);
    this.name = "UnauthorizedError";
  }
}

function normalizePathPrefix(pathname: string): string {
  if (!pathname) return "/";
  if (!pathname.startsWith("/")) {
    pathname = `/${pathname}`;
  }
  if (pathname !== "/" && pathname.endsWith("/")) {
    return pathname.slice(0, -1);
  }
  return pathname;
}

function getBackendConfig(): BackendConfig | null {
  const rawBaseUrl = API_BASE_URL;

  if (!rawBaseUrl) {
    return null;
  }

  try {
    const url = new URL(rawBaseUrl, window.location.origin);
    return {
      origin: url.origin,
      pathPrefix: normalizePathPrefix(url.pathname),
    };
  } catch {
    // If URL parsing fails, fail closed: do not attempt to intercept.
    return null;
  }
}

function getRequestUrl(input: RequestInfo | URL): URL | null {
  try {
    if (input instanceof Request) {
      return new URL(input.url, window.location.origin);
    }

    if (input instanceof URL) {
      return input;
    }

    if (typeof input === "string") {
      try {
        return new URL(input);
      } catch {
        return new URL(input, window.location.origin);
      }
    }

    return null;
  } catch {
    return null;
  }
}

function isBackendRequest(
  input: RequestInfo | URL,
  backend: BackendConfig | null
): boolean {
  if (!backend) return false;

  const url = getRequestUrl(input);
  if (!url) return false;

  if (url.origin !== backend.origin) {
    return false;
  }

  const requestPath = normalizePathPrefix(url.pathname);

  if (backend.pathPrefix === "/" || backend.pathPrefix === "") {
    // Entire origin is considered backend API.
    return true;
  }

  return (
    requestPath === backend.pathPrefix ||
    requestPath.startsWith(`${backend.pathPrefix}/`)
  );
}

function isOnSignInRoute(): boolean {
  try {
    const path = window.location?.pathname || "";
    return path === "/sign-in" || path.startsWith("/sign-in/");
  } catch {
    // If we cannot safely read location, do not attempt redirect logic.
    return false;
  }
}

function shouldHandleUnauthorized(
  response: Response,
  input: RequestInfo | URL,
  backend: BackendConfig | null
): boolean {
  if (response.status !== 401) return false;
  if (!isBackendRequest(input, backend)) return false;
  if (isOnSignInRoute()) return false;
  return true;
}

declare global {
  interface Window {
    __fetch401InterceptorInstalled__?: boolean;
  }
}

export function installFetch401Interceptor(): void {
  
  if (typeof window === "undefined" || typeof window.fetch !== "function") {
    return;
  }

  if (window.__fetch401InterceptorInstalled__) {
    return;
  }

  const backendConfig = getBackendConfig();
  if (!backendConfig) {
    // If backend config cannot be determined safely, skip installing the interceptor
    // to avoid accidental interference with unrelated requests.
    window.__fetch401InterceptorInstalled__ = true;
    return;
  }

  const originalFetch: typeof window.fetch = window.fetch.bind(window);

  const interceptedFetch: typeof window.fetch = (async (
    input: RequestInfo | URL,
    init?: RequestInit
  ): Promise<Response> => {
    const response = await originalFetch(input, init);

    if (shouldHandleUnauthorized(response, input, backendConfig)) {
      try {
        logout();
      } catch (error) {
        console.error("Error during logout after 401 response", error);
      }

      try {
        window.location.replace("/sign-in");
      } catch (error) {
        console.error("Failed to redirect after 401 response", error);
      }

      // Stop further processing in calling code.
      throw new UnauthorizedError(
        "Session expired or unauthorized. Redirecting to sign-in."
      );
    }

    return response;
  }) as typeof window.fetch;

  window.fetch = interceptedFetch;
  window.__fetch401InterceptorInstalled__ = true;
}

