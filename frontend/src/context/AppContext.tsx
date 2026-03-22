import { createContext, useContext } from "react";
import type { PlanResponse } from "../api/client";

export interface Subtask {
  id: string;
  title: string;
  description?: string;
  done: boolean;
  tinyStart?: boolean;
}

export interface Task {
  id: string;
  title: string;
  done: boolean;
  urgent: boolean;
  timeEstimate: string;
  subtasks: Subtask[];
  _projectColor?: string;
}

export interface Project {
  id: string;
  name: string;
  emoji: string;
  color: string;
  tasks: Task[];
}

export interface DeletedTask {
  task: Task;
  projectId: string;
  projectName: string;
  projectEmoji: string;
  projectColor: string;
}

export interface WhatsAppNudge {
  message: string;
  two_minute_action: string;
}

export interface AppContextType {
  whatsAppNudge: WhatsAppNudge | null;
  clearWhatsAppNudge: () => void;
  projects: Project[];
  activeProject: string | null;
  setActiveProject: (id: string | null) => void;
  activeFilter: string | null;
  setActiveFilter: (filter: string | null) => void;
  toggleSubtask: (taskId: string, subtaskId: string) => void;
  addSubtask: (projectId: string, taskId: string, title: string) => void;
  removeSubtask: (projectId: string, taskId: string, subtaskId: string) => void;
  deleteTask: (projectId: string, taskId: string) => void;
  restoreTask: (taskId: string) => void;
  deletedTasks: DeletedTask[];
  addProject: (project: Project) => void;
  planResponse: PlanResponse | null;
  setPlanResponse: (plan: PlanResponse | null) => void;
  sessionActive: boolean;
  setSessionActive: (active: boolean) => void;
}

export const AppContext = createContext<AppContextType | null>(null);

export function useAppContext(): AppContextType {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error("useAppContext must be used within AppContext.Provider");
  return ctx;
}
