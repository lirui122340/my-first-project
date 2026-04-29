require('dotenv').config();
const express = require('express');
const cors = require('cors');
const ticketRouter = require('./routes/ticket');
const cityRouter = require('./routes/city');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.use('/api/ticket', ticketRouter);
app.use('/api/city', cityRouter);

app.get('/', (req, res) => {
  res.json({ code: 0, message: '省钱旅游小程序后端服务运行中' });
});

app.listen(PORT, () => {
  console.log(`服务器已启动: http://localhost:${PORT}`);
});
