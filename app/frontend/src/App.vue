<template>
  <div id="app">
    <h1>Formulário de Cadastro</h1>
    <form @submit.prevent="submitForm">
      <div>
        <label for="registro_ans">Registro ANS:</label>
        <input v-model="form.registro_ans" type="text" id="registro_ans" />
      </div>
      <div>
        <label for="cnpj">CNPJ:</label>
        <input v-model="form.cnpj" type="text" id="cnpj" />
      </div>
      <div>
        <label for="razao_social">Razão Social:</label>
        <input v-model="form.razao_social" type="text" id="razao_social" />
      </div>
      <div>
        <label for="cidade">Cidade:</label>
        <input v-model="form.cidade" type="text" id="cidade" />
      </div>
      <button type="submit">Enviar</button>
    </form>

    <div v-if="response">
      <h2>Resultado:</h2>
      <pre>{{ response }}</pre>
    </div>
  </div>
</template>

<script>
import { ref } from "vue";
import axios from "axios";

export default {
  setup() {
    const form = ref({
      registro_ans: "",
      cnpj: "",
      razao_social: "",
      cidade: "",
    });

    const response = ref(null);

    const submitForm = async () => {
      try {
        const result = await axios.post("http://localhost:8000/search", form.value);
        response.value = result.data;
        console.log("Success:", result.data);
      } catch (error) {
        console.error("Error:", error);
        response.value = { error: "Ocorreu um erro ao enviar os dados" };
      }
    };

    return {
      form,
      submitForm,
      response,
    };
  },
};
</script>

<style scoped>
#app {
  font-family: Arial, sans-serif;
  padding: 20px;
  max-width: 600px;
  margin: 0 auto;
}

h1 {
  text-align: center;
  margin-bottom: 20px;
}

form {
  display: grid;
  gap: 15px;
}

label {
  font-weight: bold;
}

input {
  padding: 8px;
  font-size: 16px;
  width: 100%;
  border: 1px solid #ccc;
  border-radius: 4px;
}

button {
  padding: 10px 20px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:hover {
  background-color: #45a049;
}

div {
  margin-top: 20px;
}

pre {
  background-color: #f4f4f4;
  color: black;
  padding: 10px;
  border-radius: 4px;
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style>
