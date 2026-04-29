const express = require('express');
const router = express.Router();
const { batchQueryDestinations } = require('../services/aggregator');
const ticketService = require('../services/ticket-service');

router.get('/destinations', async (req, res) => {
  const { from_city, date, sort_by } = req.query;

  if (!from_city || !date) {
    return res.status(400).json({
      code: 1,
      message: '缺少必要参数: from_city, date',
    });
  }

  try {
    const result = await batchQueryDestinations(from_city, date);

    if (sort_by === 'price') {
      result.destinations.sort((a, b) => a.minPrice - b.minPrice);
    } else {
      result.destinations.sort((a, b) => b.totalSeats - a.totalSeats);
    }

    res.json({ code: 0, message: 'success', data: result });
  } catch (error) {
    console.error('查询可直达城市失败:', error);
    res.status(500).json({ code: 1, message: '服务器内部错误' });
  }
});

router.get('/trains', async (req, res) => {
  const { from_city, to_city, date, train_type } = req.query;

  if (!from_city || !to_city || !date) {
    return res.status(400).json({
      code: 1,
      message: '缺少必要参数: from_city, to_city, date',
    });
  }

  try {
    const result = await ticketService.queryTickets(from_city, to_city, date);

    if (!result || !result.data) {
      return res.json({
        code: 0,
        message: 'success',
        data: {
          fromStation: from_city,
          toStation: to_city,
          date,
          tickets: [],
        },
      });
    }

    let tickets = result.data;
    if (train_type && train_type !== 'all') {
      const prefixMap = {
        'G-D': ['G', 'D', 'C'],
        'K-T-Z': ['K', 'T', 'Z'],
      };
      const prefixes = prefixMap[train_type] || [train_type];
      tickets = tickets.filter((t) =>
        prefixes.some((p) => t.trainNo.startsWith(p))
      );
    }

    res.json({
      code: 0,
      message: 'success',
      data: {
        fromStation: tickets[0]?.fromStation || from_city,
        toStation: tickets[0]?.toStation || to_city,
        date,
        tickets,
      },
    });
  } catch (error) {
    console.error('查询车次详情失败:', error);
    res.status(500).json({ code: 1, message: '服务器内部错误' });
  }
});

module.exports = router;
