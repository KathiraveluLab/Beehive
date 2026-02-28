import { getToken } from "./auth";

const BASE_URL = import.meta.env.VITE_API_URL;

export async function apiFetch(
  url: string,
  options: RequestInit = {}
) {
  const token = getToken();

  const res = await fetch(`${BASE_URL}${url}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  });

  // Read body ONCE
  const rawText = await res.text();
  let data: any = null;

  try {
    data = rawText ? JSON.parse(rawText) : null;
  } catch {
    data = rawText; // fallback for non-JSON responses
  }

  if (!res.ok) {
    throw new Error(
      data?.error ||
      data?.message ||
      rawText ||
      `Request failed (${res.status})`
    );
  }

  return data;
}
