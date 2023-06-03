$(document).ready(function () {
    $(".draggable-row").draggable({
        helper: function () {
            const draggedRow = $(this);
            let customHelper = draggedRow.find(".issue-name").clone();
            customHelper.css({
                backgroundColor: "#f0f0f0",
                border: "1px solid #ccc",
                padding: "10px 15px",
                borderRadius: "4px",
                fontSize: "14px",
                color: "#333"
            });
            customHelper.data("issue-id", draggedRow.data("issue-id"));
            return customHelper;
        },
        cursor: "move",
        opacity: 1,
        revert: "invalid",
        zIndex: 100,
        appendTo: "body",
        containment: "window",
        cursorAt: {top: 30, left: 5}
    });

    $(".card.hover-effect").droppable({
        over: function (event, ui) {
            $(this).addClass("hovered");
        },
        out: function (event, ui) {
            $(this).removeClass("hovered");
        },
        drop: function (event, ui) {
            var droppedRow = ui.draggable;
            droppedRow.hide();
            var boardId = $(this).data("board-id");

            const csrftoken = Cookies.get('csrftoken');

            $.ajax({
                url: "/move-issue-to-board/",
                type: "POST",
                data: {
                    issueId: droppedRow.data("issue-id"),
                    boardId: boardId
                },
                headers: {'X-CSRFToken': csrftoken},
                success: function (response) {
                    console.log("Column ID updated successfully");
                },
                error: function (xhr, status, error) {
                    console.error("Error updating column ID:", error);
                }
            });
        }
    });
});
