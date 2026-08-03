<script setup lang="ts">
definePageMeta({ middleware: "auth" });

const api = useApi();
const router = useRouter();
const departments = ref<any[]>([]);
const loading = ref(false);
const errorMsg = ref("");
const blank = { first_name: "", last_name: "", email: "", phone: "", department: null, position: "", salary: 0, hire_date: new Date().toISOString().slice(0, 10), status: "active" };

onMounted(async () => {
  const data: any = await api.get("/departments/");
  departments.value = data.results || data;
});

async function handleSubmit(form: any) {
  loading.value = true;
  errorMsg.value = "";
  try {
    await api.post("/employees/", form);
    router.push("/employees");
  } catch (e: any) {
    const data = e?.data;
    errorMsg.value = data ? Object.entries(data).map(([k, v]) => `${k}: ${v}`).join(" ") : "Failed to create employee.";
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div>
    <h1 class="text-xl font-bold text-slate-800 mb-6">Add Employee</h1>
    <EmployeeForm :model-value="blank" :departments="departments" submit-label="Create Employee" :loading="loading" :error-msg="errorMsg" @submit="handleSubmit" />
  </div>
</template>
