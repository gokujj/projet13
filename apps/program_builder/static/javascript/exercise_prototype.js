// ---------------------------------------------------------------
// Exercise Prototype
// ---------------------------------------------------------------

function Exercise() {
    this.id = Number();
    this.name = String();
    this.exerciseType = String();
    this.description = String();
    this.founder = String();
    this.goalType = String();
    this.goalValue = Number();
    this.movements = Array();
};

Exercise.prototype.defineGoalType = function(exerciseType) {
    // To define performanceType according exerciseType only for 
    // Modal Label
    // A treatment id done on backend from exercise type value
    goalType = String();

    if (exerciseType === 'RUNNING') {
        goalType = 'Distance';
    } else if (exerciseType === 'AMRAP' || exerciseType === 'EMOM') {
        goalType = 'Duree';
    } else {
        goalType = 'Nombre de rounds';
    }
    return goalType;
};

// ---------------------------------------------------------------
// Movement Prototype
// ---------------------------------------------------------------

function Movement(name, order) {
    this.name = name;
    this.order = order;
    this.settings = Array();
};

function Setting(name, value) {
    this.name = name;
    this.value = value;
}

