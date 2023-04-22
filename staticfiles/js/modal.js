function addFormURLtoClass(className, modalID) {
    let buttons = document.getElementsByClassName(className);
    for (let index = 0; index < buttons.length; index++) {
        modalForm(buttons[index], {
            formURL: buttons[index]["dataset"]["formUrl"],
            modalID: modalID
        });
    }
}

function addFormURLtoClassAsync(className, modalID) {
    let buttons = document.getElementsByClassName(className);
    for (let index = 0; index < buttons.length; index++) {
        modalForm(buttons[index], {
            formURL: buttons[index]["dataset"]["formUrl"],
            modalID: modalID,
            asyncUpdate: true,
            asyncSettings: {
                closeOnSubmit: false,
                successMessage: "<div></div>",
                dataUrl: "/empty/",
                dataElementId: "placeholder",
                dataKey: "placeholder",
                addModalFormFunction: addFormURLtoClassAsync
            }
        });
    }
}

$(function () {
    addFormURLtoClass("modal-link-m", "#modal-m");
    addFormURLtoClassAsync("modal-link-xl-async", "#modal-xl");
});

$(function () {
    const targetNodes = document.getElementsByClassName("modal-content");
    for (let targetNode of targetNodes){
        const callback = (mutationList, observer) => {
            for (const mutation of mutationList) {
                if (mutation.type === "childList" && mutation.addedNodes.length > 0) {

                    const arr = document.querySelectorAll('.modal script');
                    for (let n = 0; n < arr.length; n++)
                        eval(arr[n].innerHTML)

                    addFormURLtoClass("modal-link-m", "#modal-m");
                }
            }
        };
        const observer = new MutationObserver(callback);
        observer.observe(targetNode, {childList: true});
    }
});

function setSubmitButtonName(button) {
    $('<input>').attr({
        type: 'hidden',
        name: button.name
    }).appendTo(button.form)
}