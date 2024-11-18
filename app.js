
const express = require('express');
const path = require('path');

const app = express();
const port = process.env.PORT || 3000;

app.use(express.static(path.join(__dirname, 'public')));

app.get('/', (req, res) => {
  res.send('Cardinali - Editor de Imagem');
});

app.listen(port, () => {
  console.log(`Servidor rodando em http://localhost:${port}`);
});