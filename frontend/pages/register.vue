<script setup lang="ts">
const config = useRuntimeConfig();
const router = useRouter();

const form = reactive({ username: "", email: "", first_name: "", last_name: "", password: "" });
const error = ref("");
const success = ref(false);
const loading = ref(false);

async function handleRegister() {
  error.value = "";
  loading.value = true;
  try {
    await $fetch(`${config.public.apiBase}/auth/register/`, { method: "POST", body: form });
    success.value = true;
    setTimeout(() => router.push("/login"), 1200);
  } catch (e: any) {
    const data = e?.data;
    error.value = data ? Object.values(data).flat().join(" ") : "Registration failed.";
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-slate-50 px-4">
    <div class="w-full max-w-sm bg-white rounded-xl shadow p-6 sm:p-8">
      <h1 class="text-2xl font-bold text-slate-800 mb-1">Create account</h1>
      <p class="text-sm text-slate-500 mb-6">New accounts get "employee" access. An admin can promote your role later.</p>

      <form class="space-y-3" @submit.prevent="handleRegister">
        <div class="grid grid-cols-2 gap-3">
          <input v-model="form.first_name" placeholder="First name" required class="border rounded-lg px-3 py-2" />
          <input v-model="form.last_name" placeholder="Last name" required class="border rounded-lg px-3 py-2" />
        </div>
        <input v-model="form.username" placeholder="Username" required class="w-full border rounded-lg px-3 py-2" />
        <input v-model="form.email" type="email" placeholder="Email" required class="w-full border rounded-lg px-3 py-2" />
        <input v-model="form.password" type="password" placeholder="Password (min 8 characters)" required class="w-full border rounded-lg px-3 py-2" />

        <p v-if="error" class="text-sm text-red-600">{{ error }}</p>
        <p v-if="success" class="text-sm text-green-600">Account created! Redirecting to login...</p>

        <button type="submit" :disabled="loading" class="w-full bg-slate-900 hover:bg-slate-700 disabled:opacity-60 text-white font-medium py-2 rounded-lg transition">
          {{ loading ? "Creating..." : "Create account" }}
        </button>
      </form>

      <p class="text-sm text-center mt-4 text-slate-500">
        Already have an account? <NuxtLink to="/login" class="text-slate-900 font-medium">Sign in</NuxtLink>
      </p>
    </div>
  </div>
</template>
