const express = require("express");
const fs = require("fs");
const csvParser = require("csv-parser");
const axios = require("axios");
const path = require("path");

const app = express();

const FACEBOOK_PIXEL_ID = "512078474586717";
const ACCESS_TOKEN = "EAAQdOzvvr9IBO1lNOcrWxZAyOtreq0oKcCPgitjA4HhNV1P9RqIVQZAEyxbNtuGZAFIjfhWXfqjKv9of68QgT1iSJHdndL1YCYZBvzs29PDQxY6My4j9fu0sOkXRsZCrjnZBOVwqaqXwX9DIy8n6kY2Mb7fwDnCGyvCGMUpbZCEVRUK4duhgPVq8LuZAaQPGlKZB4HAZDZD";
const FB_API_URL = `https://graph.facebook.com/v13.0/${FACEBOOK_PIXEL_ID}/events`;

// Caminho do arquivo CSV
const CSV_FILE_PATH = path.join(__dirname, "12 de jan de 2025 23_59.csv");

// Função para ler o CSV e enviar os eventos
async function processarCsvEEnviarEventos() {
  const events = [];

  try {
    // Ler e processar o CSV
    fs.createReadStream(CSV_FILE_PATH)
      .pipe(csvParser())
      .on("data", (row) => {
        events.push({
          event_name: row.event,
          event_time: parseInt(row.unix_time_start),
          custom_data: {
            browser_received_count: parseInt(row.browser_received_count),
            server_received_count: parseInt(row.server_received_count),
            facebook_sdk_received_count: parseInt(row.facebook_sdk_received_count),
            mmp_received_count: parseInt(row.mmp_received_count),
            ae_api_received_count: parseInt(row.ae_api_received_count),
            total_count: parseInt(row.total_count),
          },
        });
      })
      .on("end", async () => {
        console.log("Eventos carregados do CSV. Enviando para a API...");

        try {
          // Enviar eventos para a API do Facebook
          const response = await axios.post(FB_API_URL, {
            data: events,
            access_token: ACCESS_TOKEN,
          });

          console.log("Eventos enviados com sucesso:", response.data);
        } catch (error) {
          console.error("Erro ao enviar eventos:", error.response?.data || error);
        }
      })
      .on("error", (err) => {
        console.error("Erro ao processar CSV:", err);
      });
  } catch (err) {
    console.error("Erro ao ler o arquivo CSV:", err);
  }
}

// Rota para disparar o envio de eventos
app.get("/enviar-eventos", async (req, res) => {
  await processarCsvEEnviarEventos();
  res.send("Processamento iniciado. Verifique o console para status.");
});

// Inicia o servidor
app.listen(3000, () => {
  console.log("API rodando em http://localhost:3000");
  processarCsvEEnviarEventos(); // Inicia automaticamente o processamento ao iniciar o servidor
});
