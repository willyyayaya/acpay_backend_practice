const express = require('express');
const mysql = require('mysql2');
const cors = require('cors');

const app = express();
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// 建立資料庫連線
const db = mysql.createConnection({
    host: 'localhost',
    user: 'root',
    password: '',
    database: 'acpay_db'
});

db.connect(err => {
    if (err) {
        console.error('資料庫連線失敗:', err);
    } else {
        console.log('成功連接到 MySQL');
    }
});

// 創建交易記錄 (Create)
app.post('/checkout', (req, res) => {

    console.log('收到 POST /checkout 請求:', req.body);
    const { email, prime } = req.body;

    if (!email || !prime) {
        return res.status(400).json({ message: '缺少必要參數 email 或 prime' });
    }

    const sql = 'INSERT INTO payments (email, prime) VALUES (?, ?)';
    db.query(sql, [email, prime], (err, result) => {
        if (err) {
            console.error('新增失敗:', err);
            return res.status(500).json({ message: '資料儲存失敗' });
        }
        res.status(201).json({ message: '付款成功!', id: result.insertId });
    });
});

// 取得所有交易記錄 (Read)
app.get('/payments', (req, res) => {

    console.log('收到 GET /payments all 請求');
    const sql = 'SELECT id, email, prime, created_at FROM payments ORDER BY created_at DESC';
    db.query(sql, (err, results) => {
        if (err) {
            console.error('查詢失敗:', err);
            return res.status(500).json({ message: '查詢失敗' });
        }
        res.json(results);
    });
});

// 更新交易記錄 (Update)
app.put('/payments/:id', (req, res) => {
    
    const { email } = req.body;
    const { id } = req.params;
    console.log('收到 PUT /payments 請求:', req.params, req.body);

    if (!email) {
        return res.status(400).json({ message: '缺少 email 欄位' });
    }

    const sql = 'UPDATE payments SET email = ? WHERE id = ?';
    db.query(sql, [email, id], (err, result) => {
        if (err) {
            console.error('更新失敗:', err);
            return res.status(500).json({ message: '更新失敗' });
        }
        if (result.affectedRows === 0) {
            return res.status(404).json({ message: '找不到該筆交易記錄' });
        }
        res.json({ message: '更新成功!' });
    });
});

// 刪除交易記錄 (Delete)
app.delete('/payments/:id', (req, res) => {

    const { id } = req.params;
    console.log('收到 DELETE /payments 請求:', req.params);
    const sql = 'DELETE FROM payments WHERE id = ?';
    db.query(sql, [id], (err, result) => {
        if (err) {
            console.error('刪除失敗:', err);
            return res.status(500).json({ message: '刪除失敗' });
        }
        if (result.affectedRows === 0) {
            return res.status(404).json({ message: '找不到該筆交易記錄' });
        }
        res.json({ message: '刪除成功!' });
    });
});

// 啟動伺服器
const PORT = 3000;
app.listen(PORT, () => {
    console.log(`伺服器運行於 http://localhost:${PORT}`);
});
