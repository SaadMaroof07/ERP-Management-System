import { useAuthStore } from "~/stores/auth";

export function useApi() {
  const config = useRuntimeConfig();
  const auth = useAuthStore();
  const router = useRouter();

  async function refreshAccessToken(): Promise<boolean> {
    if (!auth.refresh) return false;
    try {
      const data: any = await $fetch(`${config.public.apiBase}/auth/refresh/`, {
        method: "POST",
        body: { refresh: auth.refresh },
      });
      auth.setTokens(data.access, auth.refresh);
      return true;
    } catch {
      return false;
    }
  }

  async function request<T>(path: string, options: any = {}): Promise<T> {
    const doRequest = () =>
      $fetch<T>(`${config.public.apiBase}${path}`, {
        ...options,
        headers: {
          ...(options.headers || {}),
          ...(auth.access ? { Authorization: `Bearer ${auth.access}` } : {}),
        },
      });

    try {
      return await doRequest();
    } catch (err: any) {
      if (err?.response?.status === 401) {
        const refreshed = await refreshAccessToken();
        if (refreshed) return await doRequest();
        auth.logout();
        router.push("/login");
      }
      throw err;
    }
  }

  return {
    get: <T>(path: string, params?: Record<string, any>) => request<T>(path, { method: "GET", params }),
    post: <T>(path: string, body?: any) => request<T>(path, { method: "POST", body }),
    patch: <T>(path: string, body?: any) => request<T>(path, { method: "PATCH", body }),
    del: <T>(path: string) => request<T>(path, { method: "DELETE" }),
  };
}
