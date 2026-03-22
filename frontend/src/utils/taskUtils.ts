import type { Task, Subtask } from "../context/AppContext";

export function getProgress(tasks: Task[]): number {
  if (!tasks || tasks.length === 0) return 0;
  let total = 0, done = 0;
  tasks.forEach(t => {
    t.subtasks?.forEach(s => { total++; if (s.done) done++; });
  });
  return total === 0 ? 0 : Math.round((done / total) * 100);
}

export function getNextTinyStart(tasks: Task[]): Subtask | null {
  for (const t of tasks) {
    if (t.done) continue;
    for (const s of t.subtasks || []) {
      if (!s.done) return s;
    }
  }
  return null;
}
