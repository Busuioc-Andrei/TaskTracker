$(document).ready(function () {
    // Enable dragging for rows with the class "draggable-row"
    $(".draggable-row").draggable({
        helper: function () {
            // Create a custom helper element to replace the dragged item
            var draggedRow = $(this);
            var customHelper = draggedRow.find(".issue-name").clone();
            customHelper.css({
                backgroundColor: "#f0f0f0",
                border: "1px solid #ccc",
                padding: "10px 15px",
                borderRadius: "4px",
                fontSize: "14px",
                color: "#333",
            });

            // Attach any necessary data or attributes from the dragged row to the custom helper
            customHelper.data("issue-id", draggedRow.data("issue-id")); // Example: Copy issue ID

            return customHelper; // Return the custom helper element
        },
        cursor: "move",
        opacity: 1,
        revert: "invalid", // Revert back if not dropped on a valid target
        zIndex: 100, // Increase the z-index to ensure the dragged element appears on top
        appendTo: "body", // Append the helper element to the body element
        containment: "window", // Keep the helper element within the window boundaries
        cursorAt: {top: 30, left: 5},
    });

    // Enable dropping for board cards
    $(".card.hover-effect").droppable({
        over: function (event, ui) {
            // Access the dragged row using "ui.draggable"
            var draggedRow = ui.draggable;

            // Apply the hover effect only when the dragged row is directly over the board card
            // if ($(this).is(":hover")) {
            $(this).addClass("hovered");
            // }
        },
        out: function (event, ui) {
            // Remove the hover effect from the board card when the dragged row moves out
            $(this).removeClass("hovered");
        },
        drop: function (event, ui) {
            // Access the dropped row using "ui.draggable"
            var droppedRow = ui.draggable;

            // Log a message when the row is dropped on the board card
            console.log("Dropped row:", droppedRow);

            // Hide the dropped row
            droppedRow.hide();

            // Retrieve the board ID from the card's data attribute or other suitable method
            var boardId = $(this).data("board-id");
            console.log("BoardId:", boardId);

            const csrftoken = Cookies.get('csrftoken');

            $.ajax({
                url: "/move-issue-to-board/", // Update the URL with the appropriate endpoint
                type: "POST",
                data: {
                    issueId: droppedRow.data("issue-id"), // Example: Pass the ID of the dropped issue
                    boardId: boardId, // Pass the ID of the board
                },
                headers: {'X-CSRFToken': csrftoken},
                success: function (response) {
                    // Handle success response
                    console.log("Column ID updated successfully");
                    // You can perform any additional actions or updates here
                },
                error: function (xhr, status, error) {
                    // Handle error
                    console.error("Error updating column ID:", error);
                },
            });
        },
    });
});
