<script setup lang="ts">
import { useAuthStore } from "~/stores/auth";

const config = useRuntimeConfig();
const auth = useAuthStore();
const router = useRouter();

const username = ref("");
const password = ref("");
const error = ref("");
const loading = ref(false);

async function handleLogin() {
  error.value = "";
  loading.value = true;
  try {
    const data: any = await $fetch(`${config.public.apiBase}/auth/login/`, {
      method: "POST",
      body: { username: username.value, password: password.value },
    });
    auth.setTokens(data.access, data.refresh);
    auth.setUser(data.user);
    router.push("/");
  } catch (e: any) {
    error.value = e?.data?.detail || "Invalid username or password.";
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-slate-50 px-4">
    <div class="w-full max-w-sm bg-white rounded-xl shadow p-6 sm:p-8">
      <h1 class="text-2xl font-bold text-slate-800 mb-1">Aptura ERP</h1>
      <p class="text-sm text-slate-500 mb-6">Sign in to your workspace</p>

      <form class="space-y-4" @submit.prevent="handleLogin">
        <div>
          <label class="block text-sm font-medium mb-1">Username</label>
          <input v-model="username" type="text" required class="w-full border rounded-lg px-3 py-2" />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Password</label>
          <input v-model="password" type="password" required class="w-full border rounded-lg px-3 py-2" />
        </div>
        <p v-if="error" class="text-sm text-red-600">{{ error }}</p>
        <button type="submit" :disabled="loading" class="w-full bg-slate-900 hover:bg-slate-700 disabled:opacity-60 text-white font-medium py-2 rounded-lg transition">
          {{ loading ? "Signing in..." : "Sign in" }}
        </button>
      </form>

      <p class="text-sm text-center mt-4 text-slate-500">
        No account? <NuxtLink to="/register" class="text-slate-900 font-medium">Register</NuxtLink>
      </p>

      <div class="text-xs text-center mt-4 text-slate-400 space-y-0.5">
        <p>Demo logins (after seed_demo_data):</p>
        <p>admin / Admin@12345 · manager / Manager@12345</p>
        <p>sales_user / Sales@12345 · inventory_user / Inventory@12345</p>
      </div>
    </div>
  </div>
</template>
