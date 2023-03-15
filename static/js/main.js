$(document).ready(function() {
    $('#datatable').DataTable({
        "lengthMenu": [ 5, 10, 25, 50 ],
        "order": [ 0, 'asc' ]
    });
});

$(document).ready(function(){
    $(".sortable").sortable({
        update: function (event, ui) {
            const csrftoken = Cookies.get('csrftoken');
            const data = $(this).sortable('serialize', { key: "sort" });
            $.ajax({
                data: data,
                headers: {'X-CSRFToken' : csrftoken},
                type: 'POST',
                mode: 'same-origin',
                url: '/echo/'
            });
        }
    });
});
