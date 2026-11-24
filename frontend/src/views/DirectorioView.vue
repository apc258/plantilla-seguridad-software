<script setup>
import { onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { api } from "@/api";

const route = useRoute();
const router = useRouter();
const termino = ref(route.query.q || "");
const buscado = ref("");
const resultados = ref([]);
const error = ref("");

async function buscar() {
  error.value = "";
  router.replace({ query: termino.value ? { q: termino.value } : {} });
  try {
    resultados.value = (await api(`/directorio?q=${encodeURIComponent(termino.value)}`)).resultados;
    buscado.value = termino.value;
  } catch (e) {
    error.value = e.message;
  }
}

onMounted(buscar);
</script>

<template>
  <div class="col-lg-8">
    <h1 class="h3 mb-3">Directorio</h1>
    <form class="d-flex gap-2 mb-3" @submit.prevent="buscar">
      <input v-model="termino" class="form-control" placeholder="Buscar por nombre" />
      <button class="btn btn-dark">Buscar</button>
    </form>
    <p v-if="buscado" class="text-secondary" v-html="`Resultados para: <strong>${buscado}</strong>`"></p>
    <div v-if="error" class="alert alert-danger py-2">{{ error }}</div>
    <ul class="list-group">
      <li v-for="cuenta in resultados" :key="cuenta.id" class="list-group-item d-flex justify-content-between">
        <span v-html="cuenta.nombre"></span>
        <span class="badge text-bg-secondary">{{ cuenta.rol }}</span>
      </li>
    </ul>
  </div>
</template>
