// -------------------------------
// Exercise Creation
// -------------------------------

// ---- Initialization -----

var exercise = new Exercise();
var modalStep1 = new Modal('exerciseModalStep1');
var modalStep2 = new ModalBuilder('exerciseModalStep2');

// ---- Step 1 -----

modalStep1.form.addEventListener("submit", function(e) {
    // Remove form component
    modalStep2.cleanFormElt();

    // Get First Exercise Elements from Step 1
    exercise.name = modalStep1.getFormTextInput("id_name");
    exercise.exerciseType = modalStep1.getFormSelectInput("id_exercise_type");
    exercise.description = modalStep1.getFormTextInput("id_description");
    exercise.goalType = exercise.defineGoalType(exercise.exerciseType);

    // Build Modal for Step2 according first exercise elements
    modalStep2.changeTitle(exercise.name);
    modalStep2.addFormSection("Type: " + exercise.exerciseType);
    if (exercise.exerciseType != "RUNNING") {
        modalStep2.addFormTextInput("modalStep2Goal", exercise.goalType, "number", false);
        
        // We get all the movements and when we have them, we generate the movement blocks + end of the form
        getAjaxJson("/app/get-all-movements/", "GET")
        .then(function (response) {
            modalStep2.addMovementBlock(response);
            modalStep2.addSplittedLine();
            modalStep2.addSubmitButton("CREER");
        })
        .catch(function (error) {
            console.log(error.status);
            console.log(error.statusText);
        })
    } else {
        // This is to manage the exercise it if is running type
            // No need movement block
            // Need decimal in performance value
        modalStep2.addFormTextInput("modalStep2Goal", exercise.goalType, "number", true);
        modalStep2.addSplittedLine();
        modalStep2.addSubmitButton("Créer");
    }

    // Hide Modal for Step1 and show Modal for Step 2 
    modalStep1.pushOptions('hide');
    modalStep2.pushOptions('show');
    e.preventDefault();
});

// ---- Step 2 -----

modalStep2.form.addEventListener("submit", function(e) {
    e.preventDefault();
    // We get all informations from the form
    exercise.goalValue = Number(modalStep2.getFormTextInput("modalStep2Goal"));
    var movements = modalStep2.getSelectInputs();
    for (i = 0; i < movements.length; i++) {
        var mvtNumber = i + 1;
        var name = modalStep2.getFormSelectInput("select" + mvtNumber);
        var movement = new Movement(name, mvtNumber);
        // We need to get Settings
        var settingsDiv = document.getElementById("settings" + mvtNumber);
        var settingsInputElt = settingsDiv.getElementsByTagName("INPUT");
        for (x = 0; x < settingsInputElt.length; x++) {
            let name = settingsInputElt[x].name;
            let value = settingsInputElt[x].value;
            let setting = new Setting(name, value);
            movement.settings.push(setting);
        }
        exercise.movements.push(movement);
    }
    // We post exercise object
    postAjaxJson("/app/add-exercise/", exercise, true, function(response) {
        window.location.href = "/app/exercise/" + response + "/";
    });
    modalStep2.pushOptions('hide');
});
