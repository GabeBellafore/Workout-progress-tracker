"""FitTrack: A workout tracker that records workouts and tracks progress."""
from drafter import *
from dataclasses import dataclass
from datetime import date, timedelta
import matplotlib.pyplot as plt

@dataclass
class Workout:
    """Stores one workout."""
    date: str
    exercise: str
    sets: int
    reps: int
    weight: float

@dataclass
class State:
    """Stores the app's data."""
    workouts: list[Workout]
    selected_exercise: str
    exercise_filter: str
    message: str
    goal_exercise: str
    goal_weight: float
    weekly_goal: int
    show_all: bool

set_website_title("FitTrack - Workout Progress Analyzer")
set_site_information(
    author="Gabe Bellafore",
    description="FitTrack tracks workouts, personal records, and fitness goals.",
    sources="Python and Drafter documentation.",
    planning="See the FitTrack planning document in the repository.",
    links=["https://github.com/GabeBellafore/Workout-tracker"])

def navigation() -> list:
    """Creates the navigation buttons."""
    return [
        Button("Dashboard", "index"),
        Button("Log Workout", "log_workout"),
        Button("Progress", "progress"),
        Button("History", "history"),
        Button("Goals", "goals")
    ]

def get_exercises(state: State) -> list:
    """Returns all unique exercises."""
    exercises = []
    for workout in state.workouts:
        if workout.exercise not in exercises:
            exercises.append(workout.exercise)
    return exercises

def get_personal_record(state: State, exercise: str) -> float:
    """Finds the highest weight for an exercise."""
    highest_weight = 0.0
    for workout in state.workouts:
        if workout.exercise.lower() == exercise.lower():
            if workout.weight > highest_weight:
                highest_weight = workout.weight
    return highest_weight

def calculate_total_volume(state: State) -> float:
    """Calculates the total weight lifted."""
    total = 0.0
    for workout in state.workouts:
        total += workout.sets * workout.reps * workout.weight
    return total

def count_weekly_workouts(state: State) -> int:
    """Counts workouts from the last seven days."""
    today = date.today()
    first_day = today - timedelta(days=6)
    count = 0
    for workout in state.workouts:
        try:
            workout_date = date.fromisoformat(workout.date)
            if first_day <= workout_date <= today:
                count += 1
        except ValueError:
            pass
    return count

def valid_date(workout_date: str) -> bool:
    """Checks whether a date is valid."""
    try:
        date.fromisoformat(workout_date)
        return True
    except ValueError:
        return False

def filtered_workouts(state: State) -> list:
    """Returns workouts that match the filter."""
    results = []
    for workout in state.workouts:
        if state.show_all:
            results.append(workout)
        elif state.exercise_filter == "All Exercises":
            results.append(workout)
        elif workout.exercise == state.exercise_filter:
            results.append(workout)
    return results

@route
def index(state: State) -> Page:
    """Displays the dashboard."""
    total_workouts = len(state.workouts)
    total_volume = calculate_total_volume(state)
    weekly_workouts = count_weekly_workouts(state)
    exercises = get_exercises(state)
    content = [
        Header("FITTRACK"),
        "WORKOUT PROGRESS ANALYZER",
        Header("Dashboard"),
        "Welcome to FitTrack!",
        "Track your strength, monitor your progress, and reach your fitness goals.",
        Header("Your Statistics"),
        "Total Workouts: " + str(total_workouts),
        "Total Weight Lifted: " + format(total_volume, ".1f") + " lbs",
        "Workouts This Week: " + str(weekly_workouts)
    ]
    if total_workouts == 0:
        content.append("You haven't recorded any workouts yet. Log your first workout to get started!")
    else:
        content.append(Header("Personal Records"))
        for exercise in exercises:
            record = get_personal_record(state, exercise)
            content.append(exercise + ": " + str(record) + " lbs")
    content.append(Header("Navigation"))
    content.extend(navigation())
    return Page(state, content)

@route
def log_workout(state: State) -> Page:
    """Displays the workout form."""
    return Page(state, [
        Header("Log a Workout"),
        "Enter your exercise information below.",
        "Exercise Name:",
        TextBox("exercise", "Bench Press"),
        "Workout Date (YYYY-MM-DD):",
        TextBox("workout_date", date.today().isoformat()),
        "Number of Sets:",
        TextBox("sets", 3, kind="number"),
        "Number of Reps:",
        TextBox("reps", 10, kind="number"),
        "Weight Used (lbs):",
        TextBox("weight", 100.0, kind="number"),
        Button("Save Workout", "save_workout"),
        Button("Back to Dashboard", "index")
    ])

@route
def save_workout(state: State, exercise: str, workout_date: str, sets: int, reps: int, weight: float) -> Page:
    """Checks and saves a workout."""
    exercise = exercise.strip()
    if exercise == "":
        state.message = "Please enter an exercise name."
    elif not valid_date(workout_date):
        state.message = "Please enter a valid date."
    elif sets <= 0 or reps <= 0 or weight <= 0:
        state.message = "All workout numbers must be positive."
    elif date.fromisoformat(workout_date) > date.today():
        state.message = "Workout date cannot be in the future."
    else:
        previous_record = get_personal_record(state, exercise)
        new_workout = Workout(workout_date, exercise, sets, reps, weight)
        state.workouts.append(new_workout)
        state.selected_exercise = exercise
        if weight > previous_record:
            state.message = "Workout saved! Congratulations! You achieved a new personal record!"
        else:
            state.message = "Workout successfully saved!"
    return Page(state, [
        Header("Workout Submission"),
        state.message,
        Button("Log Another Workout", "log_workout"),
        Button("View Progress", "progress"),
        Button("Dashboard", "index")
    ])

@route
def progress(state: State) -> Page:
    """Displays workout statistics and a line graph."""
    exercises = get_exercises(state)
    content = [
        Header("Progress Analytics"),
        "Track your strength improvements over time.",
        "Total Weight Lifted: " + format(calculate_total_volume(state), ".1f") + " lbs",
        "Total Workouts: " + str(len(state.workouts)),
        Header("Strength Progress Graph"),
        "Each point represents an individual workout."
    ]
    if len(state.workouts) == 0:
        content.append("No workout data available yet. Log workouts to create your progress graph.")
    else:
        plt.figure(figsize=(10, 5))
        for exercise in exercises:
            exercise_workouts = []
            for workout in state.workouts:
                if workout.exercise == exercise:
                    exercise_workouts.append(workout)
            # Sort workouts by date.
            exercise_workouts.sort(key=lambda workout: workout.date)
            workout_numbers = []
            weights = []
            labels = []
            # Give every workout its own point.
            for index in range(len(exercise_workouts)):
                workout = exercise_workouts[index]
                workout_numbers.append(index + 1)
                weights.append(workout.weight)
                labels.append(workout.date)
            plt.plot(workout_numbers, weights, marker="o", linewidth=2, label=exercise)
            plt.xticks(workout_numbers, labels, rotation=45)
        plt.title("Workout Strength Progress")
        plt.xlabel("Workout Date")
        plt.ylabel("Weight Lifted (lbs)")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        content.append(MatPlotLibPlot())
    content.append(Header("Personal Records"))
    for exercise in exercises:
        record = get_personal_record(state, exercise)
        content.append(exercise + ": " + str(record) + " lbs")
    content.extend([
        Button("Workout History", "history"),
        Button("Log Workout", "log_workout"),
        Button("Dashboard", "index")
    ])
    return Page(state, content)

@route
def history(state: State) -> Page:
    """Displays saved workouts and filters."""
    options = ["All Exercises"]
    options.extend(get_exercises(state))
    selected = state.exercise_filter
    if selected not in options:
        selected = "All Exercises"
    content = [
        Header("Workout History"),
        "View and filter your recorded workouts.",
        "Filter by Exercise:",
        SelectBox("exercise_filter", options, selected),
        "Show All Workouts:",
        CheckBox("show_all", state.show_all),
        Button("Apply Filter", "filter_history"),
        Header("Recorded Workouts")
    ]
    workouts_to_show = filtered_workouts(state)
    if len(workouts_to_show) == 0:
        content.append("No workouts match this filter.")
    else:
        for index in range(len(state.workouts)):
            workout = state.workouts[index]
            if workout in workouts_to_show:
                content.append(
                    workout.date + " | " + workout.exercise + " | "
                    + str(workout.sets) + " sets x "
                    + str(workout.reps) + " reps | "
                    + str(workout.weight) + " lbs"
                )
                content.append(Button("View Details", "workout_details", {"index": index}))
    content.extend([
        Button("Dashboard", "index"),
        Button("Log Workout", "log_workout")
    ])
    return Page(state, content)

@route
def filter_history(state: State, exercise_filter: str, show_all: bool) -> Page:
    """Updates the workout history filter."""
    state.exercise_filter = exercise_filter
    state.show_all = show_all
    state.message = "Workout history filter updated."
    return history(state)

@route
def workout_details(state: State, index: int) -> Page:
    """Displays one workout's details."""
    if index < 0 or index >= len(state.workouts):
        return Page(state, [
            Header("Workout Not Found"),
            "The selected workout does not exist.",
            Button("Back to History", "history")
        ])
    workout = state.workouts[index]
    state.selected_exercise = workout.exercise
    volume = workout.sets * workout.reps * workout.weight
    record = get_personal_record(state, workout.exercise)
    return Page(state, [
        Header("Workout Details"),
        "Exercise: " + workout.exercise,
        "Date: " + workout.date,
        "Sets: " + str(workout.sets),
        "Reps: " + str(workout.reps),
        "Weight: " + str(workout.weight) + " lbs",
        "Total Volume: " + str(volume) + " lbs",
        "Personal Record: " + str(record) + " lbs",
        Button("Back to History", "history"),
        Button("Dashboard", "index")
    ])

@route
def goals(state: State) -> Page:
    """Displays fitness goals and progress."""
    current_record = get_personal_record(state, state.goal_exercise)
    weekly_progress = count_weekly_workouts(state)
    content = [
        Header("Fitness Goals"),
        Header("Strength Goal"),
        "Exercise: " + state.goal_exercise,
        "Target Weight: " + str(state.goal_weight) + " lbs",
        "Current Record: " + str(current_record) + " lbs"
    ]
    if current_record >= state.goal_weight:
        content.append("Congratulations! You reached your goal!")
    else:
        remaining = state.goal_weight - current_record
        content.append("Remaining Weight: " + str(round(remaining, 1)) + " lbs")
    content.extend([
        Header("Weekly Workout Goal"),
        "Target Workouts: " + str(state.weekly_goal),
        "Completed Workouts: " + str(weekly_progress)
    ])
    if weekly_progress >= state.weekly_goal:
        content.append("You completed your weekly workout goal!")
    else:
        content.append("Workouts Remaining: " + str(state.weekly_goal - weekly_progress))
    content.extend([
        Header("Update Your Goals"),
        "Exercise:",
        TextBox("goal_exercise", state.goal_exercise),
        "Target Weight (lbs):",
        TextBox("goal_weight", state.goal_weight, kind="number"),
        "Weekly Workout Target:",
        TextBox("weekly_goal", state.weekly_goal, kind="number"),
        Button("Save Goals", "save_goal"),
        Button("Dashboard", "index")
    ])
    return Page(state, content)

@route
def save_goal(state: State, goal_exercise: str, goal_weight: float, weekly_goal: int) -> Page:
    """Checks and saves fitness goals."""
    goal_exercise = goal_exercise.strip()
    if goal_exercise == "":
        state.message = "Please enter an exercise."
    elif goal_weight <= 0:
        state.message = "Target weight must be positive."
    elif weekly_goal <= 0:
        state.message = "Weekly goal must be positive."
    else:
        state.goal_exercise = goal_exercise
        state.goal_weight = goal_weight
        state.weekly_goal = weekly_goal
        state.message = "Your fitness goals were updated!"
    return Page(state, [
        Header("Goals Updated"),
        state.message,
        Button("View Goals", "goals"),
        Button("Dashboard", "index")
    ])

def run_unit_tests() -> None:
    """Tests the app's main functions and routes."""
    test_state = State(
        workouts=[],
        selected_exercise="",
        exercise_filter="All Exercises",
        message="",
        goal_exercise="Bench Press",
        goal_weight=150.0,
        weekly_goal=3,
        show_all=False
    )
    assert index(test_state) is not None
    assert log_workout(test_state) is not None
    assert progress(test_state) is not None
    assert history(test_state) is not None
    assert goals(test_state) is not None
    today = date.today().isoformat()
    save_workout(test_state, "Bench Press", today, 3, 10, 100.0)
    assert len(test_state.workouts) == 1
    assert test_state.selected_exercise == "Bench Press"
    assert calculate_total_volume(test_state) == 3000.0
    assert get_personal_record(test_state, "Bench Press") == 100.0
    # Test multiple workouts on the same date.
    save_workout(test_state, "Bench Press", today, 3, 10, 105.0)
    assert len(test_state.workouts) == 2
    assert get_personal_record(test_state, "Bench Press") == 105.0
    assert progress(test_state) is not None
    filter_history(test_state, "Bench Press", False)
    assert test_state.exercise_filter == "Bench Press"
    assert test_state.show_all is False
    workout_details(test_state, 0)
    assert test_state.selected_exercise == "Bench Press"
    save_goal(test_state, "Squat", 200.0, 4)
    assert test_state.goal_exercise == "Squat"
    assert test_state.goal_weight == 200.0
    assert test_state.weekly_goal == 4
    previous_count = len(test_state.workouts)
    save_workout(test_state, "", today, 3, 10, 100.0)
    assert len(test_state.workouts) == previous_count
    assert workout_details(test_state, 100) is not None
    print("All FitTrack unit tests passed!")

run_unit_tests()
start_server(State(
    workouts=[],
    selected_exercise="",
    exercise_filter="All Exercises",
    message="Welcome to FitTrack!",
    goal_exercise="Bench Press",
    goal_weight=135.0,
    weekly_goal=3,
    show_all=False
))

