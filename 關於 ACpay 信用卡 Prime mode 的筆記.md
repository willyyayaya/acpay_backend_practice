---
title: 關於 ACpay 信用卡 Prime mode 的筆記

---

關於 ACpay 信用卡 Prime mode 的筆記
===
設計幾個測試網頁(JavaScript version、Python version)
---
主要參考 <https://www.acpay.com.tw/develop-doc-creditcard-prime-mode/> 的範例，並可以透過 Postman 執行 CRUD 功能，程式碼可以在 <https://github.com/willyyayaya/acpay_backend_practice> 查看。

### PRIME Mode Nodejs version
先展示 JavaScript 版本，透過 Node.js 實現，下方是 acpay_nodejs.html 的程式碼。
```
<!DOCTYPE html>
<html lang="en">

<head>
    <title>PRIME Mode(Nodejs version)</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">
    <style>
        body { margin: 20px 0; }
        .jumbotron { text-align: center; }
        .container { max-width: 750px; }
        form { padding: 40px; box-shadow: 0 7px 14px rgba(50, 50, 93, 0.1), 0 3px 6px rgba(0, 0, 0, 0.08); }
    </style>
</head>

<body>
<div class="container">
    <form id="payment-form">
        <div class="form-group">
            <label for="email">Email address</label>
            <input type="email" class="form-control" id="email" required placeholder="Email">
        </div>
        <div class="form-group card-number-group">
            <label for="card-number">卡號</label>
            <div class="form-control card-number"></div>
        </div>
        <div class="form-group expiration-date-group">
            <label for="expiration-date">卡片到期日</label>
            <div class="form-control expiration-date" id="acpay-expiration-date"></div>
        </div>
        <div class="form-group cvc-group">
            <label for="cvc">卡片後三碼</label>
            <div class="form-control cvc"></div>
        </div>
        <button type="submit" class="btn btn-primary">提交付款</button>
    </form>
    <br>
    <div id="result" class="jumbotron text-left"></div>

    <h3>交易記錄管理</h3>
    <button class="btn btn-info" onclick="fetchPayments()">取得所有交易記錄</button>
    <br><br>

    <div class="form-group">
        <label for="update-id">交易記錄 ID</label>
        <input type="number" class="form-control" id="update-id" placeholder="輸入交易記錄 ID">
    </div>
    <div class="form-group">
        <label for="update-email">更新 Email</label>
        <input type="email" class="form-control" id="update-email" placeholder="輸入新的 Email">
    </div>
    <button class="btn btn-warning" onclick="updatePayment()">更新交易記錄</button>
    <div class="form-group">
        <label for="delete-id">刪除交易記錄 ID</label>
        <input type="number" class="form-control" id="delete-id" placeholder="輸入交易記錄 ID">
    </div>
    <button class="btn btn-danger" onclick="deletePayment()">刪除交易記錄</button>
</div>

<script src="https://code.jquery.com/jquery-3.2.1.min.js"></script>
<script src="https://connectjs.payloop.com.tw/ACconnect/v1.0.3.js"></script>
<script>
    // 初始化信用卡 SDK
    ACconnect.setupSDK('090414780201003', '854b72ab-3828-4994-ab6c-16b5145937a8', 'sandbox');
    ACconnect.card.setup({
        fields: {
            number: { element: '.form-control.card-number', placeholder: '4444 3333 2222 1111' },
            expirationDate: { element: document.getElementById('acpay-expiration-date'), placeholder: '08 / 28' },
            ccv: { element: '.form-control.cvc', placeholder: '886' }
        }
    });

    // 創建交易記錄 (Create)
    $('#payment-form').on('submit', function (event) {
        event.preventDefault();
        ACconnect.card.getPrime(function (result) {
            if (result.status !== 0) {
                alert('錯誤: ' + result.msg);
                return;
            }
            const email = $('#email').val();
            fetch('http://localhost:3000/checkout', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: email, prime: result.card.prime })
            })
            .then(res => {
                if (!res.ok) {
                    throw new Error('伺服器錯誤: ' + res.status);
                }
                return res.json();
            })
            .then(data => $('#result').text(data.message))
            .catch(err => console.error('發生錯誤:', err));

        });
    });

    // 取得所有交易記錄 (Read)
    function fetchPayments() {
        fetch('http://localhost:3000/payments')
            .then(response => response.json())
            .then(data => {
                let output = '<h4>交易記錄：</h4><ul>';
                data.forEach(payment => {
                    output += `<li>ID: ${payment.id}, Email: ${payment.email}, Prime: ${payment.prime}</li>`;
                });
                output += '</ul>';
                document.getElementById('result').innerHTML = output;
            })
            .catch(err => console.error('查詢失敗:', err));
    }

    // 更新交易記錄 (Update)
    function updatePayment() {
        const id = document.getElementById('update-id').value;
        const email = document.getElementById('update-email').value;
        fetch(`http://localhost:3000/payments/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: email })
        })
        .then(res => res.json())
        .then(data => {
            document.getElementById('result').innerText = data.message;
            fetchPayments(); // 重新取得交易記錄
        })
        .catch(err => console.error('更新失敗:', err));
    }

    // 刪除交易記錄 (Delete)
    function deletePayment() {
        const id = document.getElementById('delete-id').value;
        fetch(`http://localhost:3000/payments/${id}`, {
            method: 'DELETE'
        })
        .then(res => res.json())
        .then(data => {
            document.getElementById('result').innerText = data.message;
            fetchPayments(); // 重新取得交易記錄
        })
        .catch(err => console.error('刪除失敗:', err));
    }
</script>
</body>

</html>
```
可以直接在網頁執行 CRUD 功能，其中資料庫為 MySQL 系統，裡面會儲存交易記錄 ID(ID)、信箱(email)、Prime資訊(prime)和交易時間(create_at)。
資料庫的檔案在 mysql 資料夾，可以直接匯入。

執行 Nodejs
---
到 acpay-server 資料夾並用終端機執行
```
node server.js
```
正確執行的話，終端機會顯示
```
伺服器運行於 http://localhost:3000
成功連接到 MySQL
```

### PRIME Mode FastAPI version
接者展示 Python 版本，透過 FastAPI 實現，下方是 acpay_fastapi.html 的程式碼。

```
<!DOCTYPE html>
<html lang="en">

<head>
    <title>PRIME Mode(Nodejs version)</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">
    <style>
        body { margin: 20px 0; }
        .jumbotron { text-align: center; }
        .container { max-width: 750px; }
        form { padding: 40px; box-shadow: 0 7px 14px rgba(50, 50, 93, 0.1), 0 3px 6px rgba(0, 0, 0, 0.08); }
    </style>
</head>

<body>
<div class="container">
    <form id="payment-form">
        <div class="form-group">
            <label for="email">Email address</label>
            <input type="email" class="form-control" id="email" required placeholder="Email">
        </div>
        <div class="form-group card-number-group">
            <label for="card-number">卡號</label>
            <div class="form-control card-number"></div>
        </div>
        <div class="form-group expiration-date-group">
            <label for="expiration-date">卡片到期日</label>
            <div class="form-control expiration-date" id="acpay-expiration-date"></div>
        </div>
        <div class="form-group cvc-group">
            <label for="cvc">卡片後三碼</label>
            <div class="form-control cvc"></div>
        </div>
        <button type="submit" class="btn btn-primary">提交付款</button>
    </form>
    <br>
    <div id="result" class="jumbotron text-left"></div>

    <h3>交易記錄管理</h3>
    <button class="btn btn-info" onclick="fetchPayments()">取得所有交易記錄</button>
    <br><br>

    <div class="form-group">
        <label for="update-id">交易記錄 ID</label>
        <input type="number" class="form-control" id="update-id" placeholder="輸入交易記錄 ID">
    </div>
    <div class="form-group">
        <label for="update-email">更新 Email</label>
        <input type="email" class="form-control" id="update-email" placeholder="輸入新的 Email">
    </div>
    <button class="btn btn-warning" onclick="updatePayment()">更新交易記錄</button>
    <div class="form-group">
        <label for="delete-id">刪除交易記錄 ID</label>
        <input type="number" class="form-control" id="delete-id" placeholder="輸入交易記錄 ID">
    </div>
    <button class="btn btn-danger" onclick="deletePayment()">刪除交易記錄</button>
</div>

<script src="https://code.jquery.com/jquery-3.2.1.min.js"></script>
<script src="https://connectjs.payloop.com.tw/ACconnect/v1.0.3.js"></script>
<script>
    // 初始化信用卡 SDK
    ACconnect.setupSDK('090414780201003', '854b72ab-3828-4994-ab6c-16b5145937a8', 'sandbox');
    ACconnect.card.setup({
        fields: {
            number: { element: '.form-control.card-number', placeholder: '4444 3333 2222 1111' },
            expirationDate: { element: document.getElementById('acpay-expiration-date'), placeholder: '08 / 28' },
            ccv: { element: '.form-control.cvc', placeholder: '886' }
        }
    });

    const API_BASE_URL = "http://127.0.0.1:8000";

        // 創建交易記錄 (Create)
        $('#payment-form').on('submit', function (event) {
            event.preventDefault();
            ACconnect.card.getPrime(function (result) {
                if (result.status !== 0) {
                    alert('錯誤: ' + result.msg);
                    return;
                }
                const email = $('#email').val();
                fetch(`${API_BASE_URL}/checkout`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email: email, prime: result.card.prime })
                })
                .then(res => {
                    if (!res.ok) {
                        throw new Error('伺服器錯誤: ' + res.status);
                    }
                    return res.json();
                })
                .then(data => $('#result').text(data.message))
                .catch(err => console.error('發生錯誤:', err));

            });
        });

        // 取得所有交易記錄 (Read)
        function fetchPayments() {
            fetch(`${API_BASE_URL}/payments`)
                .then(response => response.json())
                .then(data => {
                    let output = '<h4>交易記錄：</h4><ul>';
                    data.forEach(payment => {
                        output += `<li>ID: ${payment.id}, Email: ${payment.email}, PRIME: ${payment.prime}, 時間: ${new Date(payment.created_at).toLocaleString()}</li>`;
                    });
                    output += '</ul>';
                    document.getElementById('result').innerHTML = output;
                })
                .catch(err => console.error('查詢失敗:', err));
        }

        // 更新交易記錄 (Update)
        function updatePayment() {
            const id = document.getElementById('update-id').value;
            const email = document.getElementById('update-email').value;
            fetch(`${API_BASE_URL}/payments/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: email })
            })
                .then(res => res.json())
                .then(data => {
                    document.getElementById('result').innerText = data.message;
                    fetchPayments(); // 重新取得交易記錄
                })
                .catch(err => console.error('更新失敗:', err));
        }

        // 刪除交易記錄 (Delete)
        function deletePayment() {
            const id = document.getElementById('delete-id').value;
            fetch(`${API_BASE_URL}/payments/${id}`, {
                method: 'DELETE'
            })
                .then(res => res.json())
                .then(data => {
                    document.getElementById('result').innerText = data.message;
                    fetchPayments(); // 重新取得交易記錄
                })
                .catch(err => console.error('刪除失敗:', err));
        }
</script>
</body>

</html>

```
資料庫與 JavaScript 版本所使用的一樣。

執行 FastAPI 和 Uvicorn
---
用終端機執行
```
uvicorn main:app --reload
```
正確執行的話，終端機會顯示
```
INFO:     Will watch for changes in these directories: ['C:\\Users\\willy\\OneDrive\\桌面\\prime_main\\acpay_backend_practice']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [5692] using WatchFiles
INFO:     Started server process [19952]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

想到的問題
---
1.如何用自定義 callback function 使用 Prime? 
: 可以利用 ACconnect.card.getPrime 方法，自行撰寫想要的 callback function。

2.如何避免重複付款的情況?
: 需要設計條件限制，例如在三十秒內無法用同一個信用卡付款、在使用者提交表單後立即禁用按鈕直到付款完成或失敗為止等條件。

3.Prime 的資訊需要存到服務端的資料庫嗎?
: 可存可不存，一般來說 Prime 資訊會存到支付服務供應商的資料庫，服務端不會使用 Prime 資訊，但如果服務端如果有特定需求，可以臨時儲存 Prime 資訊，但必須確保加密、定期刪除，並限制存取權限。

目前的進度(1/21 ~ 1/30)
---

![Python Backend Project Plan](https://hackmd.io/_uploads/H1s2gCHOJl.png)
