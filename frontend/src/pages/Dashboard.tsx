import React, { useState } from "react";
import "./Dashboard.css";

interface Subtask {
  id: string;
  text: string;
  done: boolean;
  estimated_minutes: number;
}

interface Task {
  id: number;
  title: string;
  subtasks: Subtask[];
  currentSubtaskIndex: number;
  quadrant: string;
}

const initialTasks: Task[] = [
  {
    id: 1,
    title: "Read Chapter 1",
 subtasks: [
  { id: "1", text: "Open book", done: false, estimated_minutes: 2 },
  { id: "2", text: "Read first page", done: false, estimated_minutes: 5 },
],
    currentSubtaskIndex: 0,
    quadrant: "Quick Wins",
  },
  {
    id: 2,
    title: "Exercise",
  subtasks: [
  { id: "1", text: "Open book", done: false, estimated_minutes: 2 },
  { id: "2", text: "Read first page", done: false, estimated_minutes: 5 },
],
    currentSubtaskIndex: 0,
    quadrant: "Short Tasks",
  },
  {
    id: 3,
    title: "Organize desk",
    subtasks: [
  { id: "1", text: "Open book", done: false, estimated_minutes: 2 },
  { id: "2", text: "Read first page", done: false, estimated_minutes: 5 },
],
    currentSubtaskIndex: 0,
    quadrant: "Focus Tasks",
  },
  {
    id: 4,
    title: "Plan weekend",
    subtasks: [
  { id: "1", text: "Open book", done: false, estimated_minutes: 2 },
  { id: "2", text: "Read first page", done: false, estimated_minutes: 5 },
],
    currentSubtaskIndex: 0,
    quadrant: "Big Tasks",
  },
];

const quadrants = ["Quick Wins", "Short Tasks", "Focus Tasks", "Big Tasks"];
const getQuadrant = (minutes: number) => {
  if (minutes <= 5) return "Quick Wins";
  if (minutes <= 15) return "Short Tasks";
  if (minutes <= 30) return "Focus Tasks";
  return "Big Tasks";
};


const Dashboard: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>(initialTasks);
  const [newTask, setNewTask] = useState("");

const handleAddTask = async () => {
  if (!newTask.trim()) return;

  try {
    const res = await fetch("/plan", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ task: newTask }),
    });

    const data = await res.json();

    const subtasks: Subtask[] = [
      {
        id: "0",
        text: data.tiny_first_step.title,
        done: false,
        estimated_minutes: data.tiny_first_step.estimated_minutes,
      },
      ...data.steps.map((step: any) => ({
        id: step.id,
        text: step.title,
        done: false,
        estimated_minutes: step.estimated_minutes,
      })),
    ];

    const quadrant = getQuadrant(
      data.tiny_first_step.estimated_minutes
    );

    const newTaskObj: Task = {
      id: Date.now(),
      title: newTask,
      subtasks,
      currentSubtaskIndex: 0,
      quadrant,
    };

    setTasks((prev) => [...prev, newTaskObj]);
    setNewTask("");
  } catch (error) {
    console.error("Error creating plan:", error);
  }
};


  const markSubtaskDone = (taskId: number) => {
    setTasks((prev) =>
      prev
        .map((task) => {
          if (task.id === taskId) {
            const currentIndex = task.currentSubtaskIndex;
            if (currentIndex < task.subtasks.length) {
              const updatedSubtasks = [...task.subtasks];
              updatedSubtasks[currentIndex].done = true;
              return {
                ...task,
                subtasks: updatedSubtasks,
                currentSubtaskIndex: currentIndex + 1,
              };
            }
          }
          return task;
        })
        .filter((task) => task.currentSubtaskIndex < task.subtasks.length)
    );
  };

  return (
    <div className="dashboard-container">
      <aside className="sidebar">
        <h2>Filters</h2>
        <ul>
          <li>All Tasks</li>
          <li>Not Started</li>
          <li>In Progress</li>
        </ul>
      </aside>
      <main className="main-content">
        <h1>What do you need to do?</h1>
        <div className="task-input-container">
          <input
            type="text"
            placeholder="Add a new task..."
            value={newTask}
            onChange={(e) => setNewTask(e.target.value)}
            className="task-input"
          />
          <button onClick={handleAddTask} className="add-task-btn">
            Add
          </button>
        </div>
        <div className="quadrants-container">
          {quadrants.map((quadrant, idx) => (
            <div className={`quadrant quadrant-${idx}`} key={quadrant}>
              <h3 className="quadrant-title">{quadrant}</h3>
              <div className="tasks-list">
                {tasks
                  .filter((task) => task.quadrant === quadrant)
                  .map((task) => (
                    <div key={task.id} className="task-card">
                      <div className="task-title">{task.title}</div>
                      {task.subtasks[task.currentSubtaskIndex] && (
                        <div className="subtask-section">
                          <div className="subtask-text">
                            {task.subtasks[task.currentSubtaskIndex].text}
                          </div>
                          <div className="progress-bar-container">
                            <div
                              className="progress-bar"
                              style={{
                                width: `${
                                  ((task.currentSubtaskIndex + 1) /
                                    task.subtasks.length) *
                                  100
                                }%`,
                              }}
                            ></div>
                          </div>
                          <button
                            className="done-btn"
                            onClick={() => markSubtaskDone(task.id)}
                          >
                            ✓ Done
                          </button>
                        </div>
                      )}
                    </div>
                  ))}
              </div>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
