<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>カロリー計算</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>

    <div class="calculator-container">
        <h1>カロリー計算</h1>

        <div class="user-info">
            <div class="info-item">
                <label for="height">身長</label>
                <input type="number" id="height" name="height" placeholder="例: 170">
            </div>
            <div class="info-item">
                <label for="weight">体重</label>
                <input type="number" id="weight" name="weight" placeholder="例: 60">
            </div>
            <div>
                <div class="info-item">
                    <label for="age">年齢</label>
                    <input type="number" id="age" name="age" placeholder="例: 20">
            </div>
            <div class="info-item">
                <label for="gender">性別</label>
                <select id="gender" name="gender">
                    <option value="male">男性</option>
                    <option value="female">女性</option>
                </select>
            </div>
        </div>

        <div class="meals-grid">
            
            <div class="meal-item">
                <label for="meal1">食事1</label>
                <select id="meal1" name="meal1"></select>
            </div>
            <div class="meal-item">
                <label for="meal2">食事2</label>
                <select id="meal2" name="meal2"></select>
            </div>
            <div class="meal-item">
                <label for="meal3">食事3</label>
                <select id="meal3" name="meal3"></select>
            </div>
            <div class="meal-item">
                <label for="meal4">食事4</label>
                <select id="meal4" name="meal4"></select>
            </div>
            <div class="meal-item">
                <label for="meal5">食事5</label>
                <select id="meal5" name="meal5"></select>
            </div>
            <div class="meal-item">
                <label for="meal6">食事6</label>
                <select id="meal6" name="meal6"></select>
            </div>
        </div>
        <button id="calculateBtn" type="button">計算する</button>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const genderMap = {
                "male": 1,
                "female": 2,
            };
            
            // 1. 食事の選択肢リストを定義
            const foodOptionsList = [
                { value: "none", text: "--- 選択してください ---" },
                { value: "辛みそ豚丼（小）", text: "辛みそ豚丼（小）" },
                { value: "辛みそ豚丼（中）", text: "辛みそ豚丼（中）" },
                { value: "辛みそ豚丼（大）", text: "辛みそ豚丼（大）" },
                { value: "ねぎとろ丼", text: "ねぎとろ丼" },
                { value: "ほっき貝カレー（小）", text: "ほっき貝カレー（小）" },
                { value: "ほっき貝カレー（中）", text: "ほっき貝カレー（中）" },
                { value: "ほっき貝カレー（大）", text: "ほっき貝カレー（大）" },
                { value: "カレーライス（小）", text: "カレーライス（小）" },
                { value: "カレーライス（中）", text: "カレーライス（中）" },
                { value: "カレーライス（大）", text: "カレーライス（大）" },
                { value: "さっぽろ味噌ラーメン", text: "さっぽろ味噌ラーメン" },
                { value: "さっぽろ味噌ラーメン（大）", text: "さっぽろ味噌ラーメン（大）" },
                { value: "醤油ラーメン", text: "醤油ラーメン" },
                { value: "醤油ラーメン（大）", text: "醤油ラーメン（大）" },
                { value: "かけうどん", text: "かけうどん" },
                { value: "かけうどん（大）", text: "かけうどん（大）" },
                { value: "かけそば", text: "かけそば" },
                { value: "かけそば（大）", text: "かけそば（大）" },
                { value: "かき揚げうどん", text: "かき揚げうどん" },
                { value: "かき揚げうどん（大）", text: "かき揚げうどん（大）" },
                { value: "かき揚げそば", text: "かき揚げそば" },
                { value: "かき揚げそば（大）", text: "かき揚げそば（大）" },
                { value: "肉野菜炒めプレート（中）", text: "肉野菜炒めプレート（中）" },
                { value: "肉野菜炒めプレート（小）", text: "肉野菜炒めプレート（小）" },
                { value: "肉野菜炒めプレート（大）", text: "肉野菜炒めプレート（大）" },
                { value: "ホッケ塩焼き", text: "ホッケ塩焼き" },
                { value: "揚げ鶏の香味ソース", text: "揚げ鶏の香味ソース" },
                { value: "桜姫鶏デミチーズメンチ", text: "桜姫鶏デミチーズメンチ" },
                { value: "ポーク生姜焼き", text: "ポーク生姜焼き" },
                { value: "ねぎ塩ハンバーグ", text: "ねぎ塩ハンバーグ" },
                { value: "ジャンボたらカツ", text: "ジャンボたらカツ" },
                { value: "さば味噌煮", text: "さば味噌煮" },
                { value: "辛旨豆腐", text: "辛旨豆腐" },
                { value: "かぼちゃとチーズの包み揚げ", text: "かぼちゃとチーズの包み揚げ" },
                { value: "明太子スパゲティサラダ", text: "明太子スパゲティサラダ" },
                { value: "揚げ餃子", text: "揚げ餃子" },
                { value: "薩摩ハーブ鶏のレバー煮", text: "薩摩ハーブ鶏のレバー煮" },
                { value: "オクラのお浸し", text: "オクラのお浸し" },
                { value: "野菜生活１００", text: "野菜生活１００" },
                { value: "温泉たまご", text: "温泉たまご" },
                { value: "ひじき煮", text: "ひじき煮" },
                { value: "煮卵", text: "煮卵" },
                { value: "ごろっと野菜のツナマヨサラダ", text: "ごろっと野菜のツナマヨサラダ" },
                { value: "ポテト＆コーンサラダ", text: "ポテト＆コーンサラダ" },
                { value: "ライス１３０ｇ（小）", text: "ライス１３０ｇ（小）" },
                { value: "ライス２００ｇ（中）", text: "ライス２００ｇ（中）" },
                { value: "ライス２７０ｇ（大）", text: "ライス２７０ｇ（大）" },
                { value: "麦ご飯１３０ｇ（小）", text: "麦ご飯１３０ｇ（小）" },
                { value: "麦ご飯２００ｇ（中）", text: "麦ご飯２００ｇ（中）" },
                { value: "麦ご飯２７０ｇ（大）", text: "麦ご飯２７０ｇ（大）" },
                { value: "味噌汁（豆腐・わかめ）", text: "味噌汁（豆腐・わかめ）" },
                { value: "豚汁", text: "豚汁" },
                { value: "フルーツミックスヨーグルト", text: "フルーツミックスヨーグルト" },
                { value: "ショコラケーキ", text: "ショコラケーキ" },
                { value: "モンブラン", text: "モンブラン" },
                { value: "抹茶きなこケーキ", text: "抹茶きなこケーキ" },
                { value: "十勝大福", text: "十勝大福" }
            ];

            // 2. リストから <option> タグのHTMLを生成
            let optionsHTML = '';
            foodOptionsList.forEach(function(food) {
                optionsHTML += `<option value="${food.value}">${food.text}</option>`;
            });
            const mealSelects = document.querySelectorAll('.meals-grid select');
            mealSelects.forEach(select => {
                select.innerHTML = optionsHTML;
            });
            // ボタン要素を取得
            const calculateButton = document.getElementById('calculateBtn');

            // ボタンがクリックされたときの処理を登録
            calculateButton.addEventListener('click', function() {
                
                // 1. 身長・体重・年齢・性別の値を取得
                const height = parseFloat(getElementById('height').value);
                const weight = parseFloat(getElementById('weight').value);
                const age = parseFloat(getElementById('age').value);
                const gender = document.getElementById('gender').value;
                // 数値に変換
                const genderNum = genderMap[gender];

                // 2. 食事1〜6の値を取得 (個別に取得する場合)
                const meal1 = document.getElementById('meal1').value;
                const meal2 = document.getElementById('meal2').value;
                const meal3 = document.getElementById('meal3').value;
                const meal4 = document.getElementById('meal4').value;
                const meal5 = document.getElementById('meal5').value;
                const meal6 = document.getElementById('meal6').value;

                const requestData = {
                    // ユーザー情報
                    userInfo: {
                        height: height,
                        weight: weight,
                        age: age,
                        gender: genderNum
                    },
                    // 食事情報
                    meals: {
                        meal1,
                        meal2,
                        meal3,
                        meal4,
                        meal5,
                        meal6
                    }
                };
                // 3. [JS → Python] "rice" というキーをPythonサーバーに送信
                 fetch('http://127.0.0.1:5000/get_nutrition', { // PythonサーバーのURL
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(requestData) // { "food_key": "rice" } を送信
                 })
                // 取得した値をコンソールに出力して確認
                console.log('--- ユーザー情報 ---');
                console.log('身長:', height);
                console.log('体重:', weight);
                console.log('年齢:', age);
                console.log('性別:', gender);
                
                console.log('--- 食事情報 ---');
                console.log('食事1:', meal1);
                console.log('食事2:', meal2);
                console.log('食事3:', meal3);
                console.log('食事4:', meal4);
                console.log('食事5:', meal5);
                console.log('食事6:', meal6);
                
                // (参考: 配列の場合)
                // console.log('食事(配列):', mealValues);
            });
        });
        
    </script>


</body>
</html>

