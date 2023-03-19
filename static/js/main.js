$(function() {
    $('#datatable').DataTable({
        "lengthMenu": [ 5, 10, 25, 50 ],
        "order": [ 0, 'asc' ]
    });
});

function updateSortable (event, ui) {
    const csrftoken = Cookies.get('csrftoken');
    const data = $(this).sortable('serialize', {
        expression: /(.+)_(.+)/
    });
    $.ajax({
        data: data,
        headers: {'X-CSRFToken' : csrftoken},
        type: 'POST',
        mode: 'same-origin',
        url: '/echo/'
    });
}

$(function() {
    $(".sortable-col").sortable({
        connectWith: ".sortable-col",
        update: updateSortable
    });
});

$(function() {
    $(".sortable-item").sortable({
        connectWith: ".sortable-item",
        update: updateSortable
    });
});