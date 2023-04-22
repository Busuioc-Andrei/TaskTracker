function updateSortable (event, ui){
    const csrftoken = Cookies.get('csrftoken');
    let item = ui.item;
    let newColumn, movedIssue;
    if (ui.sender != null) {
        movedIssue = item.attr('id');
        newColumn = item.parentsUntil('.sortable-col', '.sorted-column').attr('id');
    }
    const data = $(this).sortable('serialize', {
        expression: /(.+)_(.+)/
    });
    $.ajax({
        data: JSON.stringify({'data': data, 'movedIssue': movedIssue,'newColumn': newColumn}),
        dataType: "json",
        contentType: "application/json",
        headers: {'X-CSRFToken': csrftoken},
        type: 'POST',
        mode: 'same-origin',
        url: '/persistent/'
    });
}

$(function () {
    $(".sortable-col").sortable({
        connectWith: ".sortable-col",
        update: updateSortable,
        cancel: '.exclude'
    });
});

$(function () {
    $(".sortable-item").sortable({
        connectWith: ".sortable-item",
        update: updateSortable
    });
});
