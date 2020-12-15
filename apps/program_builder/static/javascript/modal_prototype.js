// ---------------------------------------------------------------
// Modal Prototypes
// ---------------------------------------------------------------

// ---- Modal Parent -> Modal ----

function Modal(id) {
    this.id = id;
    this.modal = document.getElementById(this.id);
    this.title = document.getElementById(this.id + "Label");
    this.form = document.getElementById(this.id + "Form");
};


Modal.prototype.getFormTextInput = function(inputId) {
    // Get value from textinputform
    return document.getElementById(inputId).value;
};

Modal.prototype.getFormSelectInput = function(selectId) {
    // Get option selected from select form
    return document.getElementById(selectId).value;
};

Modal.prototype.getSelectInputs = function() {
    // Return all the selects from a modal
    return this.form.getElementsByTagName("SELECT");
};

Modal.prototype.getFormCheckboxClicked = function(inputName) {
    // Get checkbox clicked from form
    clickedCheckboxesValues = []
    var checkboxes = document.getElementsByName(inputName);
    for (i = 0; i < checkboxes.length; i++) {
        if (checkboxes[i].checked) {
            clickedCheckboxesValues.push(checkboxes[i].value);
        }
    }
    return clickedCheckboxesValues;
};

Modal.prototype.pushOptions = function(option) {
    // Manage modal option through bootstrap JQuery function
    $('#' + this.id).modal(option);
};


Modal.prototype.changeTitle = function(title) {
    // Change the title of the modal
    this.title.textContent = title;
};

// ---- Modal Child with block builder -> ModalBuilder ----

function ModalBuilder(id) {
    Modal.call(this, id);
};
ModalBuilder.prototype = Object.create(Modal.prototype);
ModalBuilder.prototype.constructor = ModalBuilder;

ModalBuilder.prototype.cleanFormElt = function() {
    // This is a method to remove all child elements from a form
    // EXCEPT the csrf token
    if (this.form.hasChildNodes()) {
        var formElts = this.form.childNodes;
        // We just need to keep csrf token
        for (i = 0; i < formElts.length; i++) {
            if (formElts[i].nodeType !== Node.ELEMENT_NODE) {
                this.form.removeChild(formElts[i]);
                i--;
            } else {
                if (formElts[i].hasAttribute("name") && formElts[i].name === "csrfmiddlewaretoken") {
                    //pass
                } else {
                    this.form.removeChild(formElts[i]);
                    i--;
                }
            }
        }
    }
}

ModalBuilder.prototype.addSplittedLine = function() {
    var hrElt = document.createElement('hr');
    this.form.appendChild(hrElt);
}

ModalBuilder.prototype.addFormSection = function(sectionName) {
    var sectionElt = document.createElement('h6');
    sectionElt.textContent = sectionName;
    this.form.appendChild(sectionElt);
};

ModalBuilder.prototype.returnSplittedLine = function() {
    var hrElt = document.createElement('hr');
    return hrElt
}

ModalBuilder.prototype.returnFormSection = function(sectionName) {
    var sectionElt = document.createElement('h6');
    sectionElt.textContent = sectionName;
    return sectionElt;
};

ModalBuilder.prototype.addFormTextInput = function(id, labelName, type, is_decimal) {
    var divElt = document.createElement("div");
    divElt.classList.add("form-group");

    var labelElt = document.createElement("label");
    labelElt.setAttribute("for", id);
    labelElt.textContent = labelName;

    var inputElt = document.createElement("input");
    inputElt.id = id;
    inputElt.setAttribute("required", "true");
    inputElt.classList.add("form-control");
    inputElt.setAttribute("type", type);
    inputElt.setAttribute("min", "0");
    if (type === "number" && is_decimal) {
        inputElt.setAttribute("step", "0.1");
    }

    divElt.appendChild(labelElt);
    divElt.appendChild(inputElt);
    this.form.appendChild(divElt);
};

ModalBuilder.prototype.addMovementBlock = function(movementsList) {
    // This is the method to build a movement block in a modal
    // In this method, ModalBuilder.prototype.returnMovementForm is used

    var startHrElt = this.returnSplittedLine();
    this.form.appendChild(startHrElt);
    
    var sectionElt = this.returnFormSection("Mouvements");
    this.form.appendChild(sectionElt);
    
    var endHrElt = this.returnSplittedLine();
    this.form.appendChild(endHrElt);

    var buttonElt = document.createElement('button');
    buttonElt.setAttribute("type", "button");
    buttonElt.classList.add("btn", "btn-sm", "btn-outline-info");
    buttonElt.textContent = "+ Mouvement";

    // mvtFormIndex used to set-up id in selected form + order
    var mvtFormIndex = 1;
    var mvtForm = this.returnMovementForm(movementsList, mvtFormIndex);
    this.form.insertBefore(mvtForm, endHrElt);

    this.form.appendChild(buttonElt);


    // Working on different buttons event

    buttonElt.addEventListener("click", function() {
        mvtFormIndex = mvtFormIndex + 1;
        var mvtForm = this.returnMovementForm(movementsList, mvtFormIndex);
        this.form.insertBefore(mvtForm, endHrElt);
    }.bind(this));
};

ModalBuilder.prototype.returnMovementForm = function(movementsList, mvtFormIndex) {
    // This is the method to return a movement div selection with its settings
    // in a movement block
    // In this method, ModalBuilder.prototype.returnSettingsMovementForm is used
    // to manage settings selection.
    // This method can be considered as a private method. It is only used in
    // ModalBuilder.prototype.addMovementBlock method

    var formElt = document.createElement("div");
    formElt.classList.add("form-group","row", "mb-2", "d-flex", "justify-content-end", "align-items-center");

    var labelElt = document.createElement("label");
    labelElt.setAttribute("for", "select" + mvtFormIndex);
    labelElt.textContent = mvtFormIndex + ". ";
    labelElt.classList.add("col-1", "col-form-label", "text-right");

    var divSelectElt = document.createElement("div");
    divSelectElt.classList.add("col-9");

    var selectElt = document.createElement("select");
    selectElt.classList.add("form-control");
    selectElt.id = "select" + mvtFormIndex;
    selectElt.setAttribute("name", "select" + mvtFormIndex)

    optionDefaultElt = document.createElement("option");
    optionDefaultElt.value = "none";
    optionDefaultElt.textContent = "Sélectionnez un mouvement";
    selectElt.appendChild(optionDefaultElt);

    for (var i = 0; i < movementsList.length; i++) {
        var optionElt = document.createElement("option");
        optionElt.setAttribute("value", movementsList[i].id);
        optionElt.textContent = movementsList[i].name;
        optionElt.value = movementsList[i].name;
        selectElt.appendChild(optionElt);
    }

    divSelectElt.appendChild(selectElt);


    // FOR FIRST MVP -> WE DON'T MANAGE DEL MOVEMENT DURING CREATION
    // if (mvtFormIndex > 1) {
    //     // Test close Button
    //     var delBtnElt = document.createElement("button");
    //     delBtnElt.id = "close-button-" + mvtFormIndex;
    //     delBtnElt.classList.add("close", 'col-2');
    //     delBtnElt.setAttribute("type", "button");
    //     delBtnElt.setAttribute("arial-label", "Close");

    //     var delSpanElt = document.createElement("span");
    //     delSpanElt.setAttribute("aria-hidden", "true");
    //     delSpanElt.textContent = "×";

    //     delBtnElt.appendChild(delSpanElt);
    //     formElt.appendChild(delBtnElt);
    // }
    
    formElt.appendChild(labelElt);
    formElt.appendChild(divSelectElt);
    
    
    //addEventListener change on selectElt element
    selectElt.addEventListener("change", function() {
        // We get the value of the selected option
        var mvtName = selectElt[selectElt.selectedIndex].value;
        // With nvtName, we get the adeaquate movement in movementsList
        var mvtSelected = {};
        if (mvtName != "none") {
            var i = 0
            var mvtNumb = movementsList.length;
            var notFound = true;
            while (i < mvtNumb && notFound) {
                if (mvtName != movementsList[i].name) {
                    i++;
                } else {
                    mvtSelected = movementsList[i];
                    notFound = false;
                }
            }
        }
        // We need to remove a previous settings block before pushing another one
        // These blocks have the id equal to "Settings" + mvtFormIndex : see returnMovementForm method
        var settingElt = document.getElementById("settings" + mvtFormIndex); 
        if (settingElt != null) {
            settingElt.parentNode.removeChild(settingElt);
        }
        // For each setting linked to the movement, we create an text input with a number type
        mvtSettingsForm = this.returnSettingsMovementForm(mvtSelected, mvtFormIndex);
        formElt.appendChild(mvtSettingsForm);

    }.bind(this));

    return formElt;
};

ModalBuilder.prototype.returnSettingsMovementForm = function (movementSelected, mvtFormIndex) {
    // This is the method to return settings movement forms in a movement div.
    // This method can be considered as a private method. It is only used in
    // ModalBuilder.prototype.returnMovementForm method

    var allSettingsElt = document.createElement("div")
    allSettingsElt.id = "settings" + mvtFormIndex;
    allSettingsElt.classList.add("mt-2");
    
    for (i=0; i < movementSelected.settings.length; i++) {
        var formElt = document.createElement("div");
        formElt.classList.add("form-group", "d-flex", "justify-content-end");
    
        var labelElt = document.createElement("label");
        labelElt.setAttribute("for", movementSelected.settings[i] + mvtFormIndex);
        labelElt.classList.add("col-4", "col-form-label", "text-right");
        labelElt.textContent = movementSelected.settings[i];

        var divInputElt = document.createElement("div");
        divInputElt.classList.add("col-4");

        var inputElt = document.createElement("input");
        inputElt.id = movementSelected.settings[i] + mvtFormIndex;
        inputElt.setAttribute("type", "number");
        inputElt.setAttribute("min", "0");
        inputElt.setAttribute("required", "true");
        inputElt.setAttribute("name", movementSelected.settings[i]);
        inputElt.classList.add("form-control", "form-control-sm");

        divInputElt.appendChild(inputElt);
        formElt.appendChild(labelElt);
        formElt.appendChild(divInputElt);
        allSettingsElt.appendChild(formElt);
    }
    return allSettingsElt;
}

ModalBuilder.prototype.addSubmitButton = function(buttonText) {
    // This is a method to generate a submit button in a modal

    var buttonElt = document.createElement("button");
    buttonElt.setAttribute("type", "submit");
    buttonElt.classList.add("btn", "btn-block" ,"btn-secondary", "text-light", "font-weight-bold");
    buttonElt.textContent = buttonText;

    this.form.appendChild(buttonElt);
};