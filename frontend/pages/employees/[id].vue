<script setup lang="ts">
definePageMeta({ middleware: "auth" });

const api = useApi();
const router = useRouter();
const route = useRoute();
const departments = ref<any[]>([]);
const employee = ref<any>(null);
const loading = ref(false);
const errorMsg = ref("");

onMounted(async () => {
  try {
    const [emp, deps]: any = await Promise.all([api.get(`/employees/${route.params.id}/`), api.get("/departments/")]);
    employee.value = emp;
    departments.value = deps.results || deps;
  } catch {
    errorMsg.value = "Could not load this employee record.";
  }
});

async function handleSubmit(form: any) {
  loading.value = true;
  errorMsg.value = "";
  try {
    await api.patch(`/employees/${route.params.id}/`, form);
    router.push("/employees");
  } catch (e: any) {
    const data = e?.data;
    errorMsg.value = data ? Object.entries(data).map(([k, v]) => `${k}: ${v}`).join(" ") : "Failed to update employee.";
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div>
    <h1 class="text-xl font-bold text-slate-800 mb-6">Edit Employee</h1>
    <p v-if="errorMsg && !employee" class="text-red-600 text-sm">{{ errorMsg }}</p>
    <EmployeeForm v-if="employee" :model-value="employee" :departments="departments" submit-label="Save Changes" :loading="loading" :error-msg="errorMsg" @submit="handleSubmit" />
  </div>
</template>
