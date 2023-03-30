$(function () {
    $('#datatable').DataTable({
        "lengthMenu": [5, 10, 25, 50],
        "order": [0, 'asc']
    });
});

function updateSortable(event, ui) {
    const csrftoken = Cookies.get('csrftoken');
    const data = $(this).sortable('serialize', {
        expression: /(.+)_(.+)/
    });
    $.ajax({
        data: data,
        headers: {'X-CSRFToken': csrftoken},
        type: 'POST',
        mode: 'same-origin',
        url: '/echo/'
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

// $(function() {
//     $(".save-column").click(function(e) {
//         e.preventDefault();
//         const csrftoken = Cookies.get('csrftoken');
//         $.ajax({
//             data: $("#save-column-form").serialize(),
//             headers: {'X-CSRFToken' : csrftoken},
//             type: 'POST',
//             mode: 'same-origin',
//             url: '/echo/'
//         });
//     });
// });

// var intervalId = window.setInterval(function () {
//         $("input[name='start_date").datetimepicker({
//             format: 'd/m/Y H:i',
//         });
//     }
//     , 5000);

function addFormURLtoClass(className) {
    let buttons = document.getElementsByClassName(className);
    for (let index = 0; index < buttons.length; index++) {
        modalForm(buttons[index], {
            formURL: buttons[index]["dataset"]["formUrl"]
        });
    }
}

$(function () {
    addFormURLtoClass("column-issue-add");
    addFormURLtoClass("model-delete");
});

$(function () {
    const targetNode = document.getElementsByClassName("modal-content")[0];
    if (targetNode){
        const callback = (mutationList, observer) => {
            for (const mutation of mutationList) {
                if (mutation.type === "childList" && mutation.addedNodes.length > 0) {
                    const arr = document.querySelectorAll('.modal script');
                    for (let n = 0; n < arr.length; n++)
                        eval(arr[n].innerHTML)
                }
            }
        };
        const observer = new MutationObserver(callback);
        observer.observe(targetNode, {childList: true});
    }
});