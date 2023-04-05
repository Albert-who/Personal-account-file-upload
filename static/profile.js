function deleteRow(rowId) {
    // AJAX запрос для удаления строки из базы данных
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/delete_row");
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.onreadystatechange = function() {
        if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
            // если запрос успешно выполнен, удаляем строку из таблицы
            var row = document.getElementById(rowId);
            row.parentNode.removeChild(row);
        }
    }
    xhr.send(JSON.stringify({"row_id": rowId}));
}