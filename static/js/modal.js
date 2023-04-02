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
