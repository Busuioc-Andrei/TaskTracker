$(document).ready(function() {
    $('#datatable').DataTable({
        "lengthMenu": [ 5, 10, 25, 50 ],
        "order": [ 0, 'asc' ]
    });
} );